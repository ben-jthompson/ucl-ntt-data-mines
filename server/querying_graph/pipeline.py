from .scraper import Scraper
from .querier import Querier
from .context_adder import ContextAdder
from ..data_graph.data_pipeline_funcs import get_local_authority
from .chroma_funcs import make_chroma_db
from .utils import dict_to_document
import json

class Pipeline:
    def __init__(self, location, query, tag, client_id, coords):
        self.location = location
        self.query = query
        self.tag = tag
        self.client_id = client_id
        self.coords = coords
        # TODO readd
        # self.scraper = Scraper(self.location, self.query)
        self.context_adder = ContextAdder(self.tag, self.client_id)
        self.retriever = None
        self.docs = []

    def data_pipeline(self):
        self.location = get_local_authority(self.coords)

    def scrape(self):
        self.docs = self.scraper.run()

    def add_context(self):
        context = self.context_adder.run(self.client_id)
        self.docs.append(context)

    def embed(self):
        # TODO temp to bypass scrape
        with open("outputs/final_results.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.docs = [dict_to_document(d) for d in data]
        # TODO end temp
        self.retriever = make_chroma_db(self.docs, self.location)
        
    
    def query_llm(self):
        # querier = Querier(self.retriever, self.query)
        # # querier.get_queries()
        # response = querier.run()
        # return response
        with open('gpt-4o-mini-multiquery-output.txt', "r", encoding="utf-8") as f:
            data=f.read()
        return data
        

    def run(self):
        self.add_context()
        self.embed()
        self.query_llm()
        # with open('gpt-4o-mini-multiquery-output.txt', "r", encoding="utf-8") as f:
        #     data=f.read()
        # return data

if __name__ == '__main__':
    pipeline = Pipeline(location='Nottingham', 
                        query='Gravitational Energy', 
                        tag='Area Demographics', client_id='2ff3ade2-9405-47ee-8014-804361215db2')
    pipeline.run()