import os
from typing import Any

from pymongo import DESCENDING, MongoClient

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "qa_results")

client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
db = client[MONGODB_DATABASE]


def ensure_indexes() -> None:
    client.admin.command("ping")
    db.test_runs.create_index("run_id", unique=True)
    db.test_runs.create_index([("created_at", DESCENDING)])
    db.test_cases.create_index("run_id")
    db.test_cases.create_index("case_id")
    db.test_cases.create_index("protocol")
    db.test_cases.create_index("service")
    db.test_cases.create_index([("created_at", DESCENDING)])
    db.api_logs.create_index("run_id")
    db.api_logs.create_index("case_id")
    db.api_logs.create_index("protocol")
    db.api_logs.create_index("service")
    db.api_logs.create_index([("created_at", DESCENDING)])


def public_doc(document: dict[str, Any]) -> dict[str, Any]:
    document = dict(document)
    document.pop("_id", None)
    return document

