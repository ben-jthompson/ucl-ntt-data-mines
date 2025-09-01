from .scraper import Scraper
from .querier import Querier
from .context_adder import ContextAdder
from .chroma_funcs import make_chroma_db
import shutil
import os
from langchain.tools import Tool
from langchain.agents import initialize_agent
from ..session_state import SessionState
from ..utils import cancellable_node, format_docs

@cancellable_node
def scrape_node(state: SessionState) -> SessionState:
    print("scraper")
    state["query"] = state["queries"][0]
    state['current'] = state['query']['topic']
    scraper = Scraper(state["location"], state['region'], state["query"], state["client_id"])
    state["docs"] = scraper.run()
    return state

@cancellable_node
def add_context_node(state: SessionState) -> SessionState:
    context_adder = ContextAdder(state["query"]['tag'], state["client_id"])
    context, references = context_adder.run()
    if context:
        state["docs"].extend(context)
    if references:
        state["bibliography"].extend(references)
    return state

@cancellable_node
def embed_node(state: SessionState) -> SessionState:
    state["retriever"] = make_chroma_db(state["docs"], state["location"])
    return state

@cancellable_node
def query_llm_node(state: SessionState) -> SessionState:
    querier = Querier(state["location"], state["region"], state["retriever"], state["queries"][0])
    state["retriever"] = querier.retriever
    current_q = querier.formulate_query()
    
    retriever_tool = Tool(
        name="query_vector_db",
        func=lambda x: format_docs(state["retriever"].invoke(x)),
        description="Search the vector DB with a reformulated query."
        "The results will include the document content and Redirect URL"
        ", the latter of which can be cited or added to the bibliography."
    )

    def add_to_bibliography(url: str):
        entry = {
            'file_name': state['query']['topic'],
            'link': url,
            'llm': True
        }
        # Only add if not already in bibliography
        if entry not in state['bibliography']:
            state['bibliography'].append(entry)
            return f"Added {url} to bibliography"
        else:
            return f"{url} already in bibliography"

    bibliography_tool = Tool(
        name="add_source_to_bibliography",
        func=add_to_bibliography,
        description="Add the cited document metadata to the bibliography."
        "Provide the redirect_url from the content that you used to provide the answer. "
        "Example: \"https://example.com/report.pdf\""
    )

    agent = initialize_agent(
        tools=[retriever_tool, bibliography_tool],
        llm=querier.llm,
        agent='zero-shot-react-description',
        max_iterations=50,
        max_execution_time=None,
        return_intermediate_steps=True,
        handle_parsing_errors=True
    )
    response = agent.invoke({'input': current_q})
    print("RESPONSE:", response['output'])
    state["report_sections"].append({'topic':state["query"]["topic"], 'explanation':response['output']})
    doc_folder = os.path.join(os.getcwd(), 'server/downloads', state['client_id'])
    if os.path.exists(doc_folder) and os.listdir(doc_folder):
        shutil.rmtree(doc_folder)

    return state

@cancellable_node
def reset_state_node(state: SessionState) -> SessionState:
    print('rst!')
    state["queries"] = state["queries"][1:]
    state['response'] = ''
    state['docs'] = []
    state['retriever'] = None
    return state

def queries_left(state: SessionState) -> str:
    print("Checking queries...", state["queries"])
    print("Bibliography: ", state['bibliography'])
    if len(state["queries"]) <= 1:
        print("dwr")
        return 'true'
    else:
        print("rst")
        return 'false'
