import httpx
from langchain.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END
import json

def rickmorty_characters(endpoint: str) -> str:
    url = f"https://rickandmortyapi.com/api/{endpoint}"
    resp = httpx.get(url)
    data = resp.json()
    print("Response from Rick and Morty API:")
    print(f"Nombre: {data['name']}")
    print(f"Especie: {data['species']}")
    print(f"Estado: {data['status']}")

rickmorty_characters("character/7")


def rickmorty_tool(endpoint: str) -> str:
    """Consulta la API de Rick and Morty en el endpoint REST indicado"""
    url = f"https://rickandmortyapi.com/api/{endpoint}"
    resp = httpx.get(url)
    return resp.text

