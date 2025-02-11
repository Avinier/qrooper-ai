import zipfile
from pathlib import Path
from ast_chunker import CodeChunker


def process_zip(zip_path: str):
    # Initialize chunker
    chunker = CodeChunker()

    # Extract zip
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall("temp_code")

    # Process all files
    results = []
    for path in Path("temp_code").rglob("*"):
        if path.is_file():
            try:
                content = path.read_text()
                chunks, metadata = chunker.chunk_file(content, str(path))
                results.extend(zip(chunks, metadata))
            except Exception as e:
                print(f"Error processing {path}: {e}")

    # Print results
    for chunk, meta in results[:5]:  # Show first 5 chunks
        print(f"File: {meta['file']}")
        print(f"Lines: {meta['start']}-{meta['end']}")
        print(chunk)
        print("\n" + "=" * 80 + "\n")

    return results


if __name__ == "__main__":
    process_zip("test1.zip")