from agents.log_analyzer_1 import analyze_logs
from agents.root_cause_2 import log_root_analyze
from agents.fix_proposer_3 import poposes_fixes
from agents.runbook_writer_4 import write_runbook, save_runbook
from agents.post_mortem_5 import write_post_mortem, save_post_mortem
from graph.state import AgentState
from datetime import datetime
import uuid
import re
from utils.logger import get_logger

log = get_logger("nodes")

def generate_incident_id() -> str:
    """Generates a unique incident ID like INC-20260605-A3F2"""
    date = datetime.now().strftime("%Y%m%d")
    short_id = str(uuid.uuid4())[:4].upper()
    return f"INC-{date}-{short_id}"


def extract_severity(log_analysis: str) -> str:
    """
    Pulls severity from Agent 1 output.
    Defaults to 'high' if not found.
    """
    analysis_lower = log_analysis.lower()
    if "critical" in analysis_lower:
        return "critical"
    elif "high" in analysis_lower:
        return "high"
    elif "medium" in analysis_lower:
        return "medium"
    else:
        return "low"


def extract_services(log_analysis: str) -> list:
    """
    Pulls affected services list from Agent 1 output.
    """
    services = []
    lines = log_analysis.split('\n')
    in_services_section = False

    for line in lines:
        if "AFFECTED SERVICES" in line.upper():
            in_services_section = True
            continue
        if in_services_section:
            if line.strip().startswith('-') and line.strip().endswith(':'):
                break
            cleaned = re.sub(r'^[\-\*\d\.\s]+', '', line).strip()
            if cleaned:
                services.append(cleaned)

    return services if services else ["unknown"]


def log_analyzer_node(state: AgentState) -> dict:
    print("\n🔍 [Node 1] Running Log Analyzer...")

    try:
        result = analyze_logs(state["raw_logs"])
        severity = extract_severity(result)
        services = extract_services(result)
        incident_id = generate_incident_id()

        print(f"  ✅ Severity detected: {severity}")
        print(f"  ✅ Services affected: {services}")
        print(f"  ✅ Incident ID: {incident_id}")

        return {
            "log_analysis": result,
            "severity": severity,
            "affected_services": services,
            "incident_id": incident_id,
            "current_agent": "log_analyzer",
            "errors": []
        }

    except Exception as e:
        print(f"  ❌ Log Analyzer failed: {e}")
        return {
            "errors": [f"log_analyzer failed: {str(e)}"],
            "current_agent": "log_analyzer"
        }


def root_cause_node(state: AgentState) -> dict:
    print("\n🔎 [Node 2] Running Root Cause Analyzer...")

    try:
        result = log_root_analyze(state["log_analysis"])
        print("  ✅ Root cause identified")

        return {
            "root_cause": result,
            "current_agent": "root_cause_analyzer"
        }

    except Exception as e:
        print(f"  ❌ Root Cause Analyzer failed: {e}")
        return {
            "errors": state.get("errors", []) + [f"root_cause failed: {str(e)}"],
            "current_agent": "root_cause_analyzer"
        }


def fix_proposer_node(state: AgentState) -> dict:
    print("\n🔧 [Node 3] Running Fix Proposer (with web search)...")

    try:
        result = poposes_fixes(state["root_cause"])
        print("  ✅ Fixes proposed")

        return {
            "fixes": result["fixes"],
            "search_queries": result["queries"],
            "current_agent": "fix_proposer"
        }

    except Exception as e:
        print(f"  ❌ Fix Proposer failed: {e}")
        return {
            "errors": state.get("errors", []) + [f"fix_proposer failed: {str(e)}"],
            "current_agent": "fix_proposer"
        }


def runbook_writer_node(state: AgentState) -> dict:
    print("\n📋 [Node 4] Running Runbook Writer...")

    try:
        result = write_runbook(
            state["log_analysis"],
            state["root_cause"],
            state["fixes"]
        )


        path = save_runbook(
            result,
            f"runbook/runbook_{state['incident_id']}.md"
        )

        print(f"  ✅ Runbook saved to: {path}")

        return {
            "runbook": result,
            "runbook_path": path,
            "current_agent": "runbook_writer"
        }

    except Exception as e:
        print(f"  ❌ Runbook Writer failed: {e}")
        return {
            "errors": state.get("errors", []) + [f"runbook_writer failed: {str(e)}"],
            "current_agent": "runbook_writer"
        }


def post_mortem_node(state: AgentState) -> dict:
    print("\n📝 [Node 5] Running Post Mortem Writer...")

    try:
        result = write_post_mortem(
            state["log_analysis"],
            state["root_cause"],
            state["fixes"],
            state["runbook"]
        )

        path = save_post_mortem(
            result,
            f"post_mortems/postmortem_{state['incident_id']}.md"
        )

        print(f"  ✅ Post mortem saved to: {path}")

        return {
            "post_mortem": result,
            "post_mortem_path": path,
            "current_agent": "post_mortem_writer"
        }

    except Exception as e:
        print(f"  ❌ Post Mortem Writer failed: {e}")
        return {
            "errors": state.get("errors", []) + [f"post_mortem failed: {str(e)}"],
            "current_agent": "post_mortem_writer"
        }
    
from agents.github_agent import analyze_with_github

def github_agent_node(state: AgentState) -> dict:
    """
    Optional node — only runs if user provided a repo URL.
    Fetches source code and gives line-specific fixes.
    """
    repo_url = state.get("repo_url", "").strip()

    # Skip if no repo provided
    if not repo_url:
        log.info("[Node: GitHub] No repo URL provided — skipping")
        return {
            "github_analysis": None,
            "github_used": False,
            "current_agent": "github_agent"
        }

    log.info(f"[Node: GitHub] Analyzing repo: {repo_url}")

    try:
        result = analyze_with_github(
            root_cause=state.get("root_cause", ""),
            affected_services=state.get("affected_services", []),
            repo_url=repo_url,
            user_context=state.get("user_context", "")
        )

        return {
            "github_analysis":  result["code_analysis"],
            "relevant_files":   result["repo_data"]["relevant_files"],
            "github_used":      result["github_used"],
            "current_agent":    "github_agent"
        }

    except Exception as e:
        log.error(f"GitHub agent failed: {e}")
        return {
            "github_analysis": f"GitHub analysis failed: {str(e)}",
            "github_used":     False,
            "errors": state.get("errors", []) + [f"github_agent: {str(e)}"],
            "current_agent":   "github_agent"
        }    