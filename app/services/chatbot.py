import os
import requests

# Variables de entorno
AI_PROVIDER = os.getenv("AI_PROVIDER", "local")
LOCAL_URL = os.getenv("LOCAL_MODEL_URL", "http://localhost:11434/api/chat")
OR_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Modelos definidos directamente
OR_MODEL = "meta-llama/llama-3.3-8b-instruct:free"
LOCAL_MODEL = "tinyllama:latest"
GROQ_MODEL = "llama3-8b-8192"

def ensure_local_model_loaded():
    """Verifica si el modelo local está cargado; si no, lo carga."""
    list_url = LOCAL_URL.replace("/chat", "/tags")
    response = requests.get(list_url)

    if response.status_code == 200:
        loaded_models = [m["name"] for m in response.json().get("models", [])]
        if LOCAL_MODEL not in loaded_models:
            print(f"Cargando modelo local '{LOCAL_MODEL}'...")
            pull_url = LOCAL_URL.replace("/chat", "/pull")
            pull_response = requests.post(pull_url, json={"name": LOCAL_MODEL})
            if pull_response.status_code != 200:
                raise Exception(f"[Local] Error al cargar modelo: {pull_response.text}")
    else:
        raise Exception(f"[Local] No se pudo verificar modelos locales: {response.text}")

def get_ai_response(query: str, history: list[tuple[str, str]], user_id: str = "anon", model_type: str = None) -> dict:
    messages = []
    for q, a in history:
        messages.append({"role": "user", "content": q})
        messages.append({"role": "assistant", "content": a})

    messages.append({"role": "user", "content": query})
    chosen_provider = model_type or AI_PROVIDER


    # OPENROUTER
    if chosen_provider == "openrouter":
        headers = {
            "Authorization": f"Bearer {OR_API_KEY}",
            "HTTP-Referer": "http://localhost",
            "Content-Type": "application/json",
        }
        data = {
            "model": OR_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"Estás interactuando con el usuario identificado con documento {user_id}. "
                        "Tienes acceso al historial completo de la conversación."
                    )
                }
            ] + messages
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers)
        if response.status_code == 200:
            return {
                "answer": response.json()["choices"][0]["message"]["content"],
                "model_used": OR_MODEL
            }
        return {
            "answer": f"[OpenRouter] Error: {response.status_code} {response.text}",
            "model_used": OR_MODEL
        }

    # GROQ
    elif chosen_provider == "groq":
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "model": GROQ_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"Estás interactuando con el usuario identificado con documento {user_id}. "
                        "Tienes acceso al historial completo de la conversación."
                    )
                }
            ] + messages
        }
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers)
        if response.status_code == 200:
            return {
                "answer": response.json()["choices"][0]["message"]["content"],
                "model_used": GROQ_MODEL
            }
        return {
            "answer": f"[Groq] Error: {response.status_code} {response.text}",
            "model_used": GROQ_MODEL
        }

    # LOCAL
    elif chosen_provider == "local":
        try:
            ensure_local_model_loaded()
        except Exception as e:
            return {
                "answer": f"[Local] Error al cargar modelo: {str(e)}",
                "model_used": LOCAL_MODEL
            }

        headers = {"Content-Type": "application/json"}
        data = {
            "model": LOCAL_MODEL,
            "messages": messages,
            "stream": False
        }
        response = requests.post(LOCAL_URL, json=data, headers=headers)
        try:
            response_data = response.json()
            return {
                "answer": response_data["message"]["content"],
                "model_used": LOCAL_MODEL
            }
        except Exception as e:
            return {
                "answer": f"[Local] Formato de respuesta inesperado: {response.text}",
                "model_used": LOCAL_MODEL
            }

    # Proveedor no válido
    return {
        "answer": "AI_PROVIDER inválido. Usa 'openrouter', 'groq' o 'local'.",
        "model_used": "desconocido"
    }
