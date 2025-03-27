from pathlib import Path
from tree_sitter_languages import get_parser


class TreeSitterParser:
    def __init__(self):
        # Directory to store AST outputs
        self.output_dir = Path("ast-output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Supported languages mapping (file extension -> tree-sitter language name)
        self.supported_languages = {
            '.py': 'python',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.json': 'json',
            '.dockerfile': 'dockerfile',
            '.sql': 'sql',
            '.html': 'html',
            '.css': 'css',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rs': 'rust',
            '.go': 'go',
            '.java': 'java',
            '.rb': 'ruby',
            '.php': 'php',
            '.cs': 'c_sharp',
            '.swift': 'swift'
        }

        # Initialize parsers
        self.parsers = self._setup_parsers()

    def _setup_parsers(self):
        """Initialize available parsers dynamically"""
        parsers = {}

        for ext, lang_name in self.supported_languages.items():
            try:
                parser = get_parser(lang_name)
                parsers[ext] = parser
                print(f"Successfully loaded {lang_name} parser")
            except Exception as e:
                print(f"Failed to load {lang_name} parser: {str(e)}")

        return parsers

    def _write_tree(self, node, file, level=0):
        """Write tree node to file with proper indentation"""
        indent = "  " * level
        node_text = node.text.decode('utf-8', errors='replace') if node.text else ''

        # Write node information
        file.write(
            f"{indent}{node.type} [{node_text}] "
            f"({node.start_point[0]}:{node.start_point[1]}-"
            f"{node.end_point[0]}:{node.end_point[1]})\n"
        )

        # Recursively write children
        for child in node.children:
            self._write_tree(child, file, level + 1)

    def parse_file(self, file_path, zip_root=None, original_path=None):
        """Parse a single file and save its AST, preserving original directory structure
        
        Args:
            file_path: Path to the file to parse (the actual file on disk)
            zip_root: Root directory where zip was extracted
            original_path: Original path within the zip (to preserve structure)
        """
        file_path = Path(file_path)

        if not file_path.exists():
            print(f"File {file_path} does not exist")
            return False

        ext = file_path.suffix.lower()  # Handle case-insensitive extensions
        if ext not in self.parsers:
            print(f"Unsupported file extension: {ext}")
            return False

        try:
            with open(file_path, 'rb') as f:
                content = f.read()

            # Parse content with appropriate parser
            parser = self.parsers[ext]
            tree = parser.parse(content)

            # Determine output path based on original structure
            if zip_root and original_path:
                # Use the original path from within the zip
                output_file = self.output_dir / original_path
                # Add the _ast.txt suffix
                output_file = output_file.with_name(f"{output_file.stem}_ast.txt")
            else:
                # Fallback to the original behavior
                output_file = self.output_dir / f"{file_path.stem}_ast.txt"

            # Create parent directories
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Write AST to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"AST for {original_path or file_path}\n{'=' * 50}\n")
                self._write_tree(tree.root_node, f)

            print(f"Saved AST to {output_file}")
            return True

        except Exception as e:
            print(f"Error parsing {file_path}: {str(e)}")
            return False


    def parse_directory(self, directory_path):
        """Parse all supported files in a directory, preserving directory structure"""
        directory_path = Path(directory_path)

        if not directory_path.exists():
            print(f"Directory {directory_path} does not exist")
            return

        for file_path in directory_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.parsers:
                # Calculate the original path relative to the directory
                original_path = file_path.relative_to(directory_path)
                
                # Parse the file with structure preservation
                self.parse_file(
                    file_path=file_path,
                    zip_root=directory_path,
                    original_path=original_path
                )


# def main():
#     if len(sys.argv) < 2:
#         print("Usage: python ast_generator.py <path_to_zip>")
#         return
#
#     parser = TreeSitterParser()
#     zip_path = Path(sys.argv[1])
#
#     if zip_path.suffix.lower() != '.zip':
#         print("Error: Input must be a ZIP file")
#         return
#
#     parser.process_zip(zip_path)
#
#
# if __name__ == "__main__":
#     main()