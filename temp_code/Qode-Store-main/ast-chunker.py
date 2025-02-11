import os
import zipfile
from tree_sitter import Parser, Language
from dataclasses import dataclass


@dataclass
class Span:
    start: int
    end: int

    def __add__(self, other):
        return Span(min(self.start, other.start), max(self.end, other.end))


class ASTChunker:
    def __init__(self):
        self.ast_references = {}
        self.languages = self.load_parsers()

    def load_parsers(self):
        # Load tree-sitter languages (implementation similar to original code)
        languages = {}
        # ... (language loading logic from original code)
        return languages

    def process_zip(self, zip_path, output_ast="ast.txt"):
        """Process a zip file containing source code"""
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("temp_code")

        with open(output_ast, "w") as ast_file:
            for root, _, files in os.walk("temp_code"):
                for file in files:
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as f:
                        content = f.read()
                    chunks, metadata = self.chunk_file(content, file_path, ast_file)
                    print(f"File: {file_path}")
                    print("Chunks:", chunks)

    def chunk_file(self, content, file_path, ast_file):
        """Chunk a single file and save AST"""
        tree = self.parse_content(content, file_path)
        if not tree:
            return [], []

        # Save AST to file
        self.save_ast(tree, file_path, ast_file)

        # Generate chunks with AST references
        source_bytes = content.encode()
        chunks = self.chunker(tree, source_bytes, file_path)
        return chunks

    def parse_content(self, content, file_path):
        """Parse content and return tree with appropriate language"""
        # ... (language detection logic similar to original code)
        return parser.parse(content.encode())

    def save_ast(self, tree, file_path, ast_file):
        """Recursively save AST nodes to file"""

        def traverse(node):
            ast_file.write(
                f"{file_path}|{node.start_byte}|{node.end_byte}|{node.type}\n"
            )
            for child in node.children:
                traverse(child)

        traverse(tree.root_node)

    def chunker(self, tree, source_bytes, file_path, max_size=512 * 3):
        """Modified chunker that tracks AST nodes"""

        def helper(node):
            chunks = []
            current_span = Span(node.start_byte, node.start_byte)
            current_nodes = []

            for child in node.children:
                child_span = Span(child.start_byte, child.end_byte)
                if child_span.end - child_span.start > max_size:
                    if current_span.end > current_span.start:
                        chunks.append((current_span, current_nodes))
                    chunks.extend(helper(child))
                    current_span = Span(child.end_byte, child.end_byte)
                    current_nodes = []
                else:
                    new_size = (child_span.end - current_span.start)
                    if new_size > max_size:
                        if current_span.end > current_span.start:
                            chunks.append((current_span, current_nodes))
                        current_span = child_span
                        current_nodes = [child]
                    else:
                        current_span += child_span
                        current_nodes.append(child)
            if current_span.end > current_span.start:
                chunks.append((current_span, current_nodes))
            return chunks

        raw_chunks = helper(tree.root_node)
        return self.process_chunks(raw_chunks, file_path)

    def process_chunks(self, raw_chunks, file_path):
        """Convert byte spans to AST references"""
        processed = []
        for span, nodes in raw_chunks:
            # Create chunk references
            refs = [
                f"{file_path}:{n.start_byte}-{n.end_byte}:{n.type}"
                for n in nodes
            ]
            processed.append({
                "chunk_ref": "|".join(refs),
                "metadata": {
                    "file": file_path,
                    "ast_nodes": refs,
                    "start_byte": span.start,
                    "end_byte": span.end
                }
            })
        return processed


# Usage
chunker = ASTChunker()
chunker.process_zip("codebase.zip")