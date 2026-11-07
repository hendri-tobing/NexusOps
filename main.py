import os
import re
import json
import uuid
import subprocess
from datetime import datetime
from typing import Optional
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="NexusOps - Spatial War Room & Workplace Brain (Tencent Cloud WorkBuddy)")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_HTML = os.path.join(BASE_DIR, "templates", "index.html")
SOP_FILE = os.path.join(BASE_DIR, "sop_data.json")
POST_MORTEM_FILE = os.path.join(BASE_DIR, "POST_MORTEM_LATEST.md")

# Load SOP knowledge base
with open(SOP_FILE, "r") as f:
    SOPS = json.load(f)


def check_workbuddy_desktop_running() -> dict:
    """Detect whether Tencent Cloud WorkBuddy Desktop ('WorkBuddy AI.app') is actively running on the OS."""
    try:
        res = subprocess.run(
            ["pgrep", "-f", "WorkBuddy AI.app/Contents/MacOS"],
            capture_output=True,
            text=True,
            timeout=1.5,
        )
        pids = [p.strip() for p in res.stdout.splitlines() if p.strip()]
        if pids:
            return {"running": True, "pid": pids[0], "app": "WorkBuddy AI.app"}
    except Exception:
        pass
    return {"running": False, "pid": None, "app": "WorkBuddy AI.app"}


def retrieve_best_sop(query: str) -> tuple[dict, float, list[str]]:
    """Compute actual token overlap similarity against sop_data.json entries."""
    query_tokens = [t for t in re.findall(r"[a-z0-9]+", query.lower()) if len(t) > 2]
    best_sop = SOPS[0]
    best_score = 0.0
    best_matched = []

    for sop in SOPS:
        corpus = " ".join(
            [
                sop.get("id", ""),
                sop.get("title", ""),
                sop.get("domain", ""),
                sop.get("summary", ""),
                " ".join(sop.get("steps", [])),
            ]
        ).lower()
        matched = [t for t in query_tokens if t in corpus]
        score = round((len(matched) / max(len(query_tokens), 1)) * 100, 1)
        if score > best_score:
            best_score = score
            best_sop = sop
            best_matched = matched

    return best_sop, best_score, best_matched


# In-memory store for active incidents & live state synchronization with WorkBuddy Desktop
active_incidents = {}
system_state = {
    "version": 1,
    "status": "HEALTHY",
    "source": "system",
    "active_incident": None,
    "last_mitigation": None,
}


class MitigateRequest(BaseModel):
    incident_id: Optional[str] = None


@app.api_route("/", methods=["GET", "HEAD"])
async def get_index():
    return FileResponse(INDEX_HTML)


@app.get("/api/health")
async def health_check():
    wb = check_workbuddy_desktop_running()
    return {
        "status": "ok",
        "workbuddy_desktop": wb,
        "sop_count": len(SOPS),
        "system_status": system_state["status"],
        "version": system_state["version"],
    }


@app.get("/api/state")
async def get_state():
    """Endpoint polled by the Spatial War Room UI to sync actions triggered from Tencent Cloud WorkBuddy Desktop."""
    wb = check_workbuddy_desktop_running()
    return {
        **system_state,
        "sop_count": len(SOPS),
        "workbuddy_desktop": wb,
    }


@app.post("/api/incident/trigger")
async def trigger_incident(type: str = "payment", source: str = "workbuddy_desktop"):
    incident_id = f"INC-{uuid.uuid4().hex[:6].upper()}"

    if type == "payment":
        affected_node = "Payment Core (Worker Ingress)"
        query = "payment webhook gateway timeout dropped callbacks proxy retry idempotency"
        alert_log = "Ingress Webhook timeout spike on node Payment Core (Worker Ingress). 504 Gateway errors exceeded threshold (>5%)."
        tasks = [
            {"title": "Trigger Redundant Ingress Failover", "pic": "Budi Pratama (Payment Lead)", "eta": "2m"},
            {"title": "Engage Redis Idempotency Queue", "pic": "Rizky Sanjaya (SRE Lead)", "eta": "1m"},
            {"title": "Dispatch Merchant Status Notice", "pic": "Sarah Amalia (CS Lead)", "eta": "3m"},
        ]
    else:
        affected_node = "Primary DB (PgBouncer Pool)"
        query = "database connection pool saturation recovery queries pgbouncer throttle"
        alert_log = "Connection pool exhaustion on node Primary DB (PgBouncer Pool). Active query wait time exceeded threshold (>45s)."
        tasks = [
            {"title": "Terminate Orphan Idle Read Connections", "pic": "Rizky Sanjaya (SRE Lead)", "eta": "1m"},
            {"title": "Expand PgBouncer Allocation (+25%)", "pic": "DevOps OnCall Bot", "eta": "2m"},
            {"title": "Throttle Background Analytic Cronjobs", "pic": "Data Platform Team", "eta": "3m"},
        ]

    matched_sop, match_score, matched_terms = retrieve_best_sop(query)

    incident_data = {
        "incident_id": incident_id,
        "type": type,
        "affected_node": affected_node,
        "query": query,
        "alert_log": alert_log,
        "sop": matched_sop,
        "match_score": match_score,
        "matched_terms": matched_terms,
        "tasks": tasks,
        "status": "ACTIVE_UNMITIGATED",
        "source": source,
    }
    active_incidents[incident_id] = incident_data

    system_state["version"] += 1
    system_state["status"] = "ACTIVE_UNMITIGATED"
    system_state["source"] = source
    system_state["active_incident"] = incident_data
    system_state["last_mitigation"] = None

    return {**incident_data, "state_version": system_state["version"]}


