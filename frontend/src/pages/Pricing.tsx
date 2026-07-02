import { CloudSyncOutlined, ThunderboltOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Select, Space, Table, Typography } from "antd";
import { useState } from "react";
import { apiGet, type ApiCallResult } from "../api/client";
import JsonViewer from "../components/JsonViewer";
import MetricCard from "../components/MetricCard";

const { Text, Title } = Typography;

interface Price {
  symbol: string;
  bid: number;
  ask: number;
  mid: number;
  timestamp: string;
  source: string;
}

interface StreamResponse {
  symbol: string;
  updates: Price[];
}

export default function Pricing() {
  const [symbol, setSymbol] = useState("LME-CA");
  const [price, setPrice] = useState<Price | null>(null);
  const [stream, setStream] = useState<StreamResponse | null>(null);
  const [lastCall, setLastCall] = useState<ApiCallResult<unknown> | null>(null);
  const [lastPayload, setLastPayload] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);

  async function getLatestPrice() {
    setLoading(true);
    const result = await apiGet<Price>(`/api/pricing/${symbol}`);
    setLoading(false);
    setLastCall(result);
    setLastPayload({ method: "GET", path: `/api/pricing/${symbol}`, internalProtocol: "gRPC unary" });
    if (result.ok && result.data) {
      setPrice(result.data);
    }
  }

  async function runStreamDemo() {
    setLoading(true);
    const result = await apiGet<StreamResponse>(`/api/pricing/${symbol}/stream-demo`);
    setLoading(false);
    setLastCall(result);
    setLastPayload({ method: "GET", path: `/api/pricing/${symbol}/stream-demo`, internalProtocol: "gRPC server streaming" });
    if (result.ok && result.data) {
      setStream(result.data);
    }
  }

  return (
    <div className="page-stack">
      <div className="page-header">
        <div>
          <Text className="page-kicker">gRPC response converted by BFF</Text>
          <Title level={2}>Pricing</Title>
        </div>
      </div>

      <Card className="panel-card">
        <Space wrap>
          <Select
            value={symbol}
            onChange={setSymbol}
            options={["LME-CA", "LME-AL", "LME-ZN", "LME-NI", "BAD-SYMBOL"].map((value) => ({ value, label: value }))}
            className="control-wide"
          />
          <Button type="primary" icon={<ThunderboltOutlined />} onClick={() => void getLatestPrice()} loading={loading}>
            Get Latest Price
          </Button>
          <Button icon={<CloudSyncOutlined />} onClick={() => void runStreamDemo()} loading={loading}>
            Stream Demo
          </Button>
        </Space>
      </Card>

      {lastCall && !lastCall.ok ? <Alert type="error" showIcon message={lastCall.error?.message} description={lastCall.error?.errorCode} /> : null}

      {price ? (
        <div className="metric-grid-four">
          <MetricCard title="Bid" value={price.bid} tone="teal" />
          <MetricCard title="Ask" value={price.ask} tone="blue" />
          <MetricCard title="Mid" value={price.mid} tone="gray" />
          <MetricCard title="Source" value={price.source} tone="amber" />
        </div>
      ) : null}

      {stream ? (
        <Table
          rowKey="timestamp"
          title={() => `Stream updates for ${stream.symbol}`}
          dataSource={stream.updates}
          size="small"
          columns={[
            { title: "Symbol", dataIndex: "symbol" },
            { title: "Bid", dataIndex: "bid" },
            { title: "Ask", dataIndex: "ask" },
            { title: "Mid", dataIndex: "mid" },
            { title: "Timestamp", dataIndex: "timestamp" }
          ]}
        />
      ) : null}

      <div className="two-column">
        <JsonViewer title="BFF request" value={lastPayload} />
        <JsonViewer title="gRPC response as JSON" value={lastCall?.raw} />
      </div>
    </div>
  );
}

