from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from langchain.retrievers.multi_query import MultiQueryRetriever

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

class Querier:
    def __init__(self, retriever, location):
        self.location = location
        self.api_key = api_key
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature = 0, api_key=api_key)
        self.retriever = MultiQueryRetriever.from_llm(llm=self.llm, retriever=retriever)

    def query_vector_db(self, query):
        docs = self.retriever.invoke(query)
        return docs
    
    def run_query(self, docs):
        system_prompt = """
You are an intelligent AI assistant who answers questions about data centre feasibility in coal mines.
Please always cite the specific parts of the sources you use in your answers. Use the data provided to you.
"""
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=f'Please conduct analysis, focusing specifically on the location: {self.location}, using this specific data: {docs}')]
        return self.llm.invoke(messages)