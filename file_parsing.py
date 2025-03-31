import asyncio
import aiofiles
import os
import zipfile
import shutil
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import time

async def read_file(file_path, semaphore):
    """Read file with concurrency control"""
    async with semaphore:
        try:
            async with aiofiles.open(file_path, "rb") as f:
                content = await f.read()
                return (file_path, content)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return (file_path, None)

async def async_file_reader(file_paths, max_concurrent_files=100):
    """Read files with async I/O in batches"""
    semaphore = asyncio.Semaphore(max_concurrent_files)
    return await asyncio.gather(
        *(read_file(path, semaphore) for path in file_paths)
    )

def batch_files(file_paths, batch_size=500):
    """Split files into processing batches"""
    for i in range(0, len(file_paths), batch_size):
        yield file_paths[i:i + batch_size]

async def extract_zip(zip_file_path: str) -> str:
    """Extract zip file to temp_dir"""
    output_dir = "temp_dir"
    os.makedirs(output_dir, exist_ok=True)
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    return output_dir

async def parallel_file_processing(file_paths, processing_func):
    """Generic parallel file processing"""
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as pool:
        tasks = [
            loop.run_in_executor(pool, processing_func, path)
            for path in file_paths
        ]
        results = await asyncio.gather(*tasks)
        return [
            (file_paths[i], results[i])
            for i in range(len(results))
            if results[i] is not None
        ]

async def concurrent_file_processing(file_paths : list[str], max_concurrent=50)-> list[tuple[str, bytes]]:
    """Process files concurrently using async I/O with semaphore"""
    semaphore = asyncio.Semaphore(max_concurrent)
    results = await asyncio.gather(
        *(read_file(path, semaphore) for path in file_paths)
    )
    
    # Filter out failed reads
    return [result for result in results if result[1] is not None]

async def process_zip(zip_file_path: str, processing_func, file_filter=None) -> dict:
    """Generic zip file processing"""
    extract_dir = await extract_zip(zip_file_path)
    all_results = {}
    try:
        file_paths = []
        for root, _, files in os.walk(extract_dir):
            for f in files:
                full_path = os.path.join(root, f)
                file_paths.append(full_path)

        if file_filter:
            file_paths = [p for p in file_paths if file_filter(p)]

        processed = await parallel_file_processing(file_paths, processing_func)
        
        for path, result in processed:
            rel_path = os.path.relpath(path, extract_dir)
            all_results[rel_path] = result
            
        return all_results
    finally:
        # Add a delay to allow files to be released
        await asyncio.sleep(1)
        try_cleanup(extract_dir, max_retries=3)


async def try_cleanup(path, max_retries=3, retry_delay=1):
    """Try to clean up a directory with retries on failure"""
    for attempt in range(max_retries):
        try:
            if os.path.exists(path):
                # On Windows, sometimes we need to handle read-only attributes
                for root, dirs, files in os.walk(path, topdown=False):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            os.chmod(file_path, 0o777)  # Make file writable
                        except:
                            pass
                shutil.rmtree(path)
                return  # Success, exit the function
        except Exception as e:
            print(f"Cleanup attempt {attempt+1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:  # Wait before retrying
                await asyncio.sleep(retry_delay)  # Use asyncio.sleep instead of time.sleep
            else:
                print(f"Failed to clean up {path} after {max_retries} attempts")