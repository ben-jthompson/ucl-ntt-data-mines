from ..session_state import SessionState
from .report_builder import ReportBuilder
import json
import os

def text_compilation_node(state: SessionState) -> SessionState:
    pass

def pdf_creation_node(state: SessionState) -> SessionState:
    report_builder = ReportBuilder(client_id=state['client_id'], location=state['location'], report_sections=[])
    report_builder.run()
    # TODO: get cursor to modify private vars eg. client id with an _
    metadata = report_builder.get_metadata()
    state["metadata"]["file_name"] = metadata['file_name']
    state["metadata"]["display_name"] = f'{state["location"]} Report {metadata["display_date"]}'
    state["metadata"]["upload_date"] = metadata['date'].isoformat()
    state["metadata"]["description"] = f'Report for location: {state["location"]}'
    state["metadata"]["coords"] = state["coords"]
    return state

def metadata_making_node(state: SessionState) -> SessionState:
    folder_path = os.path.join(os.getcwd(), "server/reports", state["client_id"])
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f'{state["metadata"]["file_name"]}.meta.json')
    with open(file_path, "w") as f:
        json.dump(state["metadata"], f, indent=2)

if __name__ == '__main__':
    metadata = pdf_creation_node({'location':'Adderbury', 'metadata': {}, 'coords': [53.1, -1.2], 'client_id': '123445'})   
    metadata_making_node(metadata) 