from typing import TypedDict, Dict, Optional, Tuple, List, Any

class SessionState(TypedDict, total=False):
    # session level
    current: Optional[str]
    client_id: Optional[str]
    location: Optional[str]
    coords: Optional[Tuple[float, float]]
    buffer: Optional[int]
    report_sections: List[Any]

    # Spatial data phase
    region: Optional[Any]  
    suitability: List[Any]

    # Querying phase
    queries: List[Dict] 
    query: Dict            
    tags: Optional[str]
    tag: str              
    docs: List[Any]
    retriever: Optional[Any]
    response: Optional[str]

