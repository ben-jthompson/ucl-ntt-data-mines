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
from langchain_chroma import Chroma
from langchain_core.tools import tool

# embedding model
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
directory = os.path.join(os.getcwd(), 'server/vectordb')
db_collection = "suitabilitydb"

def add_vectors_from_files(files):

    vectordb = Chroma(
        embedding=embeddings,
        persist_directory=directory,
        collection_name=db_collection
    )
    if not os.path.exists(directory):
        os.makedirs(directory)

    for file_path in files:
        if not os.path.exists(file_path):
            continue
        
        pdf_loaded = PyPDFLoader(file_path) 
        try:
            pages = pdf_loaded.load()
        except Exception as e:
            continue

        pages_split = text_splitter.split_documents(pages)
        vectordb.add_documents(pages_split)

    return vectordb


@tool
def retriever_tool(query: str, db: Chroma) -> str:
    """
    This tool returns the most relevant information from the documents in the RAG pipeline, to be used as information in the creation of the suitability report.
    """
    retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5} 
)
    docs = retriever.invoke(query)

    if not docs:
        return "No relevant information in the accompanying documents."
    
    results = []
    for i, doc in enumerate(docs):
        results.append(f"Document {i+1}:\n{doc.page_content}")
    
    return "\n\n".join(results)


tools = [retriever_tool]

llm = llm.bind_tools(tools)
