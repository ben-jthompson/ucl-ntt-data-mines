from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever
from langchain.schema import Document
from typing import List
from dotenv import load_dotenv
import os
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# embedding model
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
)

# splitter model
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

def make_chroma_db(documents: List[Document], query: str) -> VectorStoreRetriever:
    # create a store for the vectors
    persist_dir = os.path.abspath('/server/querying_graph/chroma_store') 
    os.makedirs(persist_dir, exist_ok=True)


    documents_split = text_splitter.split_documents(documents)
    vectordb = Chroma.from_documents(documents=documents_split,
                          embedding=embeddings,
                          collection_name=f'{query.lower().replace(" ", "-")}-suitability',
                          persist_directory=persist_dir)
    # TODO: delete collections after use
    retriever = vectordb.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 10} 
)
    return retriever

def url_suitability_scoring(urls: List[Document], query: str) -> List[Document]:
    search_collection = Chroma(
        embedding_function=embeddings,
        collection_name=f"{query.replace(' ', '-')}-Results".lower()
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

