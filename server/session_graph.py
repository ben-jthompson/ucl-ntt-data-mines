from langgraph.graph import StateGraph
from typing import TypedDict, List, Dict
from .querying_graph.pipeline_graph import build_pipeline_graph
from .data_graph.data_pipeline_graph import build_data_pipeline_graph
from .data_graph.data_pipeline_funcs import get_local_authority


# state for all queries
class SessionState(TypedDict):
    client_id: str
    location: str
    region: List[Dict]
    coords: tuple
    buffer: int
    queries: List[Dict] 
    report_sections: List

def run_spatial_operations(state: SessionState) -> SessionState:
    state['region'] = get_local_authority(state['coords'], state['buffer'])
    data_query_pipeline = build_data_pipeline_graph()


def run_all_queries(state: SessionState) -> SessionState:
    query_pipeline = build_pipeline_graph()
    sections = []

    for q in state["queries"]:
        # handle geospatial queries
        
        pipeline_state = {
            "client_id": state["client_id"],
            "location": state["location"],
            "coords": state["coords"],
            "tag": state["tag"],
            "query": q,
            "docs": [],
            "retriever": None,
            "response": ""
        }
        final_state = query_pipeline.invoke(pipeline_state)
        # TODO add metadata to each response
        sections.append(final_state["response"])
    
    state["report_sections"].append(sections)
    return state

outer_graph = StateGraph(SessionState)
outer_graph.add_node("run_queries", run_all_queries)
outer_graph.set_entry_point("run_queries")
pipeline = outer_graph.compile()

# Run once for multiple queries
session_state = {
    "client_id": "123",
    "location": "NYC",
    "coords": (40.7128, -74.0060),
    "tag": "my-tag",
    "queries": ["first query", "second query", "third query"],
    "report_sections": []
}
final_report = pipeline.invoke(session_state)
print(final_report["report_sections"])
