#TODO: failed to parse json response error
import asyncio
import json
import os
import shutil
from file_parsing import extract_zip, batch_files
import requests

# Globals for configuration
headers = None
model_name = "accounts/fireworks/models/deepseek-v3"
semaphore = None
api_key = "fw_3ZYVTdrvNUzJcNyGe4P4fjLY"


def setup_api():
    """Initialize API configuration"""
    global headers, model_name
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

async def call_llm_api(prompt):
    """Async wrapper for LLM API call using thread pool"""
    payload = {
        "model": model_name,
        "max_tokens": 4096,
        "temperature": 0.3,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: requests.post(
                "https://api.fireworks.ai/inference/v1/chat/completions",
                headers=headers,
                json=payload
            )
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"filename_evaluator API Error: {str(e)}")
        return None

async def process_batch(batch_files, query):
    """Process a single batch of filenames"""
    file_list = "\n".join([f"- {f}" for f in batch_files])

    FILENAME_EVAL_PROMPT = f"""Analyze these files in relation to the query: "{query}".
    Respond ONLY with a JSON array of relevant file paths:
    Files:
    {file_list}"""

    response = await call_llm_api(FILENAME_EVAL_PROMPT)
    if not response:
        return []
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        print(f"Failed to parse response: {response}")
        return []

async def process_batch_with_semaphore(batch, query):
    """Wrapper with semaphore for concurrency control"""
    async with semaphore:
        return await process_batch(batch, query)

async def filter_zip_contents(zip_path, query, batch_size=50, max_concurrent=5):
    """Main processing pipeline"""
    global semaphore
    
    # Setup API configuration
    setup_api()
    
    # Initialize semaphore for concurrency control
    semaphore = asyncio.Semaphore(max_concurrent)
    
    # Extract zip file
    extract_dir = await extract_zip(zip_path)
    all_files = []
    
    try:
        # Collect relative file paths
        for root, _, files in os.walk(extract_dir):
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), extract_dir)
                all_files.append(rel_path)
        
        # Process in batches
        batches = list(batch_files(all_files, batch_size))
        tasks = []
        
        for batch in batches:
            task = asyncio.create_task(
                process_batch_with_semaphore(batch, query)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Combine and deduplicate results
        return list({f for batch_result in results for f in batch_result})
        
    finally:
        shutil.rmtree(extract_dir)

async def filename_evaluate(zip_path, query, batch_size=50, max_concurrent=5):
    """Filter the zip contents and return the results as a formatted string"""
    # Get the list of relevant files
    relevant_files = await filter_zip_contents(
        zip_path, query, batch_size, max_concurrent
    )
    
    # Format the results as a string
    if not relevant_files:
        return "No relevant files found."
    
    result_string = f"Relevant files ({len(relevant_files)}):\n"
    for file in relevant_files:
        result_string += f"- {file}\n"
    
    return result_string

async def main():
    formatted_results = await filename_evaluate(
        "test2.zip",
        "Find files related to user authentication",
        batch_size=40,
        max_concurrent=3
    )
    print(formatted_results)

if __name__ == "__main__":
    asyncio.run(main())