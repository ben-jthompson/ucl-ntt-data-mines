from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from typing import TypedDict, List, Union
import requests
import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from newspaper import Article
from langchain.schema import Document
from bs4 import BeautifulSoup
from chroma_funcs import url_suitability_scoring
from urllib.parse import urljoin
from utils import download_file

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
search_api_key = os.getenv("SEARCH_API_KEY")

llm = ChatOpenAI(
    model="gpt-4o", temperature = 0, api_key=api_key) 

# -- Define input/output schema for state --
class FeasibilityState(TypedDict):
    location: str
    documents: List[str]
    answer: str

# search query function
def run_search_api(query):
    response = requests.get(
  "https://api.search.brave.com/res/v1/web/search",
  headers={
    "Accept": "application/json",
    "Accept-Encoding": "gzip",
    "x-subscription-token": search_api_key
  },
  params={
    "q": query,
    "count": 5,
    "country": "GB"
  },
).json()
    
    # limit api calls
    with open('output.json', "w", encoding="utf-8") as f:
        json.dump(response['web'], f, indent=4, ensure_ascii=False)

    return response['web']['results']

# embed the search results from api
def scrape_search_results(driver: webdriver.Chrome, query: str, results = None):
    with open ('output.json', 'r', encoding='utf-8') as file:
            results = []
            data = json.load(file)
            for result in data['results']:
                try:
                    # get text from results page
                    url = result['url']
                    article = Article(url)
                    article.download()
                    article.parse()
                    doc = Document(page_content=article.text, metadata={'url': url, 'redirect_url': None})
                    results.append(doc)
                except Exception as e:
                    print(f"Failed to parse {url}: {e}")
                    continue

                # find the links within the page
                try:
                    driver.get(url)
                except Exception as e:
                    print(f"Failed to load {url}: {e}")
                    continue  
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                soup_links = []
                links = {}
                for a in soup.find_all('a', href=True):
                    if a['href'].strip().startswith('#') or not a['href'].strip():
                        continue
                    else:
                        redir_url = urljoin(base=url, url=a['href'].strip())
                        if redir_url in links:
                            continue
                        else:
                            soup_links.append(Document(page_content=a.get_text(strip=True), metadata={'redirect_url': redir_url, 'url': url}))
                
                suitable_urls = url_suitability_scoring(soup_links, query)
                for url in suitable_urls:
                    results.append(url)

    return results

def download_and_embed_reports(results: List[Document]):
    for result in results:
        print('Result is: ', result)
        if result.metadata['redirect_url'] and (result.metadata['redirect_url'].endswith('.pdf') or result.metadata['redirect_url'].endswith('.csv')):
            print('\nAttempting to download result:\n')
            download_file(result.metadata['redirect_url'])

# initial prompt
def retrieve_documents(state: FeasibilityState) -> FeasibilityState:
    system_prompt = """
You are an intelligent AI assistant who answers questions about data centre feasibility in coal mines.
If you need to look up some information before asking a follow up question, you are allowed to do that!
Please always cite the specific parts of the sources you use in your answers.
"""
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=f'Please conduct analysis for the location: {state["location"]}')]
    
    location = state['location']
    # print(f"Searching for documents on: {location}")
    docs = [
        f"Report on underground cooling systems in {location}",
        f"Relevant local authorities near {location}",
        f"Geotechnical analysis of mines in {location}"
    ]
    answer = llm.invoke(messages)
    return {**state, "answer": answer}

# setup driver for scraping
def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# find documents for rag pipeline via scraping
def find_relevant_docs(state: FeasibilityState) -> FeasibilityState:
    pass



# def summarise_documents(state: FeasibilityState) -> FeasibilityState:
#     print(f"Summarising documents for: {state['location']}")
#     # answer = f"Based on {len(state['documents'])} documents, {state['location']} shows moderate feasibility for a mine-based data centre."
#     return state

# -- Entry point node --
# def start_node(location: str) -> FeasibilityState:
#     return {"location": location, "documents": [], "answer": ""}

# # -- Build LangGraph workflow --
# graph = StateGraph(FeasibilityState)
# graph.add_node("retrieve_docs", RunnableLambda(retrieve_documents))
# graph.add_node("summarize", RunnableLambda(summarise_documents))

# # -- Edges between steps --
# graph.set_entry_point("retrieve_docs")
# graph.add_edge("retrieve_docs", "summarize")
# graph.add_edge("summarize", END)

# # -- Compile and use --
# app = graph.compile()

if __name__ == "__main__":
    # user_location = "Nottingham, UK"
    # result = run_search_api("Nottinghamshire Local Council Spending Reprot")
    driver = setup_driver()
    results = scrape_search_results(results=None, query='Nottinghamshire Council Spending Information 2025', driver=driver)
    download_and_embed_reports(results)
    # result = app.invoke({'location': user_location, 'documents': [], 'answer': '', 'messages': []})
    # print("\n✅ Final output:")
    # print(result)
