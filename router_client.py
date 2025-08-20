# Lightweight OpenRouter client (OpenAI-compatible Chat Completions style)
# Expects OPENROUTER_API_KEY in environment variables.
import os
import requests
from typing import Any, Dict, List
from dotenv import load_dotenv

load_dotenv()  # load variables from .env file

OPENROUTER_URL = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    # we do not raise here because the local utilities may still run without the LLM.
    pass

def call_openrouter(messages: List[Dict[str, str]], model: str = 'gpt-4o-mini', max_tokens: int = 1024, temperature: float = 0.0) -> Dict[str, Any]:
    """Call OpenRouter chat completions endpoint. Returns parsed JSON response."""
    if not API_KEY:
        raise RuntimeError('OPENROUTER_API_KEY not set in environment.')
    payload = {
        'model': model,
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens
    }
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    resp = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.json()
