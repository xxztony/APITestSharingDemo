import { DeploymentUnitOutlined, ExperimentOutlined, LinkOutlined, ThunderboltOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Space, Tag, Typography } from "antd";
import { useState } from "react";
import { apiGet, apiPost, type ApiCallResult } from "../api/client";
import JsonViewer from "../components/JsonViewer";
import MetricCard from "../components/MetricCard";

const { Text, Title } = Typography;

const JAEGER_URL = "http://localhost:16686";
const tracedServices = ["bff", "order-service", "portfolio-service", "pricing-service", "test-runner-service"];

export default function Tracing() {
  const [lastAction, setLastAction] = useState("Ready");
  const [lastCall, setLastCall] = useState<ApiCallResult<unknown> | null>(null);
  const [loadingDashboard, setLoadingDashboard] = useState(false);
  const [loadingRegression, setLoadingRegression] = useState(false);

  async function generateDashboardTrace() {
    setLoadingDashboard(true);
    const result = await apiGet("/api/dashboard");
    setLoadingDashboard(false);
    setLastAction("Dashboard trace generated");
    setLastCall(result);
  }

  async function generateRegressionTrace() {
    setLoadingRegression(true);
    const result = await apiPost("/api/test-runs");
    setLoadingRegression(false);
    setLastAction("Regression trace generated");
    setLastCall(result);
  }

  return (
    <div className="page-stack">
      <div className="page-header">
        <div>
          <Text className="page-kicker">OpenTelemetry to Jaeger</Text>
          <Title level={2}>Tracing</Title>
        </div>
        <Button icon={<LinkOutlined />} href={JAEGER_URL} target="_blank" rel="noreferrer">
          Open Jaeger
        </Button>
      </div>

      {lastCall && !lastCall.ok ? <Alert type="error" showIcon message={lastCall.error?.message} description={lastCall.error?.errorCode} /> : null}

      <div className="metric-grid-four">
        <MetricCard title="Collector" value="OTLP gRPC :4317" icon={<DeploymentUnitOutlined />} tone="blue" />
        <MetricCard title="Jaeger UI" value="localhost:16686" icon={<LinkOutlined />} tone="teal" />
        <MetricCard title="Sampler" value="always_on" icon={<ThunderboltOutlined />} tone="amber" />
        <MetricCard title="Services" value={tracedServices.length} icon={<ExperimentOutlined />} tone="gray" />
      </div>

      <Card className="panel-card" title="Trace Actions">
        <Space wrap>
          <Button type="primary" icon={<ThunderboltOutlined />} loading={loadingDashboard} onClick={() => void generateDashboardTrace()}>
            Generate Dashboard Trace
          </Button>
          <Button icon={<ExperimentOutlined />} loading={loadingRegression} onClick={() => void generateRegressionTrace()}>
            Generate Regression Trace
          </Button>
        </Space>
      </Card>

      <Card className="panel-card" title="Service Names">
        <Space wrap>
          {tracedServices.map((service) => (
            <Tag color="cyan" key={service}>
              {service}
            </Tag>
          ))}
        </Space>
      </Card>

      <div className="two-column">
        <JsonViewer title="Last action" value={{ status: lastAction, statusCode: lastCall?.status, durationMs: lastCall?.durationMs }} />
        <JsonViewer title="Last response" value={lastCall?.raw} />
      </div>
    </div>
  );
}
