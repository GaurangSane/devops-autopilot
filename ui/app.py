import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
import streamlit as st
import requests
import time
from datetime import datetime
from utils.tracing import get_project_stats

# ─────────────────────────────────────────
# Config
# ─────────────────────────────────────────
API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="DevOps Autopilot",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# Custom CSS — makes it look professional
# ─────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FF4B4B;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #888;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #1E1E1E;
        border-radius: 10px;
        padding: 1rem;
        border-left: 4px solid #FF4B4B;
    }
    .severity-critical { color: #FF4B4B; font-weight: 700; }
    .severity-high     { color: #FFA500; font-weight: 700; }
    .severity-medium   { color: #FFD700; font-weight: 700; }
    .severity-low      { color: #00CC00; font-weight: 700; }
    .status-completed  { color: #00CC00; }
    .status-processing { color: #FFA500; }
    .status-queued     { color: #888888; }
    .status-failed     { color: #FF4B4B; }
    .agent-section {
        background: #0E1117;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────
def check_api_health():
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        return r.status_code == 200
    except:
        return False


def submit_logs(raw_logs: str, submitted_by: str) -> dict:
    r = requests.post(
        f"{API_BASE}/analyze",
        json={"raw_logs": raw_logs, "submitted_by": submitted_by},
        timeout=10
    )
    return r.json()


def get_incident(incident_id: str) -> dict:
    r = requests.get(f"{API_BASE}/incidents/{incident_id}", timeout=10)
    return r.json()


def get_all_incidents() -> list:
    r = requests.get(f"{API_BASE}/incidents", timeout=10)
    return r.json()


def severity_badge(severity: str) -> str:
    colors = {
        "critical": "🔴",
        "high":     "🟠",
        "medium":   "🟡",
        "low":      "🟢"
    }
    return colors.get(severity, "⚪") if severity else "⚪"


def status_color(status: str) -> str:
    colors = {
        "completed":  "🟢",
        "processing": "🟡",
        "queued":     "⚪",
        "failed":     "🔴"
    }
    return colors.get(status, "⚪")


# ─────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚨 DevOps Autopilot")
    st.markdown("*Multi-Agent Incident Analysis*")
    st.divider()

    # API Health
    api_healthy = check_api_health()
    if api_healthy:
        st.success("✅ API Connected")
    else:
        st.error("❌ API Offline — start FastAPI first")
        st.code("uvicorn api.main:app --reload --port 8000")

    st.divider()

    # Navigation
    page = st.radio(
        "Navigation",
        ["🔍 Analyze Incident", "📋 Incident History", "📊 Dashboard"],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("**Stack**")
    st.markdown("""
    - 🧠 LangGraph Orchestration
    - 🦙 Groq LLaMA 3.3 70B
    - 🔍 Tavily Web Search
    - 🗄️ PostgreSQL
    - ⚡ FastAPI
    """)


# ─────────────────────────────────────────
# Page 1: Analyze Incident
# ─────────────────────────────────────────
if page == "🔍 Analyze Incident":

    st.markdown('<p class="main-header">🚨 DevOps Autopilot</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Paste your logs → 5 AI agents analyze, diagnose, and document the incident automatically</p>', unsafe_allow_html=True)

    # How it works
    with st.expander("⚙️ How it works", expanded=False):
        cols = st.columns(5)
        agents = [
            ("🔍", "Log Analyzer", "Extracts what broke, when, severity"),
            ("🔎", "Root Cause", "Finds WHY it broke, cascade chain"),
            ("🔧", "Fix Proposer", "Web search + concrete fix commands"),
            ("📋", "Runbook Writer", "Step-by-step 2am recovery guide"),
            ("📝", "Post Mortem", "Formal incident report for leadership"),
        ]
        for col, (icon, name, desc) in zip(cols, agents):
            with col:
                st.markdown(f"**{icon} {name}**")
                st.caption(desc)

    st.divider()

    # Input form
    col1, col2 = st.columns([3, 1])
    with col1:
        submitted_by = st.text_input(
            "Your name / team",
            placeholder="e.g. john-doe or sre-team",
            value="engineer"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        use_sample = st.button("Load Sample Logs", use_container_width=True)

    # Sample logs
    sample_logs = """2024-01-15 02:13:45 ERROR [payment-service] Connection pool exhausted: max_connections=10 reached
2024-01-15 02:13:45 ERROR [payment-service] Failed to acquire connection after 30000ms timeout
2024-01-15 02:13:46 ERROR [payment-service] Transaction rollback triggered for order_id=ORD-8821
2024-01-15 02:13:46 WARN  [api-gateway] Upstream payment-service returning 503
2024-01-15 02:13:47 ERROR [api-gateway] Circuit breaker OPEN for payment-service after 5 failures
2024-01-15 02:13:47 ERROR [order-service] Payment verification timeout for order_id=ORD-8821
2024-01-15 02:13:48 ERROR [order-service] Order failed, initiating compensation workflow
2024-01-15 02:13:50 FATAL [payment-service] Database connection lost: postgresql://payments-db:5432
2024-01-15 02:13:50 ERROR [payment-service] Health check failed - service marked as unhealthy
2024-01-15 02:13:55 WARN  [load-balancer] Removing payment-service instance from pool"""

    default_logs = sample_logs if use_sample else ""

    raw_logs = st.text_area(
        "Paste your logs here",
        value=default_logs,
        height=200,
        placeholder="Paste raw logs, stack traces, or error output here...",
        label_visibility="collapsed"
    )

    # Submit button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        submit = st.button(
            "🚀 Run Analysis",
            use_container_width=True,
            type="primary",
            disabled=not api_healthy
        )

    # ── Run analysis ──
    if submit:
        if not raw_logs.strip():
            st.error("Please paste some logs first.")
        else:
            with st.spinner("Submitting to pipeline..."):
                result = submit_logs(raw_logs, submitted_by)
                incident_id = result.get("incident_id")

            if not incident_id:
                st.error("Failed to submit. Is the API running?")
            else:
                st.success(f"✅ Incident created: **{incident_id}**")

                # Progress tracking
                st.markdown("### 🔄 Pipeline Running...")

                progress_bar = st.progress(0)
                status_text  = st.empty()
                agent_status = st.empty()

                agents_order = [
                    "log_analyzer",
                    "root_cause_analyzer",
                    "fix_proposer",
                    "runbook_writer",
                    "post_mortem_writer"
                ]

                agent_labels = {
                    "log_analyzer":       "🔍 Log Analyzer",
                    "root_cause_analyzer":"🔎 Root Cause Analyzer",
                    "fix_proposer":       "🔧 Fix Proposer (searching web...)",
                    "runbook_writer":     "📋 Runbook Writer",
                    "post_mortem_writer": "📝 Post Mortem Writer"
                }

                # Poll until completed
                max_wait = 300  # 5 minutes max
                elapsed  = 0
                interval = 3

                while elapsed < max_wait:
                    time.sleep(interval)
                    elapsed += interval

                    data = get_incident(incident_id)
                    status = data.get("status")
                    current = data.get("current_agent", "")

                    # Update progress
                    if status == "processing" and current in agents_order:
                        idx = agents_order.index(current)
                        progress = int(((idx + 1) / len(agents_order)) * 90)
                        progress_bar.progress(progress)
                        agent_status.info(f"Running: {agent_labels.get(current, current)}")

                    status_text.caption(f"Status: {status} | Elapsed: {elapsed}s")

                    if status == "completed":
                        progress_bar.progress(100)
                        agent_status.success("✅ All agents completed")
                        break
                    elif status == "failed":
                        st.error(f"Pipeline failed: {data.get('errors')}")
                        break

                # Show results
                if data.get("status") == "completed":
                    st.divider()
                    st.markdown("## 📊 Analysis Results")

                    # Top metrics
                    m1, m2, m3, m4 = st.columns(4)
                    with m1:
                        sev = data.get("severity", "unknown")
                        st.metric("Severity", f"{severity_badge(sev)} {sev.upper()}")
                    with m2:
                        services = data.get("affected_services", [])
                        st.metric("Services Affected", len(services) if services else 0)
                    with m3:
                        st.metric("Incident ID", incident_id)
                    with m4:
                        st.metric("Status", "✅ Resolved")

                    st.divider()

                    # Tabs for each agent output
                    tab1, tab2, tab3, tab4, tab5 = st.tabs([
                        "🔍 Log Analysis",
                        "🔎 Root Cause",
                        "🔧 Fixes",
                        "📋 Runbook",
                        "📝 Post Mortem"
                    ])

                    with tab1:
                        st.markdown("### Log Analysis")
                        st.markdown(data.get("log_analysis", "No output"))

                    with tab2:
                        st.markdown("### Root Cause Analysis")
                        st.markdown(data.get("root_cause", "No output"))

                    with tab3:
                        st.markdown("### Proposed Fixes")
                        st.markdown(data.get("fixes", "No output"))

                    with tab4:
                        st.markdown("### Runbook")
                        st.markdown(data.get("runbook", "No output"))
                        if data.get("runbook_path"):
                            with open(data["runbook_path"], "r") as f:
                                st.download_button(
                                    "⬇️ Download Runbook",
                                    f.read(),
                                    file_name=f"{incident_id}_runbook.md",
                                    mime="text/markdown"
                                )

                    with tab5:
                        st.markdown("### Post Mortem Report")
                        st.markdown(data.get("post_mortem", "No output"))
                        if data.get("post_mortem_path"):
                            with open(data["post_mortem_path"], "r") as f:
                                st.download_button(
                                    "⬇️ Download Post Mortem",
                                    f.read(),
                                    file_name=f"{incident_id}_postmortem.md",
                                    mime="text/markdown"
                                )


# ─────────────────────────────────────────
# Page 2: Incident History
# ─────────────────────────────────────────
elif page == "📋 Incident History":

    st.markdown("## 📋 Incident History")
    st.caption("All incidents stored in PostgreSQL — persists across restarts")

    if st.button("🔄 Refresh"):
        st.rerun()

    try:
        incidents = get_all_incidents()
    except:
        st.error("Cannot reach API. Make sure FastAPI is running.")
        incidents = []

    if not incidents:
        st.info("No incidents yet. Go to 'Analyze Incident' to create one.")
    else:
        for inc in incidents:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.markdown(f"**{inc['incident_id']}**")
                with col2:
                    sev = inc.get("severity") or "unknown"
                    st.markdown(f"{severity_badge(sev)} {sev}")
                with col3:
                    status = inc.get("status", "unknown")
                    st.markdown(f"{status_color(status)} {status}")
                with col4:
                    st.caption(inc.get("created_at", "")[:19])
                st.divider()


# ─────────────────────────────────────────
# Page 3: Dashboard
# ─────────────────────────────────────────
elif page == "📊 Dashboard":

    st.markdown("## 📊 System Dashboard")

    try:
        incidents = get_all_incidents()
        health    = requests.get(f"{API_BASE}/health").json()
    except:
        st.error("Cannot reach API.")
        st.stop()

    # Top metrics
    col1, col2, col3, col4 = st.columns(4)

    total     = len(incidents)
    completed = len([i for i in incidents if i["status"] == "completed"])
    failed    = len([i for i in incidents if i["status"] == "failed"])
    critical  = len([i for i in incidents if i.get("severity") == "critical"])

    with col1:
        st.metric("Total Incidents", total)
    with col2:
        st.metric("Completed", completed)
    with col3:
        st.metric("Failed", failed)
    with col4:
        st.metric("Critical", critical)

    st.divider()

    # Severity breakdown
    if incidents:
        st.markdown("### Severity Breakdown")
        severity_counts = {}
        for inc in incidents:
            sev = inc.get("severity") or "unknown"
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        cols = st.columns(len(severity_counts))
        for col, (sev, count) in zip(cols, severity_counts.items()):
            with col:
                st.metric(
                    f"{severity_badge(sev)} {sev.upper()}",
                    count
                )

    # Add this inside the Dashboard page section
    st.divider()
    st.markdown("### 🔬 LangSmith Observability")

    stats = get_project_stats()

    if stats:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Agent Runs", stats["total_runs"])
        with col2:
            st.metric("Avg Pipeline Latency", f"{stats['avg_latency']}s")
        with col3:
            st.metric("Error Rate", f"{stats['error_rate']}%")
        with col4:
            st.metric("Failed Runs", stats.get("errors",0))

        st.caption("📊 Full traces → [LangSmith Dashboard](https://smith.langchain.com)")
    else:
        st.info("LangSmith not configured or no runs yet.")             

    st.divider()
    st.markdown("### API Health")
    st.json(health)



