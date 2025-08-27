import requests
from urllib.parse import urlparse, parse_qs, unquote
import os
import fitz
import docx
import json
import csv
import pandas as pd
import geopandas as gpd
from spire.doc import Document as SpireDoc
from langchain.schema import Document
import subprocess

# find file type for scraped documents
def detect_file_type(url: str) -> str:
    # file type address stripping
    file_type = os.path.splitext(os.path.basename(url.split("?")[0]))[-1].lower()
    if file_type in {'.pdf', '.csv', '.json', '.geojson', '.docx', '.doc', '.xlsx', '.xls'}:
        return file_type
    
    # edge case for microsoft office viewer
    parsed = urlparse(url)
    if 'view.officeapps.live.com' in parsed.netloc:
        actual_url = get_ms_office_url(parsed)
        ext = os.path.splitext(actual_url)[1].lower()
        if ext in {'.docx', '.doc', '.xlsx', '.xls'}:
            return ext

    # fallback for different address
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        content_type = response.headers.get("Content-Type", "").lower()
    except Exception as e:
        print(f"Could not get Content-Type for {url}: {e}")
        return None

    if "pdf" in content_type:
        return '.pdf'
    elif "csv" in content_type:
        return '.csv'
    elif "msword" in content_type or "wordprocessingml" in content_type:
        return '.docx'
    elif "json" in content_type and "geo" not in content_type:
        return '.json'
    elif "geojson" in content_type:
        return '.geojson'
    return None  



def download_file(url: str, client_id: str, save_dir="server\downloads"):
    headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}
    os.makedirs(os.path.join(os.getcwd(), save_dir, client_id), exist_ok=True)
    filename = os.path.basename(url.split("?")[0])  
    filepath = os.path.join(save_dir, filename)

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename} to {filepath}")
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

def extract_ms_office_link(path: str) -> str:
    """If MS Office type file detected (.docx, .xlsx, .doc, .xls) - then extract the download link from the viewer url

    Args:
        path (str): web address of file

    Returns:
        str: correct download address for file
    """
    parsed = urlparse(path)
    if 'view.officeapps.live.com' in parsed.netloc:
        actual_url = get_ms_office_url(parsed)
        return actual_url
    else:
        return path
        
            
def get_ms_office_url(parsed: str) -> str:
    query = parse_qs(parsed.query)
    src = query.get('src')
    if src:
        actual_url = unquote(src[0])
        return actual_url
    else:
        return None

def extract_from_pdf(path: str, save_dir="server/downloads") -> str:
    filename = os.path.basename(path.split("?")[0])  
    filepath = os.path.join(save_dir, filename)
    file = fitz.open(filepath)
    return "\n\n".join(page.get_text() for page in file)

def extract_from_docx(filepath: str) -> str:
    print('Extracting from docx')
    file = docx.Document(filepath)
    paras = [para.text for para in file.paragraphs]
    return '\n\n'.join(paras)

def extract_from_doc(filepath: str) -> str:
    try:
        spire_doc = SpireDoc()
        spire_doc.LoadFromFile(filepath)
        pdf_file = filepath[:-4] + '.pdf'
        spire_doc.SaveToFile(pdf_file)
        spire_doc.Close()
        os.remove(filepath)
        return extract_from_pdf(pdf_file)
    except Exception as e:
        print(f"Failed to extract .doc file {filepath}: {e}")
        return

def extract_from_excel(filepath: str) -> str:
    spreadsheet = pd.ExcelFile(filepath)
    data = []
    for sheet in spreadsheet.sheet_names:
        sheet_content = spreadsheet.parse(sheet)
        sheet_csv = sheet_content.to_csv(index=False)
        data.append(f"Sheet: {sheet}\n{sheet_csv}")
        print(f"Sheet: {sheet}\n{sheet_csv}"[:250])
    return '\n\n'.join(data)

def extract_from_csv(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8') as f:
        data = f.read()
        print(data[:250])
    return data


def extract_from_json(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return json.dumps(data, indent=2)

def extract_from_geojson(filepath: str) -> str:
    gdf = gpd.read_file(filepath)
    return gdf.to_json(indent=2)

def extract_from_shp(filepath: str) -> str:
    gdf = gpd.read_file(filepath)
    return gdf.to_string(index=False)

def extract_from_source(filepath: str, doc: Document, save_dir='server/downloads') -> Document:
    parsing_method = {'.pdf': extract_from_pdf, 
                      '.docx': extract_from_docx,
                      '.doc': extract_from_doc,
                      '.xlsx': extract_from_excel,
                      '.xls': extract_from_excel, 
                      '.csv': extract_from_csv, 
                      '.shp': extract_from_shp,
                      '.json': extract_from_json, 
                      '.geojson': extract_from_geojson }
    # if document has been found during scraping:
    if save_dir == 'server/downloads':
        filename = os.path.basename(filepath.split("?")[0])  
        filepath = os.path.join(save_dir, filename)
    # else document has been uploaded by user, so filepath added in the arg is okay

    # iterate through keys to find appropriate extraction method
    for key, func in parsing_method.items():
        if filepath.endswith(key):
            # edge case: if doc
            doc.page_content=func(filepath)
            return doc

def strip_csv_metadata(filepath: str, min_columns=0) -> str:
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    delimiter = csv.Sniffer().sniff(''.join(lines[:10])).delimiter  # auto-detect delimiter

    # Find the first valid header row
    header_idx = None
    for i, line in enumerate(lines):
        # Split using delimiter and strip whitespace
        columns = [col.strip() for col in line.split(delimiter)]
        if len(columns) >= min_columns and all(col != "" for col in columns[:2]):
            header_idx = i
            break

    if header_idx is None:
        raise ValueError("Could not detect valid CSV header row.")
    print(f"Detected delimiter: {repr(delimiter)}")
    print(f"Detected header row: {header_idx}")
    print(f"Header preview: {lines[header_idx]}")

    # Use pandas to read from the detected header row
    df = pd.read_csv(filepath, skiprows=header_idx, delimiter=delimiter)
    print(df[:10])
    return df
