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

from server.graph.chroma_funcs import url_suitability_scoring
from server.graph.utils import download_file, extract_text_from_source, document_to_dict, dict_to_document
from server.graph.error_handler_class import ErrorHandler

class Scraper:
    def __init__(self, location: str, query: str):
        load_dotenv()
        self.location = location
        self.query = query
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.search_api_key = os.getenv("SEARCH_API_KEY")
        self.driver = self._setup_driver()
        self.documents: List[Document] = []

    def _setup_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def run_search(self) -> dict:
        # TODO brave api start
        # response = requests.get(
        #     "https://api.search.brave.com/res/v1/web/search",
        #     headers={
        #         "Accept": "application/json",
        #         "Accept-Encoding": "gzip",
        #         "x-subscription-token": self.search_api_key
        #     },
        #     params={
        #         "q": self.query,
        #         "count": 20,
        #         "country": "GB"
        #     },
        # ).json()
        # TODO brave api end

        # TODO free search api
        ddg = DuckDuckGoSearchResults()
        response = ddg.invoke(self.query)
        # TODO free search end

        # TODO cached response
        with open('outputs/ddgoutput.json', "w", encoding="utf-8") as f:
            json.dump(response, f, indent=4, ensure_ascii=False)
        # TODO cached response end

        return response

    def scrape_results(self, search_results=None):
        results = []
        if not search_results:
            with open('outputs/20output.json', 'r', encoding='utf-8') as file:
                search_results = json.load(file)

        for result in search_results['results']:
            url = result.get('url')
            if not url or url.endswith('pdf') or url.endswith('csv'):
                continue

            try:
                article = Article(url)
                article.download()
                article.parse()
                results.append(Document(page_content=article.text, metadata={'url': url, 'redirect_url': url}))
            except Exception as e:
                error_handler = ErrorHandler(url=url, error=e)
                error_handler.run()

            # Selenium parse internal links
            try:
                self.driver.get(url)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
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
                    soup_links.append(Document(page_content=a.get_text(strip=True), metadata={'redirect_url': redir_url, 'url': url}))

                if soup_links:
                    suitable_urls = url_suitability_scoring(soup_links, self.query)
                    results.extend(suitable_urls)

            except Exception as e:
                print(f"Failed to load {url}: {e}")

        self.documents = results

    def download_and_parse_reports(self):
        for doc in self.documents:
            url = doc.metadata.get('redirect_url', '')
            if url.endswith('.pdf') or url.endswith('.csv'):
                try:
                    print(f"Downloading {url}")
                    download_file(url)
                    extract_text_from_source(url, doc)
                except Exception as e:
                    print(f"Failed to download/parse {url}: {e}")

    def finalise_documents(self):
        link_set = set()
        filtered_docs = []

        for doc in self.documents:
            redir_url = doc.metadata.get('redirect_url', '')
            base_url = doc.metadata.get('url', '')

            if redir_url in link_set:
                continue

            if redir_url == base_url or redir_url.endswith('.pdf') or redir_url.endswith('.csv'):
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
                    continue

            link_set.add(redir_url)

        self.documents = filtered_docs

    def save_documents(self, filename="final_results.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([document_to_dict(doc) for doc in self.documents], f, indent=4, ensure_ascii=False)

    def run(self):
        # TODO temp to bypass api
        # search_results = self.run_search()
        # TODO temp end
        self.scrape_results()
        self.download_and_parse_reports()
        self.finalise_documents()
        self.save_documents()
        return self.documents

if __name__ == '__main__':
    scraper = Scraper('Nottingham', "Nottinghamshire Report Mine Reuse Heat Water")
    docs = scraper.run()
    # print(docs)