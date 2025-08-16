from typing import TypedDict, Dict
from langgraph.graph import StateGraph
from .data_pipeline_funcs import get_local_authority
from .cooling_feasibility import CoolingFeasibility
from .environmental_feasibility import EnvironmentalFeasibility
from ..session_state import SessionState    

def region_node(state: SessionState) -> SessionState:
    print('Moving to region node...')
    state['region'] = get_local_authority(state['coords'], state['buffer'])
    state['current'] = 'cooling'
    return state

def cooling_node(state: SessionState) -> SessionState:
    print('Moving to cooling node...')
    cooler = CoolingFeasibility(state['coords'], state['buffer'])
    # TODO: get outputs
    aquifer_dict = cooler.get_aquifer_status()
    state['suitability'].append(aquifer_dict)
    state['current'] = 'environmental'
    return state

def environmental_node(state: SessionState) -> SessionState:
    print('Moving to environmental node...')
    environmental = EnvironmentalFeasibility(state['coords'], state['buffer'])
    flood_risk_dict = environmental.get_flood_risk()
    state['suitability'].append(flood_risk_dict)
    state['current'] = 'formatting'
    return state

def formatting_node(state: SessionState) -> SessionState:
    risk_dict = {
        'High': '#FF0000',
        'Moderate': '#FFA500',
        'Low': '#008000'
    }
    suitability_dict = {
        'High': '#008000',
        'Medium': '#FFA500',
        'Low': '#FF0000'
    }
    for dictionary in state['suitability']:
        entry = [f"*{dictionary['topic']}*: {dictionary['explanation']}"]       
        if 'risk' in dictionary.keys():
            entry.append(risk_dict[dictionary['risk']])
        else:
            entry.append(suitability_dict[dictionary['suitability']])
    
    state['report_sections'].append({'Data Queries': entry})
    state['current'] = 'data_end'
    return state
