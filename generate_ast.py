import hashlib
import os
from pathlib import Path
import shutil
import asyncio
import aiofiles
from file_parsing import process_zip, extract_zip, try_cleanup
from ast_parser_2 import TreeSitterParser

parser = TreeSitterParser()

def file_filter(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    return ext in parser.supported_languages

def ast_parse_file(zip_path: str):
    """Process ZIP file and parse contents with TreeSitter"""
    try:
        # Extract ZIP to temp directory
        extracted_dir = asyncio.run(extract_zip(zip_path))
        
        # Process all files in extracted directory
        parser = TreeSitterParser()
        parser.parse_directory(extracted_dir)
        
        return {
            "status": "success",
            "ast_dir": parser.output_dir,
            "processed_files": len(list(Path(extracted_dir).rglob('*')))
        }
    except Exception as e:
        print(f"Error processing {zip_path}: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        # Cleanup extracted files
        asyncio.run(try_cleanup(extracted_dir))

async def main(zip_path: str):
    """Main entry point for AST generation"""
    return await asyncio.get_event_loop().run_in_executor(
        None, ast_parse_file, zip_path
    )


if __name__ == "__main__":
    import asyncio
    results = asyncio.run(main("test2.zip"))
    # Process results as needed