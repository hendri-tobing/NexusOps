#!/usr/bin/env python3
"""
Tencent Cloud WorkBuddy Desktop — CLI Bridge for NexusOps Spatial War Room.
Used by Tencent Cloud WorkBuddy Desktop App to trigger simulations, retrieve SOPs,
dispatch PIC tasks, and execute automated mitigation while syncing with the live Web Radar.
"""
import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8765"


def request_api(path: str, method: str = "GET", payload: dict = None) -> dict:
    url = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if data is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"[ERROR] Tidak dapat menghubungi server NexusOps di {BASE_URL}: {e}")
        print("Pastikan server sudah dijalankan dengan: ./run_demo.sh")
        sys.exit(1)


def cmd_status():
    state = request_api("/api/state")
    print("=== NEXUSOPS TELEMETRY & WORKBUDDY STATUS ===")
    print(f"System Status : {state.get('status')}")
    print(f"State Version : {state.get('version')}")
    inc = state.get("active_incident")
    if inc:
        print(f"Active Incident: {inc['incident_id']} ({inc['affected_node']})")
        print(f"Matched SOP    : {inc['sop']['id']} - {inc['sop']['title']}")
    else:
        print("Active Incident: None (All 6 Spatial Nodes Nominal)")


def cmd_trigger(inc_type: str = "payment"):
    res = request_api(f"/api/incident/trigger?type={inc_type}&source=workbuddy_desktop", method="POST")
    sop = res["sop"]
    print(f"🚨 [INCIDENT DETECTED] {res['incident_id']} — {res['affected_node']}")
    print(f"Gejala        : {res['alert_log']}")
    print(f"\n📘 [WORKPLACE BRAIN — SOP RETRIEVAL]")
    print(f"Matched SOP   : {sop['id']} — {sop['title']} (Severity: {sop['severity']})")
    print(f"Domain        : {sop['domain']}")
    print(f"Ringkasan     : {sop['summary']}")
    print("\n⚡ [OFFICE AGENT — DISPATCHED ACTION ITEMS]")
    for idx, t in enumerate(res["tasks"], 1):
        print(f"  {idx}. {t['title']} -> PIC: {t['pic']} (ETA: {t['eta']})")
    print("\nStatus Radar Web (http://127.0.0.1:8765) telah diperbarui secara real-time.")
    print("Ketik 'Eksekusi mitigasi otomatis sekarang' di WorkBuddy Desktop untuk menjalankan pemulihan.")


def cmd_mitigate():
    res = request_api("/api/incident/mitigate?source=workbuddy_desktop", method="POST", payload={})
    print(f"✅ [MITIGASI SELESAI] Insiden {res['incident_id']} ({res['sop_id']}) berhasil dipulihkan!")
    print("\n📋 [LOG EKSEKUSI WORKBUDDY]")
    for line in res.get("mitigation_logs", []):
        print(f"  - {line}")
    print("\n📊 [EXECUTIVE POST-MORTEM AUDIT]")
    print(res["post_mortem"])


def cmd_reset():
    request_api("/api/incident/reset", method="POST")
    print("🔄 [SYSTEM RESET] Seluruh node NexusOps kembali ke status HEALTHY (Hijau).")


if __name__ == "__main__":
    action = sys.argv[1].lower() if len(sys.argv) > 1 else "status"
    if action in ("trigger", "trigger-payment", "payment"):
        cmd_trigger("payment")
    elif action in ("trigger-db", "db"):
        cmd_trigger("db")
    elif action in ("mitigate", "mitigasi", "recover"):
        cmd_mitigate()
    elif action in ("reset",):
        cmd_reset()
    else:
        cmd_status()
