from langchain_chroma import Chroma
from langchain.schema import Document
from typing import List
from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from operator import add as add_messages
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.tools import tool

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# embedding model
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
)

def url_suitability_scoring(urls: List[Document], query: str):
    search_collection = Chroma(
        embedding_function=embeddings,
        collection_name="search_results"
        )
    search_collection.add_documents(urls)
    retriever = search_collection.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5} 
)
    relevant_results = retriever.invoke(query)

    if not relevant_results:
        return "No relevant information in the accompanying documents."
    
    results = []
    for doc in relevant_results:
        results.append(doc)
    
    return results

