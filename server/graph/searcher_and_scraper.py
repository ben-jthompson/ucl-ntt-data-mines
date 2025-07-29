from typing import TypedDict, List
import requests
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from newspaper import Article
from langchain.schema import Document
from bs4 import BeautifulSoup
from chroma_funcs import url_suitability_scoring
from urllib.parse import urljoin
from utils import download_file, document_to_dict, dict_to_document, extract_text_from_source
from error_handler_class import ErrorHandler

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
search_api_key = os.getenv("SEARCH_API_KEY")

llm = ChatOpenAI(
    model="gpt-4o-mini", temperature = 0, api_key=api_key) 

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
    "count": 20,
    "country": "GB"
  },
).json()
    
    # limit api calls
    with open('20output.json', "w", encoding="utf-8") as f:
        json.dump(response['web'], f, indent=4, ensure_ascii=False)

    return response['web']

# embed the search results from api
def scrape_search_results(driver: webdriver.Chrome, query: str, search_results = None) -> List[Document]:
    results = []
    if not search_results:
        with open ('20output.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    else:
        data = search_results

    for result in data['results']:
        try:
            # get text from results page
            url = result['url']
            article = Article(url)
            article.download()
            article.parse()
            doc = Document(page_content=article.text, metadata={'url': url, 'redirect_url': url})
            results.append(doc)
        except Exception as e:
            error_handler = ErrorHandler(url, e)
            error_handler.run()
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
        
        if len(soup_links) > 0:
            suitable_urls = url_suitability_scoring(soup_links, query)
            for url in suitable_urls:
                results.append(url)
    
    # turn to json format and save
    with open("scraped_results.json", "w", encoding="utf-8") as f:
        json.dump([document_to_dict(doc) for doc in results], f, indent=4, ensure_ascii=False)

    return results

def download_and_parse_reports(results: List[Document]) -> List[Document]:
    for result in results:
        # print('Result is:', result)
        if result.metadata['redirect_url'] and (result.metadata['redirect_url'].endswith('.pdf') or result.metadata['redirect_url'].endswith('.csv')):
            print('\nAttempting to download result:\n')
            download_file(result.metadata['redirect_url'])
            extract_text_from_source(result.metadata['redirect_url'], result)
    return results

# scrape the text of the links retrieved
def get_scraped_results(results: List[Document]) -> List[Document]:
    # keep track of sites visited so that duplicate text is limited
    link_set= set()
    results_set = []
    # first, add content for the pdf/csvs
    results = download_and_parse_reports(results)
    for result in (results):
        # if page has already been scraped but is a separate result, then delete the result from the list to avoid duplicates
        if result.metadata['redirect_url'] in link_set:
            continue
        # if the page has already been scraped in initial scraping, or has been scraped as a pdf/csv continue
        elif result.metadata['redirect_url'] == result.metadata['url'] or result.metadata['redirect_url'].endswith('.pdf') or result.metadata['redirect_url'].endswith('.csv'):
            # print(f"Site {result.metadata['redirect_url']} has been scraped")
            results_set.append(result)
        else:
            # print(f"Scraping site {result.metadata['redirect_url']}")
            article = Article(result.metadata['redirect_url'])
            article.download()
            article.parse()
            result.page_content = article.text
            link_set.add(result.metadata['redirect_url'])
            results_set.append(result)
        
    return results_set

# initial prompt
# def retrieve_documents(state: FeasibilityState) -> FeasibilityState:
#     system_prompt = """
# You are an intelligent AI assistant who answers questions about data centre feasibility in coal mines.
# If you need to look up some information before asking a follow up question, you are allowed to do that!
# Please always cite the specific parts of the sources you use in your answers.
# """
#     messages = [SystemMessage(content=system_prompt), HumanMessage(content=f'Please conduct analysis for the location: {state["location"]}')]
    
#     location = state['location']
#     # print(f"Searching for documents on: {location}")
#     docs = [
#         f"Report on underground cooling systems in {location}",
#         f"Relevant local authorities near {location}",
#         f"Geotechnical analysis of mines in {location}"
#     ]
#     answer = llm.invoke(messages)
#     return {**state, "answer": answer}

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
    # search_results = run_search_api("Nottinghamshire Report Mine Reuse Heat Water")
    # driver = setup_driver()
    # results = scrape_search_results(query='Nottinghamshire Report Mine Reuse Heat Water', driver=driver)
    with open("scraped_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        results = [dict_to_document(d) for d in data]
    documents = get_scraped_results(results)
    output = [document for document in documents if len(document.page_content)<50]
    print(output)
    # result = app.invoke({'location': user_location, 'documents': [], 'answer': '', 'messages': []})
    # print("\n✅ Final output:")
    # print(result)
