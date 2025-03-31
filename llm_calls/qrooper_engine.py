import asyncio
import requests
from pathlib import Path
from llm_calls.filename_evaluator import filename_evaluate
import os

model_name = "accounts/fireworks/models/deepseek-r1"
api_key = "fw_3ZYVTdrvNUzJcNyGe4P4fjLY"

PARSE_ENGINE_PROMPT="""
You are a code analysis assistant. Analyze the following code to answer the user's query.

Code Context:
{code_context}

AST Context:
{ast_context}

Based on user's query answer
"""

EXTRA_ANALYSIS_DECIDER_PROMPT="""
You are a code analysis evaluator. Your job is to determine if the initial code analysis is sufficient or if more detailed analysis with AST content is needed.

Review the analysis provided and determine if it appears complete and accurate. If the answer seems comprehensive and directly addresses the user's query, respond with "OK". If the answer seems incomplete, vague, or could benefit from deeper code structure analysis, respond with "NOT OK".

Only respond with either "OK" or "NOT OK" - no other text.
"""

class Qrooper:
    def __init__(self, ast_output_dir="ast-output"):
        self.ast_output_dir = Path(ast_output_dir)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    async def _parse_query(self, zip_path, query):
        """Main query processing pipeline"""

        # Step 1: Get relevant filenames using LLM
        relevant_files = await filename_evaluate(zip_path, query)
        
        if not relevant_files or not isinstance(relevant_files, list):
            return "qrooper error: No relevant files found for this query"

        # Step 2: get raw code from the relevant files
        code_context = await self.retrieve_raw_code(relevant_files)
    
        # Step 2: Get initial analysis without AST contents
        initial_result = await self._main_llm_call(None, query, code_context)
        
        # Step 3: Decide if more analysis is needed
        decision = await self.extra_analysis_decider(initial_result)
        
        print("DECISION TO CONTINUE: ", decision)
        if decision == "NOT OK":
            # Step 4: Retrieve AST contents if needed
            ast_contents = await self.retrieve_ast_contents(relevant_files)
            
            # Step 5: Analyze with LLM for final answer with AST contents
            return await self._main_llm_call(ast_contents, query, code_context)
        else:
            return initial_result

    async def _main_llm_call(self, ast_contents, query, code_context):
        """Final LLM analysis with relevant AST contents""" 
        
        if ast_contents is None:
            # Remove the context section if no valid ASTs
            prompt = PARSE_ENGINE_PROMPT.replace("\nAST Context:\n{ast_context}\n", "")
            prompt = prompt.format(code_context=code_context)
        else:
            ast_context = "\n\n".join(
                f"File: {path}\nAST:\n{content}"
                for path, content in ast_contents.items()
                if content is not None
            )
            prompt = PARSE_ENGINE_PROMPT.format(ast_context=ast_context)
        
        payload = {
            "model": model_name,
            "max_tokens": 4096,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
        }

        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.post(
                    "https://api.fireworks.ai/inference/v1/chat/completions",
                    headers=self.headers,
                    json=payload
                )
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Analysis failed: {str(e)}"          

    async def retrieve_ast_contents(self, file_paths : list | None):
        """Retrieve AST file contents from storage"""
        contents = {}
        
        if isinstance(file_paths, str):
            file_paths = [file_paths]
            
        for rel_path in file_paths:
            # Convert backslashes to forward slashes and append _ast
            ast_filename = rel_path.replace('\\', '/') + '_ast.txt'
            ast_path = self.ast_output_dir / ast_filename
            
            try:
                with open(ast_path, 'r', encoding='utf-8') as f:
                    contents[rel_path] = f.read()
            except Exception as e:
                print(f"Error reading AST for file {rel_path}: {e}")
                contents[rel_path] = None
                
        return contents

    async def retrieve_raw_code(self, file_paths, code_dir="E:/Projects.py/Qode-Store-V1/qodestore-rag/test2"):
        """Retrieve actual code content from files
        
        Args:
            file_paths: List of relative file paths to retrieve
            code_dir: Directory where files are located (default: "temp_dir")
            
        Returns:
            dict: Dictionary mapping file paths to their content
        """
        from file_parsing import concurrent_file_processing
        
        # Ensure file_paths is a list
        if isinstance(file_paths, str):
            file_paths = [file_paths]
        
        # Convert code_dir to Path object for better path handling
        code_dir_path = Path(code_dir)
        
        # Check if code_dir exists and is a directory
        if not code_dir_path.exists():
            print(f"Warning: Directory {code_dir} does not exist")
            return {}
            
        if not code_dir_path.is_dir():
            print(f"Error: {code_dir} is not a directory")
            return {}
        
        # Create full paths from relative paths
        full_paths = []
        for rel_path in file_paths:
            # Normalize path separators to match OS
            norm_path = os.path.normpath(rel_path)
            full_path = code_dir_path / norm_path
            full_paths.append(str(full_path))  # Convert Path to string for concurrent_file_processing
        
        contents = {}
        try:
            # Read files concurrently
            results = await concurrent_file_processing(full_paths)
            
            # Process results
            for path, content in results:
                # Get relative path as key
                rel_path = os.path.relpath(path, str(code_dir_path))
                
                # Convert bytes to string
                if isinstance(content, bytes):
                    try:
                        content_str = content.decode('utf-8')
                    except UnicodeDecodeError:
                        content_str = content.decode('latin-1')
                else:
                    content_str = content
                
                contents[rel_path] = content_str
        except Exception as e:
            print(f"Error retrieving raw code: {e}")
        
        return contents

    async def extra_analysis_decider(self, result1 : str):
        """Decide if more analysis is required through ast retrieval and stuff"""
        payload = {
            "model": model_name,
            "max_tokens": 1024,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": EXTRA_ANALYSIS_DECIDER_PROMPT
                },
                {
                    "role": "user",
                    "content": result1
                }
            ]
        }

        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.post(
                    "https://api.fireworks.ai/inference/v1/chat/completions",
                    headers=self.headers,
                    json=payload
                )
            )
            response.raise_for_status()
            decision = response.json()["choices"][0]["message"]["content"].strip()
            # Return "OK" or "NOT OK" based on the LLM's decision
            return "OK" if "OK" in decision else "NOT OK"
        except Exception as e:
            print(f"Decision analysis failed: {str(e)}")
            return "NOT OK"  # Default to more analysis if decision fails
    

if __name__ == "__main__":
    async def main():
        qrooper = Qrooper()
        result = await qrooper._parse_query(
            zip_path="E:/Projects.py/Qode-Store-V1/qodestore-rag/test2.zip",
            query="What is this codebase all about"
        )
        print("\nFINAL QROOPER ANALYSIS:")
        print(result)

    asyncio.run(main())
