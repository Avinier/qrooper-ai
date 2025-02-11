# chunker.py
import os
import re
import subprocess
import traceback
from dataclasses import dataclass
from typing import Tuple, List, Dict

# import modal
from loguru import logger
from tree_sitter import Language, Parser
from modal import method


@dataclass
class Span:
    start: int
    end: int

    def extract(self, s: str) -> str:
        return "\n".join(s.splitlines()[self.start:self.end])

    def __add__(self, other):
        if isinstance(other, int):
            return Span(self.start + other, self.end + other)
        elif isinstance(other, Span):
            return Span(self.start, other.end)
        else:
            raise NotImplementedError()

    def __len__(self):
        return self.end - self.start


def get_line_number(index: int, source_code: str) -> int:
    lines = source_code.splitlines(keepends=True)
    total_chars = 0
    line_number = 0
    while total_chars <= index:
        if line_number == len(lines):
            return line_number
        total_chars += len(lines[line_number])
        line_number += 1
    return line_number - 1


def count_length_without_whitespace(s: str) -> int:
    return len(re.sub(r'\s', '', s))


def chunker(tree, source_code_bytes, max_chunk_size=512 * 3, coalesce=50) -> List[Span]:
    def chunker_helper(node, source_code_bytes, start_position=0):
        chunks = []
        current_chunk = Span(start_position, start_position)
        for child in node.children:
            child_span = Span(child.start_byte, child.end_byte)
            if len(child_span) > max_chunk_size:
                chunks.append(current_chunk)
                chunks.extend(chunker_helper(child, source_code_bytes, child.start_byte))
                current_chunk = Span(child.end_byte, child.end_byte)
            elif len(current_chunk) + len(child_span) > max_chunk_size:
                chunks.append(current_chunk)
                current_chunk = child_span
            else:
                current_chunk += child_span
        if len(current_chunk) > 0:
            chunks.append(current_chunk)
        return chunks

    chunks = chunker_helper(tree.root_node, source_code_bytes)

    # Post-processing
    for prev, curr in zip(chunks[:-1], chunks[1:]):
        prev.end = curr.start

    new_chunks = []
    current_chunk = Span(0, 0)
    for chunk in chunks:
        current_chunk += chunk
        if count_length_without_whitespace(
                source_code_bytes[current_chunk.start:current_chunk.end].decode("utf-8")) > coalesce \
                and "\n" in source_code_bytes[current_chunk.start:current_chunk.end].decode("utf-8"):
            new_chunks.append(current_chunk)
            current_chunk = Span(chunk.end, chunk.end)
    if len(current_chunk) > 0:
        new_chunks.append(current_chunk)

    line_chunks = [Span(
        get_line_number(chunk.start, source_code_bytes.decode("utf-8")),
        get_line_number(chunk.end, source_code_bytes.decode("utf-8"))
    ) for chunk in new_chunks]
    return [chunk for chunk in line_chunks if len(chunk) > 0]


extension_to_language = {
    "js": "tsx", "jsx": "tsx", "ts": "tsx", "tsx": "tsx", "mjs": "tsx",
    "py": "python", "rs": "rust", "go": "go", "java": "java",
    "cpp": "cpp", "cc": "cpp", "cxx": "cpp", "c": "cpp", "h": "cpp",
    "hpp": "cpp", "cs": "c-sharp", "rb": "ruby", "md": "markdown",
    "rst": "markdown", "txt": "markdown", "erb": "embedded-template",
    "ejs": "embedded-template", "html": "embedded-template",
    "vue": "vue", "php": "php",
}

