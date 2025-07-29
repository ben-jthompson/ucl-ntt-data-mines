import requests
import os
import fitz
import pandas as pd
from langchain.schema import Document

def download_file(url: str, save_dir="server/downloads"):
    headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}
    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.basename(url.split("?")[0])  
    filepath = os.path.join(save_dir, filename)

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
        return filepath
    else:
        print(f"Failed to download: {url}")
        print(f"[INFO] Status code: {response.status_code}")
        print(f"[INFO] Response headers: {response.headers}")
        return None
    
def document_to_dict(doc: Document) -> dict:
    return {
        "page_content": doc.page_content,
        "metadata": doc.metadata
    }

def dict_to_document(dict: dict) -> Document:
    return Document(page_content=dict["page_content"], metadata=dict["metadata"])

def extract_text_from_pdf(path: str, save_dir="server/downloads") -> str:
    filename = os.path.basename(path.split("?")[0])  
    filepath = os.path.join(save_dir, filename)
    file = fitz.open(filepath)
    return "\n".join(page.get_text() for page in file)

def extract_text_from_csv(filepath: str) -> str:
    file = pd.read_csv(filepath)
    return file.to_string(index=False)

def extract_text_from_source(filepath: str, doc: Document):
    if filepath.endswith('.pdf'):
        doc.page_content = extract_text_from_pdf(filepath)
    elif filepath.endswith('.csv'):
        doc.page_content = extract_text_from_csv(filepath)

    # print('Page content for pdf is ', doc.page_content)
    return doc

