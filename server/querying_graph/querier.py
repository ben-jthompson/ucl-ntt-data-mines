from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from langchain.retrievers.multi_query import MultiQueryRetriever

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

class Querier:
    def __init__(self, retriever, query):
        self.query = query
        self.api_key = api_key
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature = 0, api_key=self.api_key)
        self.retriever = MultiQueryRetriever.from_llm(llm=self.llm, retriever=retriever)

    def query_vector_db(self):
        docs = self.retriever.invoke(self.query)
        return docs
    
    def run_query(self, docs):
        system_prompt = """
You are an intelligent AI assistant who answers questions about data centre feasibility in coal mines.
Please always cite the specific sources you use in your answers. Use the data provided to you.
"""
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=f'For this section, please summarise the data you have been given. Do not use any other data: {docs}')]
        # messages = [SystemMessage(content=system_prompt), HumanMessage(content=f'Please conduct analysis, focusing specifically on the location: {self.location}, using this specific data: {docs}')]
        return self.llm.invoke(messages)
    
    def get_queries(self):
        # Generate sub queries and display
        sub_queries = self.retriever.llm_chain.invoke(self.query)
        print("Generated Sub-Queries:")
        print(sub_queries)

    def run(self):
        result = self.query_vector_db()
        return self.run_query(result)