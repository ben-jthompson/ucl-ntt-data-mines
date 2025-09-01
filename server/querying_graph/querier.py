from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from langchain.retrievers.multi_query import MultiQueryRetriever

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

class Querier:
    def __init__(self, location, region, retriever, query):
        self.query = query['plain_query']
        # TODO: readd
        self.example = query.get('example', None)
        self.region = region[0]['name']
        self.location = location
        self.api_key = api_key
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature = 0, api_key=self.api_key)
        self.retriever = MultiQueryRetriever.from_llm(llm=self.llm, retriever=retriever)

    def query_vector_db(self):
        docs = self.retriever.invoke(self.query)
        return docs
    
    def add_location_to_query(self):
        self.query = self.query + f" specifically in {self.location}, {self.region}, UK?"
    
    def formulate_query(self):
        system_prompt = """
    You are an intelligent AI assistant who answers questions about data centre feasibility. 
    - You must first run the `query_vector_db` tool on all of the sub-queries provided, in order to get information. The tool will return Content: <relevant content>, Redirect URL: <redirect url of the source> for each result."
    - Always cite the URL, which is available in the results from the tool, under 'Redirect URL', when using these.
    - If you need more context or supporting information, call the query_vector_db tool with a reformulated sub-query.
    - If you cannot find relevant data from the `query_vector_db' tool after reformulating queries three times, then rely on your own knowledge to provide an informed answer. 
    - When doing so, clearly state that the information is based on your general knowledge rather than retrieved documents.
    - If neither the data from the vector database, nor your own knowledge provides an answer, clearly state the gap rather than speculating.
    - Before producing the Final Answer, you MUST call the `add_source_to_bibliography` tool once for each source you cite. The tool takes a single string input: the redirect URL of the source.
    Example: add_source_to_bibliography(\"https://example.com/report.pdf\")
    - Only AFTER you have finished all necessary tool calls, return the Final Answer as a complete, stand-alone answer to the query. Do not mix tool calls and the Final Answer in the same step.
    - In your Final Answer, explain why the cited factors are important in the context of putting data centres in a mine in the area."""
        self.add_location_to_query()
        sub_queries = self.retriever.llm_chain.invoke(self.query)
        human_prompt = f"""The query for this section is {self.query}, with three sub-queries of interest being: {sub_queries}."""
        if self.example:
            human_prompt = human_prompt + f' Please output in a format similar to this: {self.example}'
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]
        return messages
    
    def get_queries(self):
        # Generate sub queries and display
        sub_queries = self.retriever.llm_chain.invoke(self.query)
        print("Generated Sub-Queries:")
        print(sub_queries)

    def run(self):
        result = self.query_vector_db()
        return self.run_query(result)