import json
import os
import time
from datetime import datetime, timezone

import redis
import requests
from pymongo import MongoClient

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
API_BASE = os.getenv("API_BASE", "http://localhost:8000").rstrip("/")
MONGODB_URI = os.getenv("MONGODB_URI", os.getenv("MONGO_URI", "mongodb://localhost:27017"))
REDIS_URL = os.getenv("REDIS_URL", os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
SMOKE_USER_EMAIL = os.getenv("SMOKE_USER_EMAIL", "smoke@example.com")
SMOKE_USER_PASSWORD = os.getenv("SMOKE_USER_PASSWORD", "Password123!")

report = {
    "summary": {"status": "PASS", "checked_at": datetime.now(timezone.utc).isoformat(), "front_end": "PASS", "back_end": "PASS"},
    "details": {
        "frontend": {"status": "PASS", "subchecks": []},
        "backend": {"status": "PASS", "subchecks": []},
        "db": {},
        "celery": {},
        "llm": {},
        "auth": {},
        "e2e_run": {},
        "performance": {},
        "security": {}
    },
    "logs": {"http_outputs": [], "trace_samples": [], "error_traces": []},
    "remediation": [],
    "artifacts": {"created_issues": []}
}

def add_frontend_check(name, status, response_time, headers, body_snippet):
    report["details"]["frontend"]["subchecks"].append({
        "name": name,
        "status": status,
        "response_time_ms": response_time,
        "raw_headers": dict(headers),
        "raw_body_snippet": body_snippet[:100] + "..." if body_snippet else ""
    })
    if status == "FAIL":
        report["details"]["frontend"]["status"] = "FAIL"
        report["summary"]["front_end"] = "FAIL"
        report["summary"]["status"] = "FAIL"

def add_backend_check(name, status, response_time, headers, body_snippet):
    report["details"]["backend"]["subchecks"].append({
        "name": name,
        "status": status,
        "response_time_ms": response_time,
        "raw_headers": dict(headers) if headers else {},
        "raw_body_snippet": body_snippet[:100] + "..." if body_snippet else ""
    })
    if status == "FAIL":
        report["details"]["backend"]["status"] = "FAIL"
        report["summary"]["back_end"] = "FAIL"
        report["summary"]["status"] = "FAIL"

def ensure_session() -> tuple[dict[str, str], str]:
    register_payload = {
        "email": SMOKE_USER_EMAIL,
        "password": SMOKE_USER_PASSWORD,
        "name": "TraceAI Smoke User",
    }
    requests.post(f"{API_BASE}/api/auth/register", json=register_payload, timeout=10)

    login = requests.post(
        f"{API_BASE}/api/auth/login",
        json={"email": SMOKE_USER_EMAIL, "password": SMOKE_USER_PASSWORD},
        timeout=10,
    )
    login.raise_for_status()
    payload = login.json()
    token = payload["access_token"]
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, token


def run_tests():
    try:
        headers, token = ensure_session()
        report["details"]["auth"] = {"status": "PASS", "token_type": "bearer"}
    except Exception as exc:
        report["details"]["auth"] = {"status": "FAIL", "raw_error": str(exc)}
        report["summary"]["status"] = "FAIL"
        headers = {"Content-Type": "application/json"}

    # A & B Frontend Checks
    try:
        start = time.time()
        res = requests.get(f"{FRONTEND_URL}/", timeout=10)
        ms = int((time.time() - start) * 1000)
        body = res.text
        status = "PASS" if res.status_code == 200 and ("<div id=\"root\">" in body or "index.html" in body) else "FAIL"
        add_frontend_check("GET /", status, ms, res.headers, body)
        
        # SPA Fallback
        res_spa = requests.get(f"{FRONTEND_URL}/non-existent-route", timeout=10)
        add_frontend_check("GET /non-existent-route (SPA)", "PASS" if res_spa.status_code == 200 else "FAIL", int(res_spa.elapsed.total_seconds()*1000), res_spa.headers, res_spa.text)
        
        # Headers check
        start = time.time()
        res_cfg = requests.get(f"{FRONTEND_URL}/config.js", timeout=10)
        ms_cfg = int((time.time() - start) * 1000)
        cfg_status = "PASS" if res_cfg.status_code == 200 else "FAIL"
        add_frontend_check("GET /config.js", cfg_status, ms_cfg, res_cfg.headers, res_cfg.text)
    except Exception as e:
         report["summary"]["front_end"] = "FAIL"
         report["summary"]["status"] = "FAIL"
         report["remediation"].append({"issue": f"Frontend unreachable: {e}", "severity": "critical", "suggested_fix": "Check Nginx / React container."})

    # C Backend Health
    try:
        start = time.time()
        res_h = requests.get(f"{API_BASE}/health", timeout=10)
        add_backend_check("GET /health", "PASS" if res_h.status_code == 200 else "FAIL", int((time.time()-start)*1000), res_h.headers, res_h.text)
        
        res_r = requests.get(f"{API_BASE}/ready", timeout=10)
        add_backend_check("GET /ready", "PASS" if res_r.status_code in {200, 503} else "FAIL", int((time.time()-start)*1000), res_r.headers, res_r.text)
        
        res_m = requests.get(f"{API_BASE}/metrics", timeout=10)
        add_backend_check("GET /metrics", "PASS" if res_m.status_code == 200 else "WARN", int((time.time()-start)*1000), res_m.headers, res_m.text)
    except Exception as e:
         report["summary"]["back_end"] = "FAIL"
         report["summary"]["status"] = "FAIL"
         report["remediation"].append({"issue": f"Backend unreachable: {e}", "severity": "critical", "suggested_fix": "Check FastAPI app or docker-compose api logs."})

    # D Connectivity
    try:
        start = time.time()
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        report["details"]["db"]["mongo"] = {"status": "PASS", "ping_ms": int((time.time()-start)*1000)}
    except Exception as e:
        report["details"]["db"]["mongo"] = {"status": "FAIL", "raw_error": str(e)}
        report["summary"]["status"] = "FAIL"

    try:
        start = time.time()
        r = redis.Redis.from_url(REDIS_URL, socket_timeout=2)
        r.ping()
        report["details"]["db"]["redis"] = {"status": "PASS", "ping_ms": int((time.time()-start)*1000)}
    except Exception as e:
        report["details"]["db"]["redis"] = {"status": "FAIL", "raw_error": str(e)}
        report["summary"]["status"] = "FAIL"

    try:
        start = time.time()
        res_llm = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        report["details"]["llm"] = {"status": "PASS" if res_llm.status_code == 200 else "FAIL", "latency_ms": int((time.time()-start)*1000), "sample_response": res_llm.text[:100]}
    except Exception as e:
        report["details"]["llm"] = {"status": "FAIL", "raw_error": str(e)}

    # E2E queued run flow
    try:
        submit = requests.post(
            f"{API_BASE}/api/runs/submit",
            json={"session_id": "e2esmoke123", "goal": "connectivity test"},
            headers=headers,
            timeout=15,
        )
        report["details"]["e2e_run"]["submit_status"] = submit.status_code
        if submit.status_code == 202:
            run_id = submit.json()["run_id"]
            report["details"]["e2e_run"]["run_id"] = run_id
            status = requests.get(f"{API_BASE}/api/runs/{run_id}/status", headers=headers, timeout=10)
            report["details"]["e2e_run"]["status"] = "PASS"
            report["details"]["e2e_run"]["run_status_payload"] = status.json()
        else:
             report["details"]["e2e_run"]["status"] = "FAIL"
             report["details"]["e2e_run"]["errors"] = [submit.text]
        
    except Exception as e:
         report["details"]["e2e_run"]["status"] = "FAIL"
         report["details"]["e2e_run"]["errors"] = [str(e)]

    with open("report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    run_tests()
    
    status = report["summary"]["status"]
    print(f"Status: {status}")
    print(f"Checked At: {report['summary']['checked_at']}")
    print(f"Frontend: {report['summary']['front_end']}")
    print(f"Backend: {report['summary']['back_end']}")
    print("Dependencies:")
    print(f"  MongoDB: {report['details']['db'].get('mongo', {}).get('status', 'FAIL')}")
    print(f"  Redis:   {report['details']['db'].get('redis', {}).get('status', 'FAIL')}")
    print(f"  LLM:     {report['details']['llm'].get('status', 'FAIL')}")
    print(f"E2E Run: {report['details'].get('e2e_run', {}).get('status', 'FAIL')}")

    with open("summary.txt", "w") as f:
        f.write(f"Smoke Test Summary - {status}\n")
        f.write(f"Frontend: {report['summary']['front_end']}\n")
        f.write(f"Backend: {report['summary']['back_end']}\n")
        f.write(f"DBs: Mongo={report['details']['db'].get('mongo', {}).get('status', 'FAIL')} | Redis={report['details']['db'].get('redis', {}).get('status', 'FAIL')}\n")
        f.write(f"E2E Test: {report['details'].get('e2e_run', {}).get('status', 'FAIL')}\n")
        f.write(f"Remediations needed: {len(report['remediation'])}\n")
