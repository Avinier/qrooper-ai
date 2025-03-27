import asyncio
import os
import shutil
from pathlib import Path
from llm_calls.qrooper_engine import Qrooper
from llm_calls.generate_ast import extract_zip
from ast_parser_2 import TreeSitterParser
import aiofiles


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

async def main(zip_path, query):
    # Generate AST files if needed
    ast_generator = ASTGenerator()
    await ast_generator.generate_from_zip(zip_path)

    # Process query with Qrooper
    qrooper = Qrooper(
        api_key="fw_3ZYVTdrvNUzJcNyGe4P4fjLY",
        ast_output_dir="ast-output"
    )
    result = await qrooper.parse_query(zip_path, query)
    
    print("\n" + "="*50)
    print(f"Query: {query}")
    print("="*50)
    print(result)
    print("="*50 + "\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python main.py <zipfile> <query>")
        sys.exit(1)

    zip_path = sys.argv[1]
    query = sys.argv[2]

    asyncio.run(main(zip_path, query))