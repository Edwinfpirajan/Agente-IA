from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_community.vectorstores import FAISS
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import tool
from app.prompts.prompt_bico import PROMPT_BOT_BICO
from app.services.models import get_langchain_model
from app.conections.Apis_test import rickmorty_characters
from pydantic import Field
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from typing import List, Union
import os

AI_PROVIDER = os.getenv("AI_PROVIDER", "local")
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "tinyllama")



class AgentState(MessagesState):  
    phone: str
    question: str
    messages: List[Union[HumanMessage, AIMessage]] = Field(default_factory=list)
    context: str
    answer: str
    model_used: str 
    steps: int
    remaining_steps: int

def get_answer_for_agent(question: str, history: list[tuple[str, str]], model_used: str, phone: str = "anon") -> dict:
    state = get_agent_state_from_history(history, phone=phone, question=question, model_used=model_used)
    result_state = agent_graph.invoke(state)

    return {
        "question": result_state["question"],
        "answer": result_state["answer"],
        "model_used": result_state["model_used"],
    }

def get_agent_state_from_history(history: list[tuple[str, str]], question: str, phone: str, model_used: str) -> AgentState:
    messages = []

    for user_msg, bot_msg in history:
        messages.append(HumanMessage(content=user_msg))
        messages.append(AIMessage(content=bot_msg))

        if len(messages) > 14:  
            messages = messages[-14:]

    context = faiss_tool(question)

    messages.append(HumanMessage(content=question))

    return AgentState(
        phone=phone,
        question=question,
        messages=messages,
        context=context,
        model_used=model_used,
        answer="",
        steps=0,
        remaining_steps=5, 
    )

@tool
def faiss_tool(question: str) -> str:
    """
    Herramienta para recuperar información relevante de un vectorstore FAISS.
    Se devuelve en formato de texto plano para poder contextualizar la respuesta del agente.
    """
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    vectorstore = FAISS.load_local("vectorstore_clientes", embeddings, allow_dangerous_deserialization=True)

    retriever = vectorstore.as_retriever(k=2)

    docs = retriever.get_relevant_documents(question)

    return "\n\n".join([doc.page_content for doc in docs])


# def create_agent(provider: str = None, model: str = None):
#     provider = provider or os.getenv("AI_PROVIDER", "local")
#     model = model or os.getenv("LOCAL_MODEL", "tinyllama")

#     if provider and model:
#         try:
#             llm = get_langchain_model(provider=provider, model=model)
#             return llm
#         except ValueError as e:
#             raise ValueError(f"Error al obtener el modelo: {e}")
#     else:
#         raise ValueError("Debe proporcionar un proveedor y un modelo válidos.")

prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            PROMPT_BOT_BICO.format(
                context="{context}",
                question="{question}",
                messagges="{messages}",
            )
        ),
        HumanMessagePromptTemplate.from_template("{question}"),
    ]
)

llm = get_langchain_model(provider="openai", model="gpt-4.1-2025-04-14")

agent = create_react_agent(
model=llm,
tools=[faiss_tool , rickmorty_characters],
prompt=prompt,
state_schema=AgentState,
)

def agent_node(state: AgentState) -> AgentState:
    # Limita la recursión interna del agente para evitar bucles
    try:
        result = agent.invoke(state, config={"recursion_limit": 6})
        return AgentState(
            phone=result["phone"],
            question=result["question"],
            messages=result["messages"],
            context=result["context"],
            model_used=result["model_used"],
            answer=result["messages"][-1].content,
            steps=result["steps"] + 1,
            remaining_steps=result["remaining_steps"] - 1
        )
    except Exception:
        # Fallback sin herramientas para evitar 500 si el agente entra en loop
        sys_msg = SystemMessage(content=PROMPT_BOT_BICO.format(
            context=state.context,
            question=state.question,
            messagges=state.messages,
            species=state.species,
        ))
        human_msg = HumanMessage(content=state.question)
        ai = llm.invoke([sys_msg, human_msg])
        messages = state.messages + [human_msg, AIMessage(content=ai.content)]
        return AgentState(
            phone=state.phone,
            question=state.question,
            messages=messages,
            context=state.context,
            model_used=state.model_used,
            answer=ai.content,
            steps=state.steps + 1,
            remaining_steps=max(0, state.remaining_steps - 1)
        )

builder = StateGraph(AgentState)
builder.add_node("agent_node",agent_node )
builder.add_edge(START, "agent_node")
builder.add_edge("agent_node", END)
agent_graph = builder.compile()
