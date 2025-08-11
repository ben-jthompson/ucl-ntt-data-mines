from .scraper import Scraper
from .querier import Querier
from .context_adder import ContextAdder
from .chroma_funcs import make_chroma_db
from .utils import dict_to_document
import json
from typing import TypedDict
from langgraph.graph import StateGraph

class PipelineState(TypedDict):
    location: str
    query: str
    tag: str
    region: str
    client_id: str
    coords: tuple
    docs: list
    retriever: object
    response: str



def scrape_node(state: PipelineState) -> PipelineState:
    scraper = Scraper(state["location"], state["query"])
    state["docs"] = scraper.run()
    return state

def add_context_node(state: PipelineState) -> PipelineState:
    context_adder = ContextAdder(state["tag"], state["client_id"])
    context = context_adder.run()
    state["docs"].append(context)
    return state

def embed_node(state: PipelineState) -> PipelineState:
    state["retriever"] = make_chroma_db(state["docs"], state["location"])
    return state

def query_llm_node(state: PipelineState) -> PipelineState:
    querier = Querier(state["retriever"], state["query"])
    state["response"] = querier.run()
    return state

def build_pipeline_graph():
    graph = StateGraph(PipelineState)
    graph.add_node("scrape", scrape_node)
    graph.add_node("add_context", add_context_node)
    graph.add_node("embed", embed_node)
    graph.add_node("query_llm", query_llm_node)

    graph.set_entry_point("scrape")
    graph.add_edge("scrape", "add_context")
    graph.add_edge("add_context", "embed")
    graph.add_edge("embed", "query_llm")

    pipeline = graph.compile()
    return pipeline

# Run for a list of queries
# results = []
# for q in queries:
#     state = {
#         "location": "NYC",
#         "query": q,
#         "tag": "some-tag",
#         "client_id": "123",
#         "coords": (40.7128, -74.0060),
#         "docs": [],
#         "retriever": None,
#         "response": ""
#     }
#     final_state = pipeline.invoke(state)
#     results.append(final_state["response"])
