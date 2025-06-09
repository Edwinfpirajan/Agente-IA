import os
import requests

AI_PROVIDER = os.getenv("AI_PROVIDER", "openrouter")

# Configuración OpenRouter
OR_API_KEY = os.getenv("OPENROUTER_API_KEY")
OR_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemma-7b-it")

# Configuración modelo local
LOCAL_URL = os.getenv("LOCAL_MODEL_URL", "http://localhost:11434/api/chat")
LOCAL_MODEL = os.getenv("LOCAL_MODEL_NAME", "gemma")

def get_ai_response(query: str) -> str:
    if AI_PROVIDER == "openrouter":
        headers = {
            "Authorization": f"Bearer {OR_API_KEY}",
            "HTTP-Referer": "http://localhost",
            "Content-Type": "application/json",
        }
        data = {
            "model": OR_MODEL,
            "messages": [{"role": "user", "content": query}]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"[OpenRouter] Error: {response.status_code} {response.text}"

    elif AI_PROVIDER == "local":
        headers = {"Content-Type": "application/json"}
        data = {
            "model": LOCAL_MODEL,
            "messages": [{"role": "user", "content": query}],
            "stream": False
        }
        response = requests.post(LOCAL_URL, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()["message"]["content"]
        return f"[Local] Error: {response.status_code} {response.text}"

    return "Invalid AI_PROVIDER. Use 'openrouter' or 'local'."
