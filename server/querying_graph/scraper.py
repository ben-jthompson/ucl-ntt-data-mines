from typing import List
import os
import json
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from newspaper import Article
from langchain.schema import Document
from langchain_community.tools import DuckDuckGoSearchResults
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from server.querying_graph.chroma_funcs import url_suitability_scoring
from server.querying_graph.utils import download_file, extract_from_source, document_to_dict, dict_to_document, detect_file_type, extract_ms_office_link
from server.querying_graph.error_handler_class import ErrorHandler

class Scraper:
    def __init__(self, location: str, query: str, client_id: str):
        load_dotenv()
        self.location = location
        self.query = query
        self.client_id = client_id
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.search_api_key = os.getenv("SEARCH_API_KEY")
        self.driver = self._setup_driver()
        self.documents: List[Document] = []
        self.unique = {'.pdf', '.csv', '.json', '.geojson' }
        self.ms_unique = {'.docx', '.doc', '.xlsx', '.xls'}

    def _setup_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def run_search(self) -> dict:
        # TODO brave api start
        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "x-subscription-token": self.search_api_key
            },
            params={
                "q": self.query,
                "count": 20,
                "country": "GB"
            },
        ).json()
        # TODO brave api end

        # TODO cached response
        # with open('outputs/ddgoutput.json', "w", encoding="utf-8") as f:
        #     json.dump(response, f, indent=4, ensure_ascii=False)
        # TODO cached response end

        return response

    def scrape_results(self, search_results):
        results = []

        for result in search_results['results']:
            url = result.get('url')
            if not url: 
                continue
            file_type = detect_file_type(url)
            # if file is a ms office file, extract the actual url from the ms viewer application url
            if file_type in self.ms_unique:
                ms_url = extract_ms_office_link(url)
                results.append(Document(page_content=result.get('title'), metadata={'url': ms_url, 'redirect_url': ms_url, 'file_type': file_type}))
                continue
            elif file_type in self.unique:
                results.append(Document(page_content=result.get('title'), metadata={'url': url, 'redirect_url': url, 'file_type': file_type}))
                continue
            
            # scrape webpages (remaining files)
            try:
                article = Article(url)
                article.download()
                article.parse()
                results.append(Document(page_content=article.text, metadata={'url': url, 'redirect_url': url, 'file_type': 'web'}))
            except Exception as e:
                error_handler = ErrorHandler(url=url, error=e)
                error_handler.run()

            # use selenium to get links within webpage
            try:
                self.driver.get(url)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                # TODO: move this outside of  for loop
                soup_links = []
                seen_links = set()

                for a in soup.find_all('a', href=True):
                    href = a['href'].strip()
                    if not href or href.startswith('#'):
                        continue
                    redir_url = urljoin(base=url, url=href)
                    if redir_url in seen_links:
                        continue
                    seen_links.add(redir_url)
                    soup_links.append(Document(page_content=a.get_text(strip=True), metadata={'redirect_url': redir_url, 'url': url, 'file_type': 'soup'}))
                # TODO: move outisde of for loop to prevent duplicate information
                if soup_links:
                    suitable_urls = url_suitability_scoring(soup_links, self.query)
                    # TODO: scrape/download these
                    results.extend(suitable_urls)

            except Exception as e:
                print(f"Failed to load {url}: {e}")

        self.documents = results

    def download_and_parse_reports(self):
        for doc in self.documents:
            url = doc.metadata.get('redirect_url', '')
            file_type = doc.metadata.get('file_type')
            # if the file is identified as non-conventional file type
            if file_type in self.unique or file_type in self.ms_unique:
                try:
                    print(f"Downloading {url}")
                    download_file(url, self.client_id)
                    extract_from_source(url, doc)
                except Exception as e:
                    print(f"Failed to download/parse {url}: {e}")

    def finalise_documents(self):
        link_set = set()
        filtered_docs = []

        for doc in self.documents:
            redir_url = doc.metadata.get('redirect_url', '')
            base_url = doc.metadata.get('url', '')
            file_type = doc.metadata.get('file_type', '')

            if redir_url in link_set:
                continue
            
            # if info has already been scraped, no need to rescrape
            if redir_url == base_url or file_type in self.unique or file_type in self.ms_unique:
                filtered_docs.append(doc)
            else:
                try:
                    article = Article(redir_url)
                    article.download()
                    article.parse()
                    doc.page_content = article.text
                    filtered_docs.append(doc)
                except Exception as e:
                    print(f"Failed to scrape {redir_url}: {e}")
                    print('Document is ', doc)
                    continue

            link_set.add(redir_url)

        self.documents = filtered_docs

    def save_documents(self, filename="final_results.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([document_to_dict(doc) for doc in self.documents], f, indent=4, ensure_ascii=False)

    def run(self):
        # TODO temp to bypass api
        search_results = self.run_search()
        # TODO temp end
        self.scrape_results(search_results)
        self.download_and_parse_reports()
        self.finalise_documents()
        self.save_documents()
        return self.documents

if __name__ == '__main__':
    scraper = Scraper('Nottingham', "Nottinghamshire Report Mine Reuse Heat Water")
    docs = scraper.run()
    # print(docs)