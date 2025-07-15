import ollama
from langchain.embeddings.base import Embeddings

class OllamaEmbeddings(Embeddings):
    def __init__(self, model : str):
        self.model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = ollama.embed(model=self.model, input=texts)
        return response['embeddings']
    
    def embed_query(self, text: str) -> list[float]:
        query = ollama.embed(model=self.model, input=text)
        return query['embeddings'][0]
    


    