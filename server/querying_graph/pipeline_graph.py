from .scraper import Scraper
from .querier import Querier
from .context_adder import ContextAdder
from .chroma_funcs import make_chroma_db
from .utils import dict_to_document
import json
from langchain.tools import Tool
from langchain.agents import initialize_agent
from typing import TypedDict
from ..session_state import SessionState

def scrape_node(state: SessionState) -> SessionState:
    state["query"] = state["queries"][0]
    state["tag"] = state["tags"][0]
    state['current'] = state['query']
    scraper = Scraper(state["location"], state["query"], state["client_id"])
    state["docs"] = scraper.run()
    return state

def add_context_node(state: SessionState) -> SessionState:
    context_adder = ContextAdder(state["tag"], state["client_id"])
    context, references = context_adder.run()
    state["docs"].extend(context)
    state["bibliography"].extend(references)
    return state

def embed_node(state: SessionState) -> SessionState:
    state["retriever"] = make_chroma_db(state["docs"], state["location"])
    return state

def query_llm_node(state: SessionState) -> SessionState:
    querier = Querier(state["retriever"], state["queries"][0])
    state["retriever"] = querier.retriever
    current_q = querier.formulate_query()
    
    retriever_tool = Tool(
        name="query_vector_db",
        func=lambda x: state["retriever"].invoke(x),
        description="Search the vector DB with a reformulated query."
    )

    agent = initialize_agent(
        tools=[retriever_tool],
        llm=querier.llm,
        agent="chat-conversational-react-description",
        verbose=True
    )
    response = agent.run(current_q)
    print("RESPONSE:", response)
    state["report_sections"].append({'topic':state["query"]["topic"], 'explanation':response})

    return state

def reset_state_node(state: SessionState) -> SessionState:
    state["queries"] = state["queries"][1:]
    state["tags"] = state["tags"][1:]
    state['response'] = ''
    state['docs'] = []
    state['retriever'] = None
    return state

def queries_left(state: SessionState) -> str:
    if len(state["queries"]) == 1:
        return 'data_rewriter'
    else:
        return 'reset'
