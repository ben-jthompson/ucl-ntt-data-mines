from langgraph.graph import StateGraph
from typing import TypedDict, List, Dict, Tuple, Any, Optional
from .querying_graph.pipeline_graph import scrape_node, add_context_node, embed_node, query_llm_node, reset_state_node
from .data_graph.data_pipeline_graph import region_node, cooling_node, environmental_node, formatting_node
from .formatting_graph.formatter_pipeline_graph import text_compilation_node, pdf_creation_node, metadata_making_node
from collections.abc import Generator
from .session_state import SessionState


def build_session_graph():
    graph = StateGraph(SessionState)
    graph.add_node("region", region_node)
    graph.add_node("cooling", cooling_node)
    graph.add_node("environmental", environmental_node)
    graph.add_node("formatter", formatting_node)
    
    # graph.add_node("scrape", scrape_node)
    # graph.add_node("add_context", add_context_node)
    # graph.add_node("embed", embed_node)
    # graph.add_node("query_llm", query_llm_node)
    # graph.add_node("reset", reset_state_node)

    graph.add_node("compilation", text_compilation_node)
    graph.add_node("builder", pdf_creation_node)
    graph.add_node("metadata", metadata_making_node)

    graph.set_entry_point("region")
    graph.add_edge("region", "cooling")
    graph.add_edge("cooling", "environmental")
    graph.add_edge("environmental", "formatter")
    # graph.add_edge("formatter", "scrape")
    # graph.add_edge("scrape", "add_context")
    # graph.add_edge("add_context", "embed")
    # graph.add_edge("embed", "query_llm")
    # graph.add_conditional_edges("query_llm", "reset")
    graph.add_edge("formatter", "compilation")
    graph.add_edge("compilation", "builder")
    graph.add_edge("builder", "metadata")
    # graph.add_edge("reset", "scrape")

    return graph.compile()

# if __name__ == '__main__':
#     data_query_pipeline = build_data_pipeline_graph()
#     data_feasibility = data_query_pipeline.invoke({
#             "coords": [53.433331, -1.816667],
#             "buffer": 5000,
#             "region": 'Sheffield',
#             "suitability": [],
#             "report_sections": []
#         })
#     print(data_feasibility)

