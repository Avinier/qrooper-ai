import zipfile
import time
from pathlib import Path
from ast_chunker import CodeChunker


def process_zip(zip_path: str, output_dir: str = "chunks"):
    start_time = time.time()
    chunker = CodeChunker()

    # Extract ZIP
    extract_dir = Path("temp_extracted")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(extract_dir)

    # Process files
    results = []
    for file_path in extract_dir.rglob("*"):
        if not file_path.is_file():
            continue

        # Skip binaries and large files
        if file_path.suffix.lower() in {'.png', '.jpg', '.exe', '.zip', '.tar', '.gz', '.whl', '.otf', '.woff', '.jpeg', '.mp3', '.mp4'}:
            continue
        if file_path.stat().st_size > 1_000_000:  # 1MB max
            continue

        try:
            content = file_path.read_text(encoding='utf-8', errors='replace')
            chunks, metadata, ids = chunker.chunk_file(
                content,
                str(file_path.relative_to(extract_dir)),
                max_chunk_size=1024,
                chunk_size=40,
                overlap=10
            )
            results.extend(zip(chunks, metadata, ids))
        except Exception as e:
            print(f"⚠️ Error processing {file_path}: {e}")

    # Save results
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    for idx, (chunk, meta, cid) in enumerate(results):
        with (output_path / f"chunk_{idx}.txt").open('w', encoding='utf-8') as f:
            f.write(f"File: {meta['file_path']}\n")
            f.write(f"Lines: {meta['start']}-{meta['end']}\n")
            f.write(f"ID: {cid}\n\n")
            f.write(chunk)

    # Print summary
    print(f"\n✅ Processed {len(results)} chunks in {time.time() - start_time:.1f}s")
    print(f"Saved to: {output_path.resolve()}")

    # Cleanup
    for f in extract_dir.glob("**/*"):
        if f.is_file():
            f.unlink()
    extract_dir.rmdir()

    return results


if __name__ == "__main__":
    process_zip("test2.zip")