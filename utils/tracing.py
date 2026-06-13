from langsmith import Client
from dotenv import load_dotenv
from utils.logger import get_logger
import os

load_dotenv()
log = get_logger("tracing")

def get_langsmith_client():
    """
    Returns LangSmith client for manual trace operations.
    Auto-tracing happens via environment variables —
    this client is for explicit operations like
    fetching run data or adding feedback.
    """
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        log.warning("LANGCHAIN_API_KEY not set — tracing disabled")
        return None
    return Client(api_key=api_key)


def get_project_stats():
    client = get_langsmith_client()
    if not client:
        return None

    try:
        project_name = os.getenv("LANGCHAIN_PROJECT", "devops-autopilot")

        # No run_type filter — get everything
        runs = list(client.list_runs(
            project_name=project_name,
            limit=100
        ))

        print(f"[LangSmith] Found {len(runs)} runs in project '{project_name}'")

        if not runs:
            return {
                "total_runs":  0,
                "avg_latency": 0,
                "error_rate":  0,
                "errors":      0
            }

        total     = len(runs)
        errors    = len([r for r in runs if r.error])
        latencies = []

        for r in runs:
            try:
                if r.end_time and r.start_time:
                    # Safe datetime subtraction
                    delta = r.end_time - r.start_time
                    latencies.append(abs(delta.total_seconds()))
            except Exception:
                continue

        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        error_rate  = (errors / total * 100) if total else 0

        return {
            "total_runs":  total,
            "avg_latency": round(avg_latency, 2),
            "error_rate":  round(error_rate, 2),
            "errors":      errors
        }

    except Exception as e:
        log.error(f"LangSmith stats failed: {e}")
        print(f"[LangSmith ERROR] {e}")
        return None

def add_feedback(run_id: str, score: int, comment: str = ""):
    """
    Adds human feedback to a LangSmith run.
    Score: 1 = good, 0 = bad
    This is how you build evaluation datasets over time.
    """
    client = get_langsmith_client()
    if not client:
        return False

    try:
        client.create_feedback(
            run_id=run_id,
            key="user_rating",
            score=score,
            comment=comment
        )
        log.info(f"Feedback added to run {run_id}: score={score}")
        return True
    except Exception as e:
        log.error(f"Failed to add feedback: {e}")
        return False