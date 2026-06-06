from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
from database.models import Incident, get_session, init_db
from sqlalchemy.orm import Session

from graph.workflow import build_graph


# ─────────────────────────────────────────
# App Setup
# ─────────────────────────────────────────
app = FastAPI(
    title="DevOps Autopilot API",
    description="Multi-agent system for automated incident analysis",
    version="1.0.0"
)

@app.on_event("startup")
def startup():
    init_db()
    print("✅ Database initialized")

# Allow Streamlit to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Build graph once at startup — not on every request
graph = build_graph()




# ─────────────────────────────────────────
# Request / Response Models
# ─────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    """What the client sends us"""
    raw_logs: str
    submitted_by: Optional[str] = "anonymous"


class IncidentSummary(BaseModel):
    """Short summary returned immediately"""
    incident_id: str
    status: str
    submitted_by: str
    created_at: str
    severity: Optional[str] = None


class IncidentDetail(BaseModel):
    """Full incident data"""
    incident_id: str
    status: str
    submitted_by: str
    created_at: str
    severity: Optional[str]
    affected_services: Optional[List[str]]
    log_analysis: Optional[str]
    root_cause: Optional[str]
    fixes: Optional[str]
    runbook: Optional[str]
    post_mortem: Optional[str]
    runbook_path: Optional[str]
    post_mortem_path: Optional[str]
    errors: Optional[List[str]]


# ─────────────────────────────────────────
# Background Task — runs pipeline async
# ─────────────────────────────────────────
def run_pipeline(incident_id: str, raw_logs: str):
    """Updated to persist to PostgreSQL"""
    db: Session = get_session()

    try:
        incident = db.query(Incident).filter_by(
            incident_id=incident_id
        ).first()

        if not incident:
            raise Exception(f"Incident {incident_id} not found")

        incident.status = "processing"
        db.commit()

        # Build and run graph
        initial_state = {
            "raw_logs": raw_logs,
            "log_analysis": None,
            "root_cause": None,
            "fixes": None,
            "search_queries": None,
            "runbook": None,
            "post_mortem": None,
            "severity": None,
            "affected_services": None,
            "incident_id": incident_id,
            "runbook_path": None,
            "post_mortem_path": None,
            "errors": [],
            "current_agent": None
        }

        final_state = graph.invoke(initial_state)

        # Persist results
        incident.status           = "completed"
        incident.log_analysis     = final_state.get("log_analysis")
        incident.root_cause       = final_state.get("root_cause")
        incident.fixes            = final_state.get("fixes")
        incident.runbook          = final_state.get("runbook")
        incident.post_mortem      = final_state.get("post_mortem")
        incident.severity         = final_state.get("severity")
        incident.affected_services = final_state.get("affected_services")
        incident.search_queries   = final_state.get("search_queries")
        incident.runbook_path     = final_state.get("runbook_path")
        incident.post_mortem_path = final_state.get("post_mortem_path")
        incident.errors           = final_state.get("errors", [])
        incident.updated_at       = datetime.utcnow()
        db.commit()

    except Exception as e:
        incident = db.query(Incident).filter_by(incident_id=incident_id).first()
        if incident:
            incident.status = "failed"
            incident.errors = [str(e)]
            db.commit()
    finally:
        db.close()


# ─────────────────────────────────────────
# Routes
# ─────────────────────────────────────────
@app.get("/")
def root():
    return {
        "name": "DevOps Autopilot",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "POST /analyze — Submit logs for analysis",
            "GET  /incidents — List all incidents",
            "GET  /incidents/{id} — Get full incident detail",
            "GET  /health — Health check"
        ]
    }


@app.get("/health")
def health():
    db = get_session()

    try:
        count = db.query(Incident).count()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "total_incidents": count
        }

    finally:
        db.close()
    


@app.post("/analyze", response_model=IncidentSummary)
async def analyze_logs(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit logs for analysis.
    Returns immediately with incident_id.
    Pipeline runs in background.
    Poll /incidents/{id} for results.
    """
    if not request.raw_logs.strip():
        raise HTTPException(
            status_code=400,
            detail="raw_logs cannot be empty"
        )

    if len(request.raw_logs) > 50000:
        raise HTTPException(
            status_code=400,
            detail="Logs too large. Maximum 50,000 characters."
        )

    # Create incident record
    incident_id = f"INC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
    created_at = datetime.now().isoformat()

    db = get_session()

    try:
        incident = Incident(
            incident_id=incident_id,
            status="queued",
            submitted_by=request.submitted_by,
            raw_logs=request.raw_logs,
            created_at=datetime.utcnow()
        )

        db.add(incident)
        db.commit()

        background_tasks.add_task(
            run_pipeline,
            incident_id,
            request.raw_logs
        )

        return IncidentSummary(
            incident_id=incident_id,
            status="queued",
            submitted_by=request.submitted_by,
            created_at=incident.created_at.isoformat()
        )

    finally:
        db.close()

    


@app.get("/incidents")
def list_incidents():
    db = get_session()

    try:
        rows = db.query(Incident)\
                 .order_by(Incident.created_at.desc())\
                 .all()

        return [
            IncidentSummary(
                incident_id=r.incident_id,
                status=r.status,
                submitted_by=r.submitted_by,
                created_at=r.created_at.isoformat(),
                severity=r.severity
            )
            for r in rows
        ]

    finally:
        db.close()


@app.get("/incidents/{incident_id}", response_model=IncidentDetail)
def get_incident(incident_id: str):
    """Returns full detail for one incident"""
    db = get_session()

    try:
        row = db.query(Incident).filter_by(
            incident_id=incident_id
        ).first()

        if not row:
            raise HTTPException(
                status_code=404,
                detail="Incident not found"
            )

        return IncidentDetail(
            incident_id=row.incident_id,
            status=row.status,
            submitted_by=row.submitted_by,
            created_at=row.created_at.isoformat(),
            severity=row.severity,
            affected_services=row.affected_services,
            log_analysis=row.log_analysis,
            root_cause=row.root_cause,
            fixes=row.fixes,
            runbook=row.runbook,
            post_mortem=row.post_mortem,
            runbook_path=row.runbook_path,
            post_mortem_path=row.post_mortem_path,
            errors=row.errors or []
        )

    finally:
        db.close()
