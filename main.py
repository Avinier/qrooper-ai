import asyncio
import sys
from llm_calls.qrooper_engine import Qrooper
from generate_ast import ASTGenerator

async def main(zip_path, query):
    # Generate AST files if needed
    ast_generator = ASTGenerator()
    await ast_generator.generate_from_zip(zip_path)

    # Process query with Qrooper
    qrooper = Qrooper(
        api_key="fw_3ZYVTdrvNUzJcNyGe4P4fjLY",
        ast_output_dir="ast-output"
    )
    result = await qrooper.parse_query(zip_path, query)
    
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