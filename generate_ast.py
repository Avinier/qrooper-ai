import hashlib
import os
from file_processor import process_zip
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

if __name__ == "__main__":
    import asyncio
    results = asyncio.run(main("test2.zip"))
    # Process results as needed