from typing import TypedDict, Dict
from langgraph.graph import StateGraph
from .data_pipeline_funcs import get_local_authority
from .cooling_feasibility import CoolingFeasibility

class DataPipelineState(TypedDict):
    coords: tuple
    buffer: int
    region: str
    suitability: Dict

    

def region_node(state: DataPipelineState) -> DataPipelineState:
    state['region'] = get_local_authority(state['coords'])
    return state

def cooling_node(state: DataPipelineState) -> DataPipelineState:
    cooler = CoolingFeasibility(state['coords'], state['buffer'])
    cooler.get_aquifer_status()

def build_data_pipeline_graph():
    graph = StateGraph(DataPipelineState)
    graph.add_node("region", region_node)
    graph.add_node("cooling", cooling_node)

    graph.set_entry_point("region")
    graph.add_edge("region", "cooling")

    pipeline = graph.compile()
    return pipeline

