db = db.getSiblingDB("qa_results");

db.createCollection("test_runs");
db.createCollection("test_cases");
db.createCollection("api_logs");

db.test_runs.createIndex({ run_id: 1 }, { unique: true });
db.test_runs.createIndex({ created_at: -1 });
db.test_cases.createIndex({ run_id: 1 });
db.test_cases.createIndex({ case_id: 1 });
db.test_cases.createIndex({ protocol: 1 });
db.test_cases.createIndex({ service: 1 });
db.test_cases.createIndex({ created_at: -1 });
db.api_logs.createIndex({ run_id: 1 });
db.api_logs.createIndex({ case_id: 1 });
db.api_logs.createIndex({ protocol: 1 });
db.api_logs.createIndex({ service: 1 });
db.api_logs.createIndex({ created_at: -1 });

