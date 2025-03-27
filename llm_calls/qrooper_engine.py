import asyncio
import requests
from pathlib import Path
from llm_calls.filename_evaluator import filename_evaluate

model_name = "accounts/fireworks/models/deepseek-v3"
api_key = "fw_3ZYVTdrvNUzJcNyGe4P4fjLY"

class Qrooper:
    def __init__(self, ast_output_dir="ast-output"):
        self.ast_output_dir = Path(ast_output_dir)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    async def parse_query(self, zip_path, query):
        """Main query processing pipeline"""
        # Step 1: Get relevant filenames using LLM
        relevant_files = await filename_evaluate(
            zip_path, query
        )
        
        if not relevant_files:
            return "qrooper error: No relevant files found for this query"
            
        # Step 2: Retrieve AST contents for relevant files
        ast_contents = await self.retrieve_ast_contents(relevant_files)
        
        # Step 3: Analyze with LLM for final answer
        return await self.analyze_with_llm(ast_contents, query)

    async def retrieve_ast_contents(self, file_paths):
        """Retrieve AST file contents from storage"""
        contents = {}
        
        for rel_path in file_paths:
            # Convert file path to AST file path
            ast_path = self.ast_output_dir / f"{rel_path}_ast.txt"
            
            try:
                with open(ast_path, 'r', encoding='utf-8') as f:
                    contents[rel_path] = f.read()
            except Exception as e:
                print(f"Error reading AST for {rel_path}: {e}")
                contents[rel_path] = None
                
        return contents

    async def analyze_with_llm(self, ast_contents, query):
        """Final LLM analysis with relevant AST contents"""
        context = "\n\n".join(
            f"File: {path}\nAST:\n{content}"
            for path, content in ast_contents.items()
            if content is not None
        )
        
        payload = {
            "model": "accounts/fireworks/models/deepseek-v3",
            "max_tokens": 4096,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a code analysis assistant. Analyze the following ASTs to answer the user's query."
                },
                {
                    "role": "user",
                    "content": f"Query: {query}\n\nContext ASTs:\n{context}"
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

if __name__ == "__main__":
    async def main():
        qrooper = Qrooper(api_key="fw_3ZYVTdrvNUzJcNyGe4P4fjLY")
        result = await qrooper.parse_query(
            zip_path="test2.zip",
            query="Where are database connections being created in the code?"
        )
        print("\nFinal Analysis:")
        print(result)

    asyncio.run(main())