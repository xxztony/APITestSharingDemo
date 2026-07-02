import { CloudSyncOutlined, ThunderboltOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Empty, Select, Space, Table, Typography } from "antd";
import { useEffect, useMemo, useState } from "react";
import { apiGet, type ApiCallResult } from "../api/client";
import JsonViewer from "../components/JsonViewer";
import MetricCard from "../components/MetricCard";

const { Text, Title } = Typography;
const PRODUCTS = ["LME-CA", "LME-AL", "LME-ZN", "LME-NI", "BAD-PRODUCT"];
const MAX_HISTORY_POINTS = 36;
const CHART_WIDTH = 960;
const CHART_HEIGHT = 360;
const CHART_PADDING = { top: 30, right: 96, bottom: 54, left: 76 };

interface Price {
  product: string;
  bid: number;
  ask: number;
  mid: number;
  timestamp: string;
  source: string;
  proto?: ProtoMessage;
}

interface ProtoMessage {
  type: string;
  text: string;
  serializedBase64: string;
  serializedBytes: number;
}

interface StreamResponse {
  product: string;
  updates: Price[];
}

function formatPrice(value: number) {
  return value.toLocaleString(undefined, { maximumFractionDigits: 4 });
}

function formatSignedPrice(value: number) {
  const sign = value > 0 ? "+" : "";
  return `${sign}${formatPrice(value)}`;
}

