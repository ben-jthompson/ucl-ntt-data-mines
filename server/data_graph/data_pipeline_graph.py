import os
from .data_pipeline_funcs import get_local_authority
from .cooling_feasibility import CoolingFeasibility
from .environmental_feasibility import EnvironmentalFeasibility
from .mine_feasibility import MineFeasibility
from ..session_state import SessionState 
import json   
from ..utils import cancellable_node

@cancellable_node
def start_node(state: SessionState) -> SessionState:
    state['current'] = 'region'
    return state

@cancellable_node
def region_node(state: SessionState) -> SessionState:
    state['region'] = get_local_authority(state['coords'], state['buffer'])
    state['current'] = 'mining'
    return state

@cancellable_node
def mining_node(state: SessionState) -> SessionState:
    mining = MineFeasibility(state['coords'], state['buffer'], state['client_id'])
    mining_sections = mining.run()
    state['data_report_sections'].extend(mining_sections)
    state['current'] = 'cooling'
    return state

@cancellable_node
def cooling_node(state: SessionState) -> SessionState:
    cooler = CoolingFeasibility(state['coords'], state['buffer'])
    # TODO: get outputs
    cooler_sections = cooler.run()
    state['data_report_sections'].extend(cooler_sections)
    state['current'] = 'environmental'
    return state

@cancellable_node
def environmental_node(state: SessionState) -> SessionState:
    environmental = EnvironmentalFeasibility(state['coords'], state['buffer'], state['client_id'])
    environmental_sections = environmental.run()
    state['data_report_sections'].extend(environmental_sections)
    state['current'] = 'data_bibliography'
    return state

@cancellable_node
def data_bibliography(state: SessionState) -> SessionState:
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    references = os.path.join(base_path, 'data/geojson', 'data_references.json')
    with open(references, "r") as f:
        metadata = json.load(f)
        for entry in metadata:
            state['bibliography'].append({'file_name': entry['file'], 'link': entry['link']})
    
    state['current'] = 'data_end'
    return state

