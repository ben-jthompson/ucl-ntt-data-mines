from .scraper import Scraper
from .querier import Querier
from .chroma_funcs import make_chroma_db
from .utils import dict_to_document
import json

class Pipeline:
    def __init__(self, location, query):
        self.location = location
        self.query = query
        self.scraper = Scraper(self.location, self.query)
        self.retriever = None
        self.docs = None

    def scrape(self):
        self.docs = self.scraper.run()
        

    def embed(self):
        # TODO temp to bypass scrape
        with open("outputs/final_results.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.docs = [dict_to_document(d) for d in data]
        # TODO end temp
        self.retriever = make_chroma_db(self.docs, self.location)
        
    
    def query_llm(self):
        querier = Querier(self.retriever, self.query)
        
        ques = querier.get_queries()
        print('Queries are ', ques)
        # querier.run(self.query)
        # with open('gpt-4o-mini-multiquery-output.txt', "r", encoding="utf-8") as f:
        #     data=f.read()
        # return data
        

    def run(self):
        self.embed()
        self.query_llm()
        # with open('gpt-4o-mini-multiquery-output.txt', "r", encoding="utf-8") as f:
        #     data=f.read()
        # return data

if __name__ == '__main__':
    pipeline = Pipeline(location='Nottingham', query='Nottinghamshire Report Mine Reuse Heat Water for Data Center Cooling')
    pipeline.run()