function formatTime(timestamp: string) {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return timestamp;
  }
  return date.toLocaleTimeString([], { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function formatTickTime(timestamp: string) {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return timestamp;
  }
  const milliseconds = date.getMilliseconds().toString().padStart(3, "0");
  return `${formatTime(timestamp)}.${milliseconds}`;
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

function ProtoMessageViewer({ proto }: { proto?: ProtoMessage }) {
  return (
    <Card className="json-card proto-card" size="small" title="Original protobuf message">
      {proto ? (
        <>
          <div className="proto-meta">
            <Text type="secondary">Type</Text>
            <Text strong>{proto.type}</Text>
            <Text type="secondary">Bytes</Text>
            <Text strong>{proto.serializedBytes}</Text>
          </div>
          <pre className="json-viewer proto-viewer">
            <Text>{proto.text}</Text>
          </pre>
          <pre className="proto-base64">
            <Text>{proto.serializedBase64}</Text>
          </pre>
        </>
      ) : (
        <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="Call a valid product to inspect the raw protobuf response" />
      )}
    </Card>
  );
}

function makeLinePath(points: Array<{ x: number; y: number }>) {
  return points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" ");
}

function QuoteMarketChart({ history }: { history: Price[] }) {
  const innerWidth = CHART_WIDTH - CHART_PADDING.left - CHART_PADDING.right;
  const innerHeight = CHART_HEIGHT - CHART_PADDING.top - CHART_PADDING.bottom;
  const midX = CHART_PADDING.left + innerWidth / 2;
  const latest = history[history.length - 1];
  const previous = history[history.length - 2];

  if (!latest) {
    return <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No quote ticks yet" />;
  }

  const values = history.flatMap((item) => [item.bid, item.ask, item.mid]);
  const rawMin = Math.min(...values);
  const rawMax = Math.max(...values);
  const rawRange = Math.max(rawMax - rawMin, 1);
  const spreadPad = Math.max(latest.ask - latest.bid, 1) * 0.7;
  const pad = Math.max(rawRange * 0.16, spreadPad);
  const min = rawMin - pad;
  const max = rawMax + pad;
  const range = max - min || 1;
  const change = previous ? latest.mid - previous.mid : 0;
  const changePercent = previous ? (change / previous.mid) * 100 : 0;
  const isUp = change >= 0;

  const xForIndex = (index: number) => {
    if (history.length === 1) {
      return midX;
    }
    return CHART_PADDING.left + (index / (history.length - 1)) * innerWidth;
  };
  const yForValue = (value: number) => CHART_PADDING.top + ((max - value) / range) * innerHeight;

  const bidPoints = history.map((item, index) => ({ x: xForIndex(index), y: yForValue(item.bid) }));
  const askPoints = history.map((item, index) => ({ x: xForIndex(index), y: yForValue(item.ask) }));
  const midPoints = history.map((item, index) => ({ x: xForIndex(index), y: yForValue(item.mid) }));
  const spreadArea = [...askPoints, ...bidPoints.slice().reverse()]
    .map((point) => `${point.x},${point.y}`)
    .join(" ");
  const gridValues = Array.from({ length: 5 }, (_, index) => max - (index / 4) * range);
  const xLabels = history.length > 2 ? [0, Math.floor((history.length - 1) / 2), history.length - 1] : [0, history.length - 1];
  const uniqueXLabels = Array.from(new Set(xLabels));
  const latestY = yForValue(latest.mid);
  const latestX = xForIndex(history.length - 1);

  return (
    <div className="market-chart">
      <div className="market-chart-stats">
        <div>
          <Text type="secondary">Last Mid</Text>
          <strong>{formatPrice(latest.mid)}</strong>
        </div>
        <div className={isUp ? "market-up" : "market-down"}>
          <Text type="secondary">Change</Text>
          <strong>
            {formatSignedPrice(change)} ({formatSignedPrice(changePercent)}%)
          </strong>
        </div>
        <div>
          <Text type="secondary">Bid / Ask</Text>
          <strong>
            {formatPrice(latest.bid)} / {formatPrice(latest.ask)}
          </strong>
        </div>
        <div>
          <Text type="secondary">Spread</Text>
          <strong>{formatPrice(latest.ask - latest.bid)}</strong>
        </div>
      </div>

      <svg className="quote-chart" viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} role="img" aria-label="Bid ask mid quote chart">
        <defs>
          <linearGradient id="quoteSpreadFill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#14b8a6" stopOpacity="0.2" />
            <stop offset="100%" stopColor="#2563eb" stopOpacity="0.08" />
          </linearGradient>
          <filter id="lastPriceShadow" x="-20%" y="-40%" width="140%" height="180%">
            <feDropShadow dx="0" dy="2" stdDeviation="2" floodColor="#0f172a" floodOpacity="0.18" />
          </filter>
        </defs>

        <rect
          x={CHART_PADDING.left}
          y={CHART_PADDING.top}
          width={innerWidth}
          height={innerHeight}
          rx="8"
          className="quote-chart-plot"
        />

        {gridValues.map((value) => {
          const y = yForValue(value);
          return (
            <g key={value}>
              <line x1={CHART_PADDING.left} x2={CHART_WIDTH - CHART_PADDING.right} y1={y} y2={y} className="quote-grid-line" />
              <text x={CHART_PADDING.left - 12} y={y + 4} textAnchor="end" className="quote-axis-label">
                {formatPrice(value)}
              </text>
            </g>
          );
        })}

        {uniqueXLabels.map((index) => {
          const item = history[index];
          const x = xForIndex(index);
          return (
            <g key={`${item.timestamp}-${index}`}>
              <line x1={x} x2={x} y1={CHART_PADDING.top} y2={CHART_PADDING.top + innerHeight} className="quote-grid-line quote-grid-line-vertical" />
              <text x={x} y={CHART_HEIGHT - 18} textAnchor="middle" className="quote-axis-label">
                {formatTickTime(item.timestamp)}
              </text>
            </g>
          );
        })}

        <polygon points={spreadArea} className="quote-spread-area" />
        <path d={makeLinePath(askPoints)} className="quote-line quote-line-ask" />
        <path d={makeLinePath(bidPoints)} className="quote-line quote-line-bid" />
        <path d={makeLinePath(midPoints)} className="quote-line quote-line-mid" />

        {history.map((item, index) => {
          const x = xForIndex(index);
          const bidY = yForValue(item.bid);
          const askY = yForValue(item.ask);
          const midY = yForValue(item.mid);
          const directionUp = index === 0 ? true : item.mid >= history[index - 1].mid;
          return (
            <g key={`${item.timestamp}-${item.mid}`} className={directionUp ? "quote-tick quote-tick-up" : "quote-tick quote-tick-down"}>
              <line x1={x} x2={x} y1={askY} y2={bidY} />
              <line x1={x - 5} x2={x + 5} y1={askY} y2={askY} />
              <line x1={x - 5} x2={x + 5} y1={bidY} y2={bidY} />
              <circle cx={x} cy={midY} r={3.5} />
            </g>
          );
        })}

        <line x1={latestX} x2={CHART_WIDTH - CHART_PADDING.right + 18} y1={latestY} y2={latestY} className="quote-last-guide" />
        <g filter="url(#lastPriceShadow)">
          <rect x={CHART_WIDTH - CHART_PADDING.right + 20} y={latestY - 14} width="72" height="28" rx="14" className={isUp ? "quote-last-price-up" : "quote-last-price-down"} />
          <text x={CHART_WIDTH - CHART_PADDING.right + 56} y={latestY + 5} textAnchor="middle" className="quote-last-price-text">
            {formatPrice(latest.mid)}
          </text>
        </g>
      </svg>

      <div className="quote-tape">
        {history.slice(-12).map((item, index, recent) => {
          const prev = recent[index - 1];
          const up = !prev || item.mid >= prev.mid;
          return (
            <div className={up ? "quote-tape-cell quote-tape-up" : "quote-tape-cell quote-tape-down"} key={`${item.timestamp}-${item.mid}`}>
              <Text type="secondary">{formatTime(item.timestamp)}</Text>
              <strong>{formatPrice(item.mid)}</strong>
            </div>
          );
        })}
      </div>
    </div>
  );
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
        title={
          <div className="market-chart-title">
            <span>{product} quote tape</span>
            <span>Bid / Ask / Mid</span>
          </div>
        }
        extra={<Text type="secondary">{currentHistory.length ? `${currentHistory.length} ticks` : "No ticks yet"}</Text>}
      >
        {currentHistory.length ? (
          <QuoteMarketChart history={currentHistory} />
        ) : (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="Select a valid product or run the stream demo to plot market ticks"
          />
        )}
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

      <div className="evidence-grid">
        <JsonViewer title="BFF request" value={lastPayload} />
        <ProtoMessageViewer proto={price?.proto} />
        <JsonViewer title="gRPC response as JSON" value={lastCall?.raw} />
      </div>
    </div>
  );
}
