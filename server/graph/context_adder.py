from server.graph.utils import extract_from_source, dict_to_document
from langchain.schema import Document
import os
import json

class ContextAdder:
    def __init__(self, tag):
        self.tag = tag

    # find the documents uploaded by the user which are relevant
    def get_uploaded_files(self, client_id):
        upload_dir = os.path.join(os.getcwd(), 'server/uploads', client_id)
        uploaded_files = [os.path.join(upload_dir, file) for file in os.listdir(upload_dir)]
        return uploaded_files

    # TODO join up with UploadedDoc file type - props:
    def find_tagged_files(self, uploaded_docs):
        # check metadata for tags
        tagged_files = []
        for path in uploaded_docs:
            if path.endswith('.meta.json'):
                with open(path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    if self.tag in metadata.get('tags', []):
                        tagged_files.append(Document(page_content=metadata['description'], metadata={'url':path[:-10]}))

        for doc in tagged_files:
            self.handle_file_parsing(doc) 

        return tagged_files     

    # determine method of parsing based on file format
    def handle_file_parsing(self, doc):
        document_returned =  extract_from_source(filepath=doc.metadata.get('url'), doc=doc, save_dir='server/uploads')
        return document_returned
    
    def run(self, client_id):
        files = self.get_uploaded_files(client_id)
        relevant_files = self.find_tagged_files(files)
        return relevant_files

    