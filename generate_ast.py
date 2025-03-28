import hashlib
import os
from pathlib import Path
import shutil
import asyncio
import aiofiles
from file_parsing import process_zip
from ast_parser_2 import TreeSitterParser

parser = TreeSitterParser()

def file_filter(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    return ext in parser.supported_languages

def ast_parse_file(file_path, original_path, base_dir):
    """File processing specific to AST parsing with structure preservation
    
    Args:
        file_path: Actual path to the file on disk
        original_path: Original path within the zip/structure (for preservation)
        base_dir: Base directory for relative path calculation
    """
    try:
        # If original_path is not provided but base_dir is, calculate the relative path
        if not original_path and base_dir:
            try:
                original_path = Path(file_path).relative_to(Path(base_dir))
            except ValueError:
                # If file_path is not relative to base_dir, use the filename only
                original_path = Path(file_path).name
        
        # Call the updated parse_file method with structure preservation
        success = parser.parse_file(
            file_path=file_path,
            zip_root=base_dir,
            original_path=original_path
        )
        
        if success:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            return {
                "hash": hashlib.sha256(content).hexdigest()[:8],
                "ast": parser.get_ast(),  # Assuming parser stores last parsed AST
                "path": str(original_path) if original_path else str(file_path)
            }
        return None
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None

async def main(zip_path):
    results = await process_zip(
        zip_path,
        processing_func=ast_parse_file,
        file_filter=file_filter
    )
    return results

class ASTGenerator:
    def __init__(self, output_dir="ast-output"):
        self.output_dir = Path(output_dir)
        self.parser = TreeSitterParser()

    async def generate_from_zip(self, zip_path):
        """Generate AST files from zip archive"""
        if self.output_dir.exists():
            print(f"Using existing AST directory: {self.output_dir}")
            return

        extract_dir = await extract_zip(zip_path)
        try:
            await self._process_extracted_files(extract_dir)
        finally:
            shutil.rmtree(extract_dir)
        print(f"Generated AST files in {self.output_dir}")

    async def _process_extracted_files(self, extract_dir):
        """Process all files in extracted directory"""
        file_paths = []
        for root, _, files in os.walk(extract_dir):
            for f in files:
                file_paths.append(Path(root) / f)

        tasks = [self._process_file(path, extract_dir) for path in file_paths]
        await asyncio.gather(*tasks)

    async def _process_file(self, file_path, extract_dir):
        """Process individual file and save AST"""
        if file_path.suffix.lower() not in self.parser.supported_languages:
            return

        rel_path = file_path.relative_to(extract_dir)
        ast_path = self.output_dir / f"{rel_path}_ast.txt"

        if not ast_path.parent.exists():
            ast_path.parent.mkdir(parents=True)

        success = await asyncio.get_event_loop().run_in_executor(
            None,
            self.parser.parse_file,
            str(file_path)
        )

        if success:
            ast_content = self.parser.get_ast()
            async with aiofiles.open(ast_path, 'w', encoding='utf-8') as f:
                await f.write(ast_content)

if __name__ == "__main__":
    import asyncio
    results = asyncio.run(main("test2.zip"))
    # Process results as needed