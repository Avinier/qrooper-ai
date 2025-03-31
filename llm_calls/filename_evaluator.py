# TODO: failed to parse json response error
import asyncio
import json
import os
import shutil
from file_parsing import extract_zip, batch_files
import requests

# Globals for configuration
model_name = "accounts/fireworks/models/deepseek-v3"
semaphore = None
api_key = "fw_3ZYVTdrvNUzJcNyGe4P4fjLY"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
}

FILENAME_EVAL_PROMPT = """You are a code file evaluator. Your task is to analyze file paths and determine which ones are relevant to a specific query.

        For the query: "{query}"

        Analyze these files and return ONLY a JSON array of file paths that are relevant. Include a file if you think it might contain relevant code. Your response must be a markdown code block with 'json' language specifier containing an array of strings.
        IMPORTANT: Use forward slashes (/) instead of backslashes (\\) in all file paths.

        Files to analyze:
        {file_list}

        Remember: Respond ONLY with a code block like this:
        ```json
        ["file1/path.py", "file2/path.py"]
    ```
    """

async def call_llm_api(prompt):
    """Async wrapper for LLM API call using thread pool"""
    payload = {
        "model": model_name,
        "max_tokens": 4096,
        "temperature": 0.3,
        "messages": [{"role": "user", "content": prompt}],
    }
    try:
        # print(f"[filename_eval.call_llm_api] Sending request to LLM API...")
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.post(
                "https://api.fireworks.ai/inference/v1/chat/completions",
                headers=headers,
                json=payload,
            ),
        )

        if response.status_code != 200:
            print(f"[filename_eval.call_llm_api] Error response: {response.text}")
            return None

        response_json = response.json()
        raw_content = response_json["choices"][0]["message"]["content"]
        # print(f"[filename_eval.call_llm_api] Raw content: {raw_content}")
        return raw_content
    except Exception as e:
        print(f"[filename_eval.call_llm_api]LLM API Error: {str(e)}")
        return None


async def process_filename_batch(batch_files, query):
    """Process a single batch of filenames"""
    
    # Normalize paths to use forward slashes for consistency
    normalized_files = [f.replace('\\', '/') for f in batch_files]
    file_list = "\n".join([f"- {f}" for f in normalized_files])

    response = await call_llm_api(FILENAME_EVAL_PROMPT.format(query=query, file_list=file_list))

    if not response:
        print("[filename_eval.process_filename_batch] No response from LLM")
        return []
    try:
        # Extract JSON content from markdown code block if present
        if "```json" in response:
            start_idx = response.find("```json") + 7 
            end_idx = response.find("```", start_idx)
            if end_idx != -1:
                json_str = response[start_idx:end_idx].strip()
                json_str = json_str.replace('\\', '/')
                result = json.loads(json_str)
                if not isinstance(result, list):
                    print(
                        f"[filename_eval.process_filename_batch] Error: Expected list but got {type(result)}"
                    )
                    return []
                return [os.path.normpath(path) for path in result]
        # Fallback to direct JSON parsing
        response = response.replace('\\', '/')  # Normalize any remaining backslashes
        result = json.loads(response)
        if not isinstance(result, list):
            print(
                f"[filename_eval.process_filename_batch] Error: Expected list but got {type(result)}"
            )
            return []
        # Convert back to system-appropriate path separators if needed
        return [os.path.normpath(path) for path in result]
    except json.JSONDecodeError as e:
        print(f"[filename_eval.process_filename_batch] JSON parse error: {str(e)}")
        print(f"[filename_eval.process_filename_batch] Failed response: {response}")
        return []


async def process_filename_batch_with_semaphore(batch, query):
    """Wrapper with semaphore for concurrency control"""
    async with semaphore:
        return await process_filename_batch(batch, query)


async def filter_zip_contents(zip_path, query, batch_size=50, max_concurrent=5):
    """Main processing pipeline"""

    print("filter_zip_contents started...")
    global semaphore

    if not os.path.exists(zip_path):
        print(f"[filename_eval.filter_zip_contents] Zip file not found: {zip_path}")
        return []

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

        if not all_files:
            print("[filename_eval.filter_zip_contents] No files found in zip")
            return []

        # Process in batches
        batches = list(batch_files(all_files, batch_size))
        tasks = []

        for batch in batches:
            task = asyncio.create_task(process_filename_batch_with_semaphore(batch, query))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        # print(f"[DEBUG] LLM Results: {results}")

        # Combine and deduplicate results
        final_results = list({f for batch_result in results for f in batch_result})
        print(f"[filename_eval.filter_zip_contents] Final results: {final_results}")
        return final_results

    finally:
        shutil.rmtree(extract_dir)


# test function
async def filename_evaluate(zip_path, query, batch_size=50, max_concurrent=5):
    """Filter the zip contents and return the list of relevant filepaths"""
    # Get the list of relevant files
    relevant_files = await filter_zip_contents(
        zip_path, query, batch_size, max_concurrent
    )

    return relevant_files if relevant_files else []


async def main():
    results = await filename_evaluate(
        "E:/Projects.py/Qode-Store-V1/qodestore-rag/test2.zip",
        "Find files related to chart visualizations",
    )
    print(results)


if __name__ == "__main__":
    asyncio.run(main())
