from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from app.mongodb import db, public_doc


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class StructuredResultPlugin:
    def __init__(self) -> None:
        self.cases: list[dict] = []

    def pytest_runtest_logreport(self, report) -> None:  # pytest hook
        if report.when != "call":
            return

        record = {}
        for key, value in getattr(report, "user_properties", []):
            if key == "case_record":
                record = dict(value)
                break

        status = "PASSED" if report.passed else "FAILED"
        if report.skipped:
            status = "SKIPPED"

        case = {
            "case_id": record.get("case_id", report.nodeid),
            "name": record.get("name", report.nodeid),
            "protocol": record.get("protocol", "UNKNOWN"),
            "service": record.get("service", "unknown"),
            "endpoint": record.get("endpoint", ""),
            "method": record.get("method", ""),
            "status": status,
            "duration_ms": record.get("duration_ms", round(report.duration * 1000, 2)),
            "request_payload": record.get("request_payload", {}),
            "response_status": record.get("response_status"),
            "response_payload": record.get("response_payload", {}),
            "expected_result": record.get("expected_result", ""),
            "actual_result": record.get("actual_result", ""),
            "error_message": "" if report.passed else report.longreprtext,
            "created_at": utc_now(),
        }
        if not case["error_message"]:
            case["error_message"] = record.get("error_message", "")
        self.cases.append(case)


def execute_test_run() -> dict:
    run_id = f"RUN-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8].upper()}"
    started_at = utc_now()
    created_at = started_at

    db.test_runs.insert_one(
        {
            "run_id": run_id,
            "status": "RUNNING",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "pass_rate": 0,
            "duration_ms": 0,
            "average_duration_ms": 0,
            "started_at": started_at,
            "ended_at": None,
            "created_at": created_at,
        }
    )

    plugin = StructuredResultPlugin()
    test_dir = Path(__file__).resolve().parents[1] / "tests"
    run_started = datetime.now(timezone.utc)
    exit_code = pytest.main(["-q", str(test_dir)], plugins=[plugin])
    run_ended = datetime.now(timezone.utc)

    cases = plugin.cases
    total = len(cases)
    passed = sum(1 for case in cases if case["status"] == "PASSED")
    failed = sum(1 for case in cases if case["status"] == "FAILED")
    skipped = sum(1 for case in cases if case["status"] == "SKIPPED")
    duration_ms = round((run_ended - run_started).total_seconds() * 1000, 2)
    average_duration_ms = round(sum(float(case.get("duration_ms", 0)) for case in cases) / total, 2) if total else 0
    pass_rate = round((passed / total) * 100, 2) if total else 0
    status = "COMPLETED" if exit_code == 0 and failed == 0 else "FAILED"
    ended_at = utc_now()

    for case in cases:
        case["run_id"] = run_id

    api_logs = [
        {
            "run_id": run_id,
            "case_id": case["case_id"],
            "protocol": case["protocol"],
            "service": case["service"],
            "endpoint": case["endpoint"],
            "request_headers": {},
            "request_payload": case["request_payload"],
            "response_status": case["response_status"],
            "response_payload": case["response_payload"],
            "duration_ms": case["duration_ms"],
            "created_at": case["created_at"],
        }
        for case in cases
    ]

    if cases:
        db.test_cases.insert_many(cases)
    if api_logs:
        db.api_logs.insert_many(api_logs)

    summary = {
        "run_id": run_id,
        "status": status,
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "pass_rate": pass_rate,
        "duration_ms": duration_ms,
        "average_duration_ms": average_duration_ms,
        "started_at": started_at,
        "ended_at": ended_at,
        "created_at": created_at,
    }
    db.test_runs.update_one({"run_id": run_id}, {"$set": summary})
    return {**summary, "cases": [public_doc(case) for case in cases]}


def list_test_runs() -> list[dict]:
    return [public_doc(doc) for doc in db.test_runs.find({}, {"_id": 0}).sort("created_at", -1).limit(25)]


def get_test_run(run_id: str) -> dict | None:
    summary = db.test_runs.find_one({"run_id": run_id}, {"_id": 0})
    if not summary:
        return None
    cases = [public_doc(doc) for doc in db.test_cases.find({"run_id": run_id}, {"_id": 0}).sort("case_id", 1)]
    logs = [public_doc(doc) for doc in db.api_logs.find({"run_id": run_id}, {"_id": 0}).sort("case_id", 1)]
    return {**summary, "cases": cases, "api_logs": logs}

