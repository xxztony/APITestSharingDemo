import {
  ApiOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  CloseCircleOutlined,
  CloudServerOutlined,
  DatabaseOutlined,
  FieldTimeOutlined,
  FileDoneOutlined,
  FileSearchOutlined
} from "@ant-design/icons";
import { Alert, Button, Card, Col, Empty, Row, Skeleton, Space, Table, Typography } from "antd";
import { useEffect, useState } from "react";
import { apiGet } from "../api/client";
import JsonViewer from "../components/JsonViewer";
import MetricCard from "../components/MetricCard";
import StatusBadge from "../components/StatusBadge";

const { Text, Title } = Typography;

interface DashboardData {
  metrics: {
    totalOrders: number;
    openOrders: number;
    cancelledOrders: number;
    rejectedOrders: number;
    totalAccounts: number;
    latestPriceSymbol: string;
    latestTestPassRate: number;
    averageApiResponseTime: number;
    latestTestRunStatus: string;
  };
  latestPrice?: Record<string, unknown>;
  recentTestRun?: Record<string, unknown> | null;
  upstreamHealth?: Record<string, boolean>;
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadDashboard() {
    setLoading(true);
    setError(null);
    const result = await apiGet<DashboardData>("/api/dashboard");
    setLoading(false);
    if (!result.ok || !result.data) {
      setError(result.error?.message || "Dashboard request failed");
      return;
    }
    setData(result.data);
  }

  useEffect(() => {
    void loadDashboard();
  }, []);

  const metrics = data?.metrics;
  const run = data?.recentTestRun;

  return (
    <div className="page-stack">
      <div className="page-header">
        <div>
          <Text className="page-kicker">Microservice API testing showcase</Text>
          <Title level={2}>Dashboard</Title>
        </div>
        <Button icon={<FieldTimeOutlined />} onClick={loadDashboard} loading={loading}>
          Refresh
        </Button>
      </div>

      {error ? <Alert type="error" showIcon message={error} /> : null}

      {loading && !data ? (
        <Skeleton active paragraph={{ rows: 8 }} />
      ) : metrics ? (
        <>
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} xl={6}>
              <MetricCard title="Total orders" value={metrics.totalOrders} icon={<FileSearchOutlined />} tone="teal" />
            </Col>
            <Col xs={24} sm={12} xl={6}>
              <MetricCard title="Open orders" value={metrics.openOrders} icon={<CheckCircleOutlined />} tone="blue" />
            </Col>
            <Col xs={24} sm={12} xl={6}>
              <MetricCard title="Cancelled orders" value={metrics.cancelledOrders} icon={<CloseCircleOutlined />} tone="amber" />
            </Col>
            <Col xs={24} sm={12} xl={6}>
              <MetricCard title="Rejected orders" value={metrics.rejectedOrders} icon={<CloseCircleOutlined />} tone="red" />
            </Col>
            <Col xs={24} sm={12} xl={6}>
              <MetricCard title="Accounts" value={metrics.totalAccounts} icon={<DatabaseOutlined />} tone="gray" />
            </Col>
            <Col xs={24} sm={12} xl={6}>
              <MetricCard title="Latest price symbol" value={metrics.latestPriceSymbol} icon={<CloudServerOutlined />} tone="blue" />
            </Col>
            <Col xs={24} sm={12} xl={6}>
              <MetricCard title="Latest pass rate" value={`${metrics.latestTestPassRate}%`} icon={<FileDoneOutlined />} tone="teal" />
            </Col>
            <Col xs={24} sm={12} xl={6}>
              <MetricCard title="Avg API response" value={`${metrics.averageApiResponseTime} ms`} icon={<ClockCircleOutlined />} tone="gray" />
            </Col>
          </Row>

          <Row gutter={[16, 16]}>
            <Col xs={24} xl={14}>
              <Card
                title="Recent Test Run"
                extra={<StatusBadge status={metrics.latestTestRunStatus} />}
                className="panel-card"
              >
                {run ? (
                  <Table
                    rowKey={() => String(run.run_id)}
                    pagination={false}
                    size="small"
                    dataSource={[run]}
                    columns={[
                      { title: "Run ID", dataIndex: "run_id" },
                      { title: "Status", dataIndex: "status", render: (status) => <StatusBadge status={status} /> },
                      { title: "Total", dataIndex: "total" },
                      { title: "Passed", dataIndex: "passed" },
                      { title: "Failed", dataIndex: "failed" },
                      { title: "Duration", dataIndex: "duration_ms", render: (value) => `${value ?? 0} ms` },
                      { title: "Started", dataIndex: "started_at" },
                      { title: "Ended", dataIndex: "ended_at" }
                    ]}
                    scroll={{ x: 900 }}
                  />
                ) : (
                  <Empty description="No test run yet" />
                )}
              </Card>
            </Col>
            <Col xs={24} xl={10}>
              <Card title="Service Signals" className="panel-card">
                <Space direction="vertical" size={12} className="full-width">
                  {Object.entries(data?.upstreamHealth || {}).map(([name, ok]) => (
                    <div className="signal-row" key={name}>
                      <Space>
                        <ApiOutlined />
                        <Text>{name}</Text>
                      </Space>
                      <StatusBadge status={ok ? "OK" : "FAILED"} />
                    </div>
                  ))}
                </Space>
              </Card>
            </Col>
          </Row>

          <JsonViewer title="Latest gRPC price response as JSON" value={data.latestPrice} />
        </>
      ) : null}
    </div>
  );
}

