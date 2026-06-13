from typing import TypedDict, Optional, List

class AgentState(TypedDict):
    # INPUT
    raw_logs:           str
    repo_url:           Optional[str]      # GitHub repo URL (optional)
    user_context:       Optional[str]      # Engineer's hypothesis (optional)

    # AGENT OUTPUTS
    log_analysis:       Optional[str]
    root_cause:         Optional[str]
    fixes:              Optional[str]
    github_analysis:    Optional[str]      # NEW — codebase-aware analysis
    runbook:            Optional[str]
    post_mortem:        Optional[str]

    # METADATA
    severity:           Optional[str]
    affected_services:  Optional[List[str]]
    incident_id:        Optional[str]
    search_queries:     Optional[List[str]]
    relevant_files:     Optional[List[str]]  # NEW — files GitHub agent found
    github_used:        Optional[bool]        # NEW — was GitHub provided?

    # FILE PATHS
    runbook_path:       Optional[str]
    post_mortem_path:   Optional[str]

    # ERROR TRACKING
    errors:             Optional[List[str]]
    current_agent:      Optional[str]