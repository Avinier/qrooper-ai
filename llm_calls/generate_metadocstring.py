import os
import requests
import json
from typing import Dict, Any
from pathlib import Path

def analyze_ast_with_llm(ast_content: str, ast_file_path: str) -> str:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer fw_3ZYVTdrvNUzJcNyGe4P4fjLY"
    }

    payload = {
        "model": "accounts/fireworks/models/deepseek-v3",
        "max_tokens": 4096,
        "temperature": 0.3,
        "messages": [{
            "role": "user",
            "content": f"Analyze this AST and provide a concise description of the code's structure and functionality:\n{ast_content}"
        }]
    }

    try:
        response = requests.post(
            "https://api.fireworks.ai/inference/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        
        analysis = response.json()['choices'][0]['message']['content']
        
        # Append analysis to the AST file
        with open(ast_file_path, 'a') as f:
            f.write(f"\nContext:{analysis}")
        
        return analysis

    except Exception as e:
        print(f"LLM Analysis failed: {str(e)}")
        return ""
