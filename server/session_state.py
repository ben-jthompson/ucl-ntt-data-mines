from typing import TypedDict, Dict, Optional, Tuple, List, Any
from threading import Event

class SessionState(TypedDict, total=False):
    # session level
    current: Optional[str]
    client_id: Optional[str]
    stop_event: Optional[Event]
    location: Optional[str]
    coords: Optional[Tuple[float, float]]
    buffer: Optional[int]
    report_sections: List[Any]
    bibliography: List[Dict]

    # Spatial data phase
    region: Optional[Any]  
    data_report_sections: List[Any]

    # Querying phase
    queries: List[Dict] 
    query: Dict
    tags: Optional[str]
    tag: str              
    docs: List[Any]
    retriever: Optional[Any]
    response: Optional[str]

    # Report phase
    metadata: Dict

