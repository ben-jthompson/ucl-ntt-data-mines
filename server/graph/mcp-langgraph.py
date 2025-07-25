from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from typing import TypedDict, List
import requests
import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4o", temperature = 0, api_key=api_key) 

# -- Define input/output schema for state --
class FeasibilityState(TypedDict):
    location: str
    documents: List[str]
    answer: str

def retrieve_documents(state: FeasibilityState) -> FeasibilityState:
    system_prompt = """
You are an intelligent AI assistant who answers questions about data centre feasibility in coal mines.
If you need to look up some information before asking a follow up question, you are allowed to do that!
Please always cite the specific parts of the sources you use in your answers.
"""
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=f'Please conduct analysis for the location: {state["location"]}')]
    
    location = state['location']
    # print(f"Searching for documents on: {location}")
    docs = [
        f"Report on underground cooling systems in {location}",
        f"Relevant local authorities near {location}",
        f"Geotechnical analysis of mines in {location}"
    ]
    answer = llm.invoke(messages)
    return {**state, "answer": answer}

def summarise_documents(state: FeasibilityState) -> FeasibilityState:
    print(f"Summarising documents for: {state['location']}")
    # answer = f"Based on {len(state['documents'])} documents, {state['location']} shows moderate feasibility for a mine-based data centre."
    return state

# -- Entry point node --
def start_node(location: str) -> FeasibilityState:
    return {"location": location, "documents": [], "answer": ""}

# -- Build LangGraph workflow --
graph = StateGraph(FeasibilityState)
graph.add_node("retrieve_docs", RunnableLambda(retrieve_documents))
graph.add_node("summarize", RunnableLambda(summarise_documents))

# -- Edges between steps --
graph.set_entry_point("retrieve_docs")
graph.add_edge("retrieve_docs", "summarize")
graph.add_edge("summarize", END)

# -- Compile and use --
app = graph.compile()

if __name__ == "__main__":
    user_location = "Nottingham, UK"
    
    result = app.invoke({'location': user_location, 'documents': [], 'answer': '', 'messages': []})
    print("\n✅ Final output:")
    print(result['answer'])
