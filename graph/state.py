from typing import TypedDict, Optional, List

class AgentState(TypedDict):
    """
    Shared state that flows through every agent in the graph.
    Every agent reads from this and writes back to it.
    Think of it as the single source of truth for one incident.
    """
    raw_logs: str                      

    
    log_analysis: Optional[str]
    root_cause: Optional[str]            
    fixes: Optional[str]                 
    search_queries: Optional[List[str]]  
    runbook: Optional[str]               
    post_mortem: Optional[str]           

    severity: Optional[str]            
    affected_services: Optional[List[str]]
    incident_id: Optional[str]          

    runbook_path: Optional[str]
    post_mortem_path: Optional[str]

    
    errors: Optional[List[str]]         
    current_agent: Optional[str]        