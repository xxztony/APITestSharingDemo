import { DollarOutlined, SaveOutlined, SearchOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Form, InputNumber, Select, Space, Table, Typography } from "antd";
import { useEffect, useState } from "react";
import { apiGet, apiPost, type ApiCallResult } from "../api/client";
import JsonViewer from "../components/JsonViewer";
import MetricCard from "../components/MetricCard";

const { Text, Title } = Typography;

interface Position {
  symbol: string;
  quantity: number;
  averagePrice: number;
  marketValue: number;
}

interface PortfolioData {
  accountId: string;
  cashBalance: number;
  riskLimit: number;
  usedLimit: number;
  availableLimit: number;
  positions: Position[];
}

export default function Portfolio() {
  const [accountId, setAccountId] = useState("ACC001");
  const [riskLimit, setRiskLimit] = useState<number | null>(3200000);
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);
  const [lastCall, setLastCall] = useState<ApiCallResult<unknown> | null>(null);
  const [lastPayload, setLastPayload] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);

  async function loadPortfolio(nextAccountId = accountId) {
    setLoading(true);
    const result = await apiGet<PortfolioData>(`/api/portfolio/${nextAccountId}`);
    setLoading(false);
    setLastCall(result);
    setLastPayload({ method: "GET", path: `/api/portfolio/${nextAccountId}` });
    if (result.ok && result.data) {
      setPortfolio(result.data);
      setRiskLimit(result.data.riskLimit);
    }
  }

  async function saveRiskLimit() {
    if (!riskLimit) {
      return;
    }
    setLoading(true);
    const payload = { limit: riskLimit };
    const result = await apiPost<PortfolioData>(`/api/portfolio/${accountId}/risk-limit`, payload);
    setLoading(false);
    setLastCall(result);
    setLastPayload(payload);
    if (result.ok && result.data) {
      setPortfolio(result.data);
    }
  }

  useEffect(() => {
    void loadPortfolio("ACC001");
  }, []);

  return (
    <div className="page-stack">
      <div className="page-header">
        <div>
          <Text className="page-kicker">GraphQL converted to JSON by BFF</Text>
          <Title level={2}>Portfolio</Title>
        </div>
      </div>

      <Card className="panel-card">
        <Space wrap>
          <Select
            aria-label="Account"
            value={accountId}
            onChange={(value) => {
              setAccountId(value);
              void loadPortfolio(value);
            }}
            options={["ACC001", "ACC002", "ACC003", "ACC-NOT-FOUND"].map((value) => ({ value, label: value }))}
            className="control-wide"
          />
          <Button icon={<SearchOutlined />} onClick={() => void loadPortfolio()} loading={loading}>
            Query
          </Button>
          <InputNumber value={riskLimit} min={1} step={10000} onChange={setRiskLimit} className="control-wide" />
          <Button type="primary" icon={<SaveOutlined />} onClick={() => void saveRiskLimit()} loading={loading}>
            Update Risk Limit
          </Button>
        </Space>
      </Card>

      {lastCall && !lastCall.ok ? <Alert type="error" showIcon message={lastCall.error?.message} /> : null}

      {portfolio ? (
        <>
          <div className="metric-grid-four">
            <MetricCard title="Cash balance" value={`$${portfolio.cashBalance.toLocaleString()}`} icon={<DollarOutlined />} tone="teal" />
            <MetricCard title="Risk limit" value={`$${portfolio.riskLimit.toLocaleString()}`} tone="blue" />
            <MetricCard title="Used limit" value={`$${portfolio.usedLimit.toLocaleString()}`} tone="amber" />
            <MetricCard title="Available limit" value={`$${portfolio.availableLimit.toLocaleString()}`} tone="gray" />
          </div>
          <Table
            rowKey="symbol"
            size="small"
            dataSource={portfolio.positions}
            columns={[
              { title: "Symbol", dataIndex: "symbol" },
              { title: "Quantity", dataIndex: "quantity" },
              { title: "Average Price", dataIndex: "averagePrice" },
              { title: "Market Value", dataIndex: "marketValue", render: (value) => `$${Number(value).toLocaleString()}` }
            ]}
          />
        </>
      ) : null}

      <div className="two-column">
        <JsonViewer title="BFF request" value={lastPayload} />
        <JsonViewer title="BFF response" value={lastCall?.raw} />
      </div>
    </div>
  );
}

