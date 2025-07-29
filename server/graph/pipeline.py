from .scraper import Scraper
from .querier import Querier
from .chroma_funcs import make_chroma_db
import json

class Pipeline:
    def __init__(self, location, query):
        self.location = location
        self.query = query

    def run(self):
        # scraper = Scraper(self.location, self.query)
        # docs = scraper.run()
        # retriever = make_chroma_db(docs, self.location)
        # querier = Querier(retriever, self.location)
        # result = querier.query_vector_db(self.query)
        # output = querier.run_query(result)
        with open('gpt-4o-mini-multiquery-output.txt', "w", encoding="utf-8") as f:
            data=f.read()
        return data

if __name__ == '__main__':
    pipeline = Pipeline(location='Nottingham', query='Nottinghamshire Report Mine Reuse Heat Water')
    pipeline.run()