#TODO:
# - check why all files aren't being parsed in ast-output
# - see whether code should be taken from github api or node.text.decode in ast
import asyncio
import sys
import os
from llm_calls.qrooper_engine import Qrooper
from generate_ast import main as ast_parse_file

async def main(zip_path, query):
    # Generate AST files if needed
    ast_output_dir = "ast-output"
    if not os.path.exists(ast_output_dir):
        print(f"AST output directory not found. Generating AST files for {zip_path}...")
        ast_result = await ast_parse_file(zip_path)
        print(f"AST generation result: {ast_result}")
    else:
        print(f"Using existing AST files in {ast_output_dir}")

    # Process query with Qrooper
    qrooper = Qrooper(
        ast_output_dir=ast_output_dir
    )
    result = await qrooper._parse_query(zip_path, query)
    
    print("\n" + "="*50)
    print(f"Query: {query}")
    print("="*50)
    print(result)
    print("="*50 + "\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <zipfile> <query>")
        sys.exit(1)

    zip_path = sys.argv[1]
    query = sys.argv[2]

    asyncio.run(main(zip_path, query))