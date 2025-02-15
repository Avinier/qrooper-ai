import os
import re
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, List, Dict, Optional

from loguru import logger
from tree_sitter import Parser
from tree_sitter_languages import get_parser, get_language


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
            return Span(min(self.start, other.start), max(self.end, other.end))
        raise NotImplementedError()

    def __len__(self):
        return self.end - self.start


extension_to_language = {
    "js": "javascript", "jsx": "javascript", "ts": "typescript",
    "tsx": "tsx", "mjs": "javascript", "py": "python", "rs": "rust",
    "go": "go", "java": "java", "cpp": "cpp", "cc": "cpp", "cxx": "cpp",
    "c": "cpp", "h": "cpp", "hpp": "cpp", "cs": "c-sharp", "rb": "ruby",
    "md": "markdown", "rst": "markdown", "txt": "markdown", "html": "html",
    "vue": "vue", "php": "php"
}


class CodeChunker:
    def __init__(self):
        self.parsers = {}

    def get_parser(self, language: str) -> Optional[Parser]:
        if language not in self.parsers:
            try:
                parser = get_parser(language)
                self.parsers[language] = parser
            except Exception as e:
                logger.warning(f"Parser for {language} not available: {str(e)}")
                return None
        return self.parsers[language]

    def chunk_file(
            self,
            file_content: str,
            file_path: str,
            max_chunk_size: int = 512 * 3,
            chunk_size: int = 30,
            overlap: int = 15,
            score: float = 1.0,
            additional_metadata: dict = None
    ) -> Tuple[List[str], List[dict], List[str]]:
        additional_metadata = additional_metadata or {}
        ext = os.path.splitext(file_path)[1].lstrip(".")
        language = extension_to_language.get(ext)
        parser = self.get_parser(language) if language else None
        chunks, metadatas, ids = [], [], []

        if parser:
            try:
                tree = parser.parse(bytes(file_content, "utf-8"))
                spans = self._chunk_tree(tree, bytes(file_content, "utf-8"), max_chunk_size)
                chunks = [span.extract(file_content) for span in spans]
                metadatas = [{
                    "file_path": file_path,
                    "start": span.start,
                    "end": span.end,
                    "score": score,
                    **additional_metadata
                } for span in spans]
                ids = [f"{file_path}:{span.start}:{span.end}" for span in spans]
            except Exception as e:
                logger.error(f"AST chunking failed for {file_path}: {str(e)}")
                traceback.print_exc()

        if not chunks:
            chunks, metadatas, ids = self._naive_chunk(file_content, file_path, chunk_size, overlap, score,
                                                       additional_metadata)

        return chunks, metadatas, ids

    def _chunk_tree(self, tree, source_bytes, max_size=512 * 3, coalesce=50) -> List[Span]:
        def helper(node, start=0):
            chunks = []
            current = Span(start, start)
            for child in node.children:
                child_span = Span(child.start_byte, child.end_byte)
                if len(child_span) > max_size:
                    if len(current) > 0:
                        chunks.append(current)
                    chunks.extend(helper(child, child.start_byte))
                    current = Span(child.end_byte, child.end_byte)
                elif len(current) + len(child_span) > max_size:
                    chunks.append(current)
                    current = child_span
                else:
                    current += child_span
            if len(current) > 0:
                chunks.append(current)
            return chunks

        chunks = helper(tree.root_node)
        merged = []
        for chunk in chunks:
            if merged and merged[-1].end == chunk.start:
                merged[-1] = Span(merged[-1].start, chunk.end)
            else:
                merged.append(chunk)

        final = []
        current = Span(0, 0)
        for chunk in merged:
            current += chunk
            content = source_bytes[current.start:current.end].decode("utf-8")
            if len(re.sub(r'\s', '', content)) > coalesce and "\n" in content:
                final.append(current)
                current = Span(chunk.end, chunk.end)
        if len(current) > 0:
            final.append(current)

        source_str = source_bytes.decode("utf-8")
        return [
            Span(self._get_line_num(c.start, source_str),
                 self._get_line_num(c.end, source_str))
            for c in final if len(c) > 0
        ]

    def _get_line_num(self, index: int, source: str) -> int:
        total = 0
        for line_num, line in enumerate(source.splitlines(keepends=True)):
            if total <= index < total + len(line):
                return line_num
            total += len(line)
        return len(source.splitlines())

    def _naive_chunk(self, content, path, size, overlap, score, metadata):
        lines = content.split("\n")
        chunks = []
        start = 0
        while start < len(lines):
            end = min(start + size, len(lines))
            chunks.append("\n".join(lines[start:end]))
            start += size - overlap

        metadatas = [{
            "file_path": path,
            "start": i * (size - overlap),
            "end": min((i + 1) * size, len(lines)),
            "score": score,
            **metadata
        } for i in range(len(chunks))]

        ids = [f"{path}:{meta['start']}:{meta['end']}" for meta in metadatas]
        return chunks, metadatas, ids