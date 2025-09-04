import httpx
from langchain.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END
import json

@tool
def rickmorty_characters(endpoint: str) -> str:
    """Consulta la API de Rick and Morty en el endpoint REST indicado"""
    from app.services.chatbot import AgentState
    url = f"https://rickandmortyapi.com/api/{endpoint}"
    resp = httpx.get(url)
    data = resp.json()
    AgentState.species = data['species']
    return data['name']



#Nodo de herramienta para llamar a la API de Rick and Morty en el grafo
# rickmorty_tool = ToolNode.from_function(
#     func=rickmorty_characters,
#     name="rickmorty_tool",
#     description="Consulta la API de Rick and Morty ",
#     return_direct=True
# )
