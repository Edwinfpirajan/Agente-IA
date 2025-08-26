from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_community.chat_models import ChatOllama

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "local")
OR_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "tinyllama")
OR_MODEL = "meta-llama/llama-3.3-8b-instruct:free"
GROQ_MODEL = "llama3-8b-8192"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"


def get_langchain_model(provider: str = None, model: str = None):
    provider = provider or AI_PROVIDER

    if provider == "openrouter":
        return ChatOpenAI(
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=OR_API_KEY,
            model=model or OR_MODEL
        )
    
    elif provider == "openai":
        return ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model=model or OPENAI_MODEL
        )

    elif provider == "groq":
        return ChatGroq(
            api_key=GROQ_API_KEY,
            model=model or GROQ_MODEL
        )

    elif provider == "ollama":
        return ChatOllama(model=model or LOCAL_MODEL)

    else:
        raise ValueError(f"Unsupported AI provider: {provider}")