# CHUNKING_CACHE_DIR = "/cache"
# chunking_volume = modal.NetworkFileSystem.persisted("chunking-cache")
# chunking_image = modal.Image.debian_slim().pip_install("tree_sitter", "loguru", "regex")
#
# stub = modal.Stub(name="code-chunker")
#
#
# @stub.cls(
#     image=chunking_image,
#     network_file_systems={CHUNKING_CACHE_DIR: chunking_volume},
# )
class CodeChunker:
    def __enter__(self):
        self.languages = {}
        langs = ["python", "java", "cpp", "go", "rust", "ruby", "php"]
        for lang in langs:
            subprocess.run(
                f"git clone https://github.com/tree-sitter/tree-sitter-{lang} {CHUNKING_CACHE_DIR}/tree-sitter-{lang}",
                shell=True)
            Language.build_library(f'{CHUNKING_CACHE_DIR}/build/{lang}.so',
                                   [f"{CHUNKING_CACHE_DIR}/tree-sitter-{lang}"])
            self.languages[lang] = Language(f'{CHUNKING_CACHE_DIR}/build/{lang}.so', lang)

        # Special cases
        for lang, repo in [("c-sharp", "c-sharp"), ("embedded-template", "embedded-template")]:
            subprocess.run(
                f"git clone https://github.com/tree-sitter/tree-sitter-{repo} {CHUNKING_CACHE_DIR}/tree-sitter-{repo}",
                shell=True)
            Language.build_library(f'{CHUNKING_CACHE_DIR}/build/{lang}.so',
                                   [f"{CHUNKING_CACHE_DIR}/tree-sitter-{repo}"])
            self.languages[lang] = Language(f'{CHUNKING_CACHE_DIR}/build/{lang}.so', lang.replace("-", "_"))

        # Markdown and Vue
        subprocess.run(
            f"git clone https://github.com/MDeiml/tree-sitter-markdown {CHUNKING_CACHE_DIR}/tree-sitter-markdown",
            shell=True)
        Language.build_library(f'{CHUNKING_CACHE_DIR}/build/markdown.so',
                               [f"{CHUNKING_CACHE_DIR}/tree-sitter-markdown/tree-sitter-markdown"])
        self.languages["markdown"] = Language(f'{CHUNKING_CACHE_DIR}/build/markdown.so', "markdown")

        subprocess.run(f"git clone https://github.com/ikatyang/tree-sitter-vue {CHUNKING_CACHE_DIR}/tree-sitter-vue",
                       shell=True)
        Language.build_library(f'{CHUNKING_CACHE_DIR}/build/vue.so', [f"{CHUNKING_CACHE_DIR}/tree-sitter-vue"])
        self.languages["vue"] = Language(f'{CHUNKING_CACHE_DIR}/build/vue.so', "vue")

        # TypeScript
        subprocess.run(
            f"git clone https://github.com/tree-sitter/tree-sitter-typescript {CHUNKING_CACHE_DIR}/tree-sitter-typescript",
            shell=True)
        Language.build_library(f'{CHUNKING_CACHE_DIR}/build/tsx.so',
                               [f"{CHUNKING_CACHE_DIR}/tree-sitter-typescript/tsx"])
        self.languages["tsx"] = Language(f'{CHUNKING_CACHE_DIR}/build/tsx.so', "tsx")

    # @method()
    def chunk_file(
            self,
            file_content: str,
            file_path: str,
            max_chunk_size: int = 512 * 3,
            chunk_size: int = 30,
            overlap: int = 15,
            score: float = 1.0,
            additional_metadata: dict = {}
    ) -> Tuple[List[str], List[dict], List[str]]:
        """Main chunking interface"""
        file_language = None
        tree = None
        _, ext = os.path.splitext(file_path)
        ext = ext.lstrip(".")
        parser = Parser()

        if ext in extension_to_language:
            lang_name = extension_to_language[ext]
            if lang_name in self.languages:
                parser.set_language(self.languages[lang_name])
                tree = parser.parse(file_content.encode("utf-8"))
                if tree.root_node.children and tree.root_node.children[0].type != "ERROR":
                    file_language = lang_name

        if file_language:
            try:
                spans = chunker(tree, file_content.encode("utf-8"), max_chunk_size)
                chunks = [Span(span.start, span.end).extract(file_content) for span in spans]
                metadatas = [{
                    "file_path": file_path,
                    "start": span.start,
                    "end": span.end,
                    "score": score,
                    **additional_metadata
                } for span in spans]
                ids = [f"{file_path}:{span.start}:{span.end}" for span in spans]
                return chunks, metadatas, ids
            except Exception as e:
                logger.error(f"Error chunking {file_path}: {str(e)}")
                traceback.print_exc()

        # Fallback for unsupported languages
        lines = file_content.split("\n")
        chunks = []
        start_line = 0
        while start_line < len(lines):
            end_line = min(start_line + chunk_size, len(lines))
            chunk = "\n".join(lines[start_line:end_line])
            chunks.append(chunk)
            start_line += chunk_size - overlap

        metadatas = [{
            "file_path": file_path,
            "start": i * (chunk_size - overlap),
            "end": min((i + 1) * chunk_size, len(lines)),
            "score": score,
            **additional_metadata
        } for i in range(len(chunks))]

        ids = [f"{file_path}:{meta['start']}:{meta['end']}" for meta in metadatas]
        return chunks, metadatas, ids