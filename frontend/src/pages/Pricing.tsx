import { CloudSyncOutlined, ThunderboltOutlined } from "@ant-design/icons";
import type { LineConfig } from "@ant-design/charts";
import { Alert, Button, Card, Empty, Select, Space, Table, Typography } from "antd";
import { lazy, Suspense, useEffect, useMemo, useState } from "react";
import { apiGet, type ApiCallResult } from "../api/client";
import JsonViewer from "../components/JsonViewer";
import MetricCard from "../components/MetricCard";

const { Text, Title } = Typography;
const LineChart = lazy(() => import("@ant-design/charts").then((module) => ({ default: module.Line })));
const PRODUCTS = ["LME-CA", "LME-AL", "LME-ZN", "LME-NI", "BAD-PRODUCT"];
const MAX_HISTORY_POINTS = 36;

interface Price {
  product: string;
  bid: number;
  ask: number;
  mid: number;
  timestamp: string;
  source: string;
}

interface StreamResponse {
  product: string;
  updates: Price[];
}

interface ChartPoint {
  timeLabel: string;
  series: "Bid" | "Ask" | "Mid";
  value: number;
}

function formatPrice(value: number) {
  return value.toLocaleString(undefined, { maximumFractionDigits: 4 });
}

function formatTime(timestamp: string) {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return timestamp;
  }
  return date.toLocaleTimeString([], { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function appendHistory(history: Record<string, Price[]>, selectedProduct: string, updates: Price[]) {
  const existing = history[selectedProduct] || [];
  const validUpdates = updates.filter((update) => update.product === selectedProduct);
  const merged = [...existing, ...validUpdates];
  const unique = Array.from(new Map(merged.map((item) => [`${item.timestamp}-${item.mid}`, item])).values());
  return {
    ...history,
    [selectedProduct]: unique.slice(-MAX_HISTORY_POINTS)
  };
}

export default function Pricing() {
  const [product, setProduct] = useState("LME-CA");
  const [latestPriceByProduct, setLatestPriceByProduct] = useState<Record<string, Price>>({});
  const [stream, setStream] = useState<StreamResponse | null>(null);
  const [priceHistory, setPriceHistory] = useState<Record<string, Price[]>>({});
  const [lastCall, setLastCall] = useState<ApiCallResult<unknown> | null>(null);
  const [lastPayload, setLastPayload] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);

  const currentHistory = priceHistory[product] || [];
  const price = latestPriceByProduct[product] || null;

  const chartData = useMemo<ChartPoint[]>(
    () =>
      currentHistory.flatMap((item) => {
        const timeLabel = formatTime(item.timestamp);
        return [
          { timeLabel, series: "Bid", value: item.bid },
          { timeLabel, series: "Ask", value: item.ask },
          { timeLabel, series: "Mid", value: item.mid }
        ];
      }),
    [currentHistory]
  );

  const chartConfig = useMemo<LineConfig>(
    () => ({
      data: chartData,
      xField: "timeLabel",
      yField: "value",
      colorField: "series",
      height: 300,
      color: ["#0f766e", "#2563eb", "#475569"],
      axis: {
        x: { title: false, labelAutoHide: true },
        y: { title: "Price" }
      },
      scale: {
        y: { nice: true }
      },
      legend: {
        color: {
          position: "top",
          layout: { justifyContent: "center" }
        }
      },
      point: {
        sizeField: 3,
        shapeField: "circle"
      },
      style: {
        lineWidth: 2
      },
      tooltip: {
        title: "timeLabel"
      }
    }),
    [chartData]
  );

  async function getLatestPrice(selectedProduct = product) {
    setLoading(true);
    const result = await apiGet<Price>(`/api/pricing/${selectedProduct}`);
    setLoading(false);
    setLastCall(result);
    setLastPayload({ method: "GET", path: `/api/pricing/${selectedProduct}`, internalProtocol: "gRPC unary" });
    if (result.ok && result.data) {
      setLatestPriceByProduct((latest) => ({ ...latest, [selectedProduct]: result.data as Price }));
      setPriceHistory((history) => appendHistory(history, selectedProduct, [result.data as Price]));
    }
  }

  async function runStreamDemo() {
    setLoading(true);
    const result = await apiGet<StreamResponse>(`/api/pricing/${product}/stream-demo`);
    setLoading(false);
    setLastCall(result);
    setLastPayload({ method: "GET", path: `/api/pricing/${product}/stream-demo`, internalProtocol: "gRPC server streaming" });
    if (result.ok && result.data) {
      setStream(result.data);
      const latestStreamPrice = result.data.updates[result.data.updates.length - 1];
      if (latestStreamPrice) {
        setLatestPriceByProduct((latest) => ({ ...latest, [product]: latestStreamPrice }));
      }
      setPriceHistory((history) => appendHistory(history, product, result.data?.updates || []));
    }
  }

  useEffect(() => {
    setStream(null);
    void getLatestPrice(product);
  }, [product]);

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
            value={product}
            onChange={setProduct}
            options={PRODUCTS.map((value) => ({ value, label: value }))}
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

      <Card
        className="panel-card price-chart-card"
        title={`${product} market chart`}
        extra={<Text type="secondary">{currentHistory.length ? `${currentHistory.length} ticks` : "No ticks yet"}</Text>}
      >
        {chartData.length ? (
          <Suspense fallback={<div className="chart-loading">Loading chart...</div>}>
            <LineChart {...chartConfig} />
          </Suspense>
        ) : (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="Select a valid product or run the stream demo to plot market ticks"
          />
        )}
        {price ? (
          <div className="price-chart-summary">
            <Text type="secondary">Last tick</Text>
            <Text strong>{formatTime(price.timestamp)}</Text>
            <Text type="secondary">Spread</Text>
            <Text strong>{formatPrice(price.ask - price.bid)}</Text>
          </div>
        ) : null}
      </Card>

      {stream ? (
        <Table
          rowKey="timestamp"
          title={() => `Stream updates for ${stream.product}`}
          dataSource={stream.updates}
          size="small"
          columns={[
            { title: "Product", dataIndex: "product" },
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
