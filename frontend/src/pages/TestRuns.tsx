import { ExperimentOutlined, ReloadOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Drawer, Progress, Space, Table, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { useEffect, useState } from "react";
import { apiGet, apiPost, type ApiCallResult } from "../api/client";
import JsonViewer from "../components/JsonViewer";
import MetricCard from "../components/MetricCard";
import StatusBadge from "../components/StatusBadge";
import TestResultTable, { type TestCaseResult } from "../components/TestResultTable";

const { Text, Title } = Typography;

interface TestRunSummary {
  run_id: string;
  status: string;
  total: number;
  passed: number;
  failed: number;
  skipped: number;
  pass_rate: number;
  duration_ms: number;
  average_duration_ms?: number;
  started_at?: string;
  ended_at?: string;
  created_at?: string;
}

interface TestRunDetail extends TestRunSummary {
  cases: TestCaseResult[];
  api_logs?: unknown[];
}

export default function TestRuns() {
  const [runs, setRuns] = useState<TestRunSummary[]>([]);
  const [detail, setDetail] = useState<TestRunDetail | null>(null);
  const [selectedCase, setSelectedCase] = useState<TestCaseResult | null>(null);
  const [lastCall, setLastCall] = useState<ApiCallResult<unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);

  async function loadRuns() {
    setLoading(true);
    const result = await apiGet<TestRunSummary[]>("/api/test-runs");
    setLoading(false);
    setLastCall(result);
    if (result.ok && result.data) {
      setRuns(result.data);
      if (!detail && result.data[0]) {
        await loadRunDetail(result.data[0].run_id);
      }
    }
  }

  async function loadRunDetail(runId: string) {
    const result = await apiGet<TestRunDetail>(`/api/test-runs/${runId}`);
    setLastCall(result);
    if (result.ok && result.data) {
      setDetail(result.data);
    }
  }

  async function triggerRegression() {
    setRunning(true);
    const result = await apiPost<TestRunDetail>("/api/test-runs");
    setRunning(false);
    setLastCall(result);
    if (result.ok && result.data) {
      setDetail(result.data);
      await loadRuns();
    }
  }

  useEffect(() => {
    void loadRuns();
  }, []);

  const columns: ColumnsType<TestRunSummary> = [
    { title: "Run ID", dataIndex: "run_id" },
    { title: "Status", dataIndex: "status", width: 130, render: (status) => <StatusBadge status={status} /> },
    { title: "Total", dataIndex: "total", width: 90 },
    { title: "Passed", dataIndex: "passed", width: 90 },
    { title: "Failed", dataIndex: "failed", width: 90 },
    { title: "Pass Rate", dataIndex: "pass_rate", width: 130, render: (value) => `${value ?? 0}%` },
    { title: "Duration", dataIndex: "duration_ms", width: 120, render: (value) => `${value ?? 0} ms` },
    {
      title: "",
      width: 80,
      render: (_, row) => (
        <Button size="small" onClick={() => void loadRunDetail(row.run_id)}>
          Open
        </Button>
      )
    }
  ];

  return (
    <div className="page-stack">
      <div className="page-header">
        <div>
          <Text className="page-kicker">REST, GraphQL, and gRPC regression suite</Text>
          <Title level={2}>Test Runs</Title>
        </div>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => void loadRuns()} loading={loading}>
            Refresh
          </Button>
          <Button type="primary" icon={<ExperimentOutlined />} onClick={() => void triggerRegression()} loading={running}>
            Run API Regression
          </Button>
        </Space>
      </div>

      {lastCall && !lastCall.ok ? <Alert type="error" showIcon message={lastCall.error?.message} description={lastCall.error?.errorCode} /> : null}

      {detail ? (
        <>
          <div className="metric-grid-four">
            <MetricCard title="Total cases" value={detail.total} tone="gray" />
            <MetricCard title="Passed" value={detail.passed} tone="teal" />
            <MetricCard title="Failed" value={detail.failed} tone="red" />
            <MetricCard title="Duration" value={`${detail.duration_ms} ms`} tone="blue" />
          </div>
          <Card className="panel-card" title={`Latest result: ${detail.run_id}`} extra={<StatusBadge status={detail.status} />}>
            <Progress percent={detail.pass_rate} status={detail.failed ? "exception" : "success"} />
            <TestResultTable cases={detail.cases || []} onSelect={setSelectedCase} />
          </Card>
        </>
      ) : null}

      <Table rowKey="run_id" columns={columns} dataSource={runs} loading={loading} size="small" scroll={{ x: 900 }} />

      <Drawer title="Test Case Detail" open={!!selectedCase} width={720} onClose={() => setSelectedCase(null)}>
        <JsonViewer title="Case" value={selectedCase} />
        <JsonViewer title="Request payload" value={selectedCase?.request_payload} />
        <JsonViewer title="Response payload" value={selectedCase?.response_payload} />
      </Drawer>
    </div>
  );
}

