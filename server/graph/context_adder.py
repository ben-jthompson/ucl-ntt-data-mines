from server.graph.utils import extract_from_source
from langchain.schema import Document

class ContextAdder:
    def __init__(self, tag):
        self.tag = tag

    # find the documents uploaded by the user which are relevant
    # TODO join up with UploadedDoc file type
    def find_tagged_files(self, uploaded_docs):
        relevant_docs = [Document(page_content=doc.file_name, 
                                  metadata={'url': doc.file_path, 
                                            'description': doc.description}) 
                                            for doc in uploaded_docs if self.tag in doc.tags]
        for doc in uploaded_docs:
            if self.tag in doc.tags:
                doc.page_content = self.handle_file_parsing(doc)
                

    # determine method of parsing based on file format
    def handle_file_parsing(self, doc):
        return extract_from_source(doc)

    