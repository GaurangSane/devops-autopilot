import os
from dotenv import load_dotenv
load_dotenv()

# Must be set before langgraph/langchain imports
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")
os.environ["LANGCHAIN_API_KEY"]    = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"]    = os.getenv("LANGCHAIN_PROJECT", "devops-autopilot")

from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.nodes import (
    log_analyzer_node,
    root_cause_node,
    fix_proposer_node,
    github_agent_node,
    runbook_writer_node,
    post_mortem_node
)
from utils.logger import get_logger

log = get_logger("workflow")


def should_continue_after_log_analysis(state: AgentState) -> str:
    """
    Conditional edge after Agent 1.
    If log analysis failed — go to END.
    If severity is low — skip to post mortem directly.
    Otherwise — continue normal pipeline.
    """
   
    if state.get("errors"):
        print("\n⚠️  Errors detected — stopping pipeline")
        return "end"

   
    if state.get("severity") == "low":
        print("\n⚠️  Low severity — routing to post mortem directly")
        return "post_mortem"

   
    return "root_cause"


def should_continue_after_root_cause(state: AgentState) -> str:
    """
    Conditional edge after Agent 2.
    If failed — stop. Otherwise continue.
    """
    if state.get("errors"):
        return "end"
    return "fix_proposer"


def build_graph():
    graph = StateGraph(AgentState)

    # Add all nodes
    graph.add_node("log_analyzer",       log_analyzer_node)
    graph.add_node("root_cause_analyzer", root_cause_node)
    graph.add_node("fix_proposer",        fix_proposer_node)
    graph.add_node("github_agent",        github_agent_node)  # NEW
    graph.add_node("runbook_writer",      runbook_writer_node)
    graph.add_node("post_mortem_writer",  post_mortem_node)

    # Entry point
    graph.set_entry_point("log_analyzer")

    # Edges
    graph.add_conditional_edges(
        "log_analyzer",
        should_continue_after_log_analysis,
        {
            "root_cause": "root_cause_analyzer",
            "post_mortem": "post_mortem_writer",
            "end": END
        }
    )

    graph.add_conditional_edges(
        "root_cause_analyzer",
        should_continue_after_root_cause,
        {
            "fix_proposer": "fix_proposer",
            "end": END
        }
    )

    # Fix proposer → GitHub agent → Runbook
    graph.add_edge("fix_proposer",    "github_agent")   # NEW
    graph.add_edge("github_agent",    "runbook_writer") # NEW
    graph.add_edge("runbook_writer",  "post_mortem_writer")
    graph.add_edge("post_mortem_writer", END)

    compiled = graph.compile()
    log.info("Graph compiled successfully")
    return compiled


def run_graph(raw_logs: str, incident_id: str,
              repo_url: str = "", user_context: str = "") -> dict:
    graph = build_graph()

    initial_state = {
        "raw_logs":          raw_logs,
        "repo_url":          repo_url,          # NEW
        "user_context":      user_context,       # NEW
        "log_analysis":      None,
        "root_cause":        None,
        "fixes":             None,
        "github_analysis":   None,               # NEW
        "runbook":           None,
        "post_mortem":       None,
        "severity":          None,
        "affected_services": None,
        "incident_id":       incident_id,
        "search_queries":    None,
        "relevant_files":    None,               # NEW
        "github_used":       False,              # NEW
        "runbook_path":      None,
        "post_mortem_path":  None,
        "errors":            [],
        "current_agent":     None
    }

    config = {
        "tags":     ["production", "devops-autopilot"],
        "metadata": {"incident_id": incident_id}
    }

    final_state = graph.invoke(initial_state, config=config)
    return final_state

if __name__ == "__main__":
    graph = build_graph()

    with open("tests/sample_logs.txt", "r") as f:
        logs = f.read()

    initial_state = {
        "raw_logs": logs,
        "log_analysis": None,
        "root_cause": None,
        "fixes": None,
        "search_queries": None,
        "runbook": None,
        "post_mortem": None,
        "severity": None,
        "affected_services": None,
        "incident_id": None,
        "runbook_path": None,
        "post_mortem_path": None,
        "errors": [],
        "current_agent": None
    }

    print("\n" + "=" * 60)
    print("🚀 STARTING DEVOPS AUTOPILOT PIPELINE")
    print("=" * 60)


    final_state = graph.invoke(initial_state)

    print("\n" + "=" * 60)
    print("✅ PIPELINE COMPLETE")
    print("=" * 60)
    print(f"Incident ID    : {final_state['incident_id']}")
    print(f"Severity       : {final_state['severity']}")
    print(f"Services Hit   : {final_state['affected_services']}")
    print(f"Runbook saved  : {final_state['runbook_path']}")
    print(f"Post mortem    : {final_state['post_mortem_path']}")
    print(f"Errors         : {final_state['errors']}")
    print("=" * 60)