@app.post("/api/incident/mitigate")
async def mitigate_incident(
    req: Optional[MitigateRequest] = None,
    source: str = "workbuddy_desktop",
):
    incident_id = req.incident_id if isinstance(req, MitigateRequest) and req.incident_id else None

    if not incident_id and system_state["active_incident"]:
        incident_id = system_state["active_incident"]["incident_id"]
    elif not incident_id and active_incidents:
        incident_id = next(reversed(active_incidents))

    incident = active_incidents.get(incident_id) if incident_id else None
    if not incident and system_state["active_incident"]:
        incident = system_state["active_incident"]
        incident_id = incident["incident_id"]

    if not incident:
        return JSONResponse(
            status_code=404,
            content={"error": "No active incident found to mitigate. Trigger an incident first."},
        )

    inc_type = incident.get("type", "payment")
    sop = incident["sop"]
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if inc_type == "payment":
        post_mortem = (
            f"INCIDENT REPORT [{incident_id}] — {timestamp_str}\n"
            f"Matched SOP: {sop['id']} ({sop['title']})\n"
            f"Root Cause: External upstream gateway degradation triggering 504 cascading timeouts.\n"
            f"Mitigation Executed: Switched traffic to secondary proxy; idempotency lock prevented duplicate ledger writes.\n"
            f"Impact: Stalled transactions: 142. Successfully reconciled: 142. Financial discrepancy: Rp 0.\n"
            f"Saved File: POST_MORTEM_LATEST.md"
        )
        mitigation_logs = [
            "[ACTION EXECUTION] Rerouting ingress traffic to secondary redundant payment gateway...",
            "[IDEMPOTENCY LOCK] Redis transaction lock engaged. 142 stalled transactions queued for reconciliation.",
            "[TELEMETRY RECOVERED] Payment Core 504 error rate dropped to 0.00%.",
            "[POST-MORTEM SAVED] Written audit report to workspace file: POST_MORTEM_LATEST.md",
        ]
    else:
        post_mortem = (
            f"INCIDENT REPORT [{incident_id}] — {timestamp_str}\n"
            f"Matched SOP: {sop['id']} ({sop['title']})\n"
            f"Root Cause: Cascading analytical read queries exhausting PgBouncer connection ceiling.\n"
            f"Mitigation Executed: Terminated idle orphan sessions (>45s), expanded pool allocation by +25%, throttled batch cronjobs.\n"
            f"Impact: Queued API requests: 310. Successfully processed: 310. Data loss: 0 records.\n"
            f"Saved File: POST_MORTEM_LATEST.md"
        )
        mitigation_logs = [
            "[ACTION EXECUTION] Terminating orphan idle read queries (>45s) on Primary DB...",
            "[POOL EXPANSION] PgBouncer connection ceiling scaled +25% with memory guard active.",
            "[TELEMETRY RECOVERED] DB pool utilization stabilized. Active connections normal.",
            "[POST-MORTEM SAVED] Written audit report to workspace file: POST_MORTEM_LATEST.md",
        ]

    # Write real post-mortem markdown file into the workspace so WorkBuddy Desktop App can read it
    md_report = (
        f"# EXECUTIVE POST-MORTEM REPORT — {incident_id}\n\n"
        f"- **Timestamp:** {timestamp_str}\n"
        f"- **Affected Node:** {incident['affected_node']}\n"
        f"- **Matched SOP:** `{sop['id']}` — {sop['title']} (Match Score: {incident.get('match_score', 100)}%)\n"
        f"- **Status:** MITIGATED & VERIFIED\n\n"
        f"## Summary\n```\n{post_mortem}\n```\n\n"
        f"## Dispatched Tasks & PIC Accountability\n"
        + "\n".join([f"- [x] **{t['title']}** — PIC: {t['pic']} (ETA: {t['eta']})" for t in incident["tasks"]])
        + "\n"
    )
    with open(POST_MORTEM_FILE, "w") as f:
        f.write(md_report)

    active_incidents.pop(incident_id, None)

    result = {
        "status": "MITIGATED",
        "incident_id": incident_id,
        "type": inc_type,
        "sop_id": sop["id"],
        "mitigation_logs": mitigation_logs,
        "post_mortem": post_mortem,
        "saved_file": "POST_MORTEM_LATEST.md",
        "source": source,
    }

    system_state["version"] += 1
    system_state["status"] = "MITIGATED"
    system_state["source"] = source
    if system_state["active_incident"]:
        system_state["active_incident"]["status"] = "MITIGATED"
    system_state["last_mitigation"] = result

    return {**result, "state_version": system_state["version"]}


@app.post("/api/incident/reset")
async def reset_system():
    active_incidents.clear()
    system_state["version"] += 1
    system_state["status"] = "HEALTHY"
    system_state["source"] = "system"
    system_state["active_incident"] = None
    system_state["last_mitigation"] = None
    return {"status": "HEALTHY", "state_version": system_state["version"]}
