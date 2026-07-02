import { EyeOutlined, PlusOutlined, StopOutlined, SyncOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Drawer, Form, Input, InputNumber, Select, Space, Table, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { useEffect, useState } from "react";
import { apiGet, apiPatch, apiPost, type ApiCallResult } from "../api/client";
import JsonViewer from "../components/JsonViewer";
import StatusBadge from "../components/StatusBadge";

const { Text, Title } = Typography;

interface Order {
  orderId: string;
  accountId: string;
  symbol: string;
  side: "BUY" | "SELL";
  quantity: number;
  price: number;
  status: string;
  createdAt?: string;
  updatedAt?: string;
  rejectReason?: string | null;
}

interface OrderForm {
  accountId: string;
  symbol: string;
  side: "BUY" | "SELL";
  quantity: number;
  price: number;
}

export default function Orders() {
  const [form] = Form.useForm<OrderForm>();
  const [orders, setOrders] = useState<Order[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [lastCall, setLastCall] = useState<ApiCallResult<unknown> | null>(null);
  const [lastPayload, setLastPayload] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);

  async function loadOrders() {
    setLoading(true);
    const result = await apiGet<Order[]>("/api/orders");
    setLoading(false);
    setLastCall(result);
    setLastPayload({ method: "GET", path: "/api/orders" });
    if (result.ok && result.data) {
      setOrders(result.data);
    }
  }

  async function createOrder(values: OrderForm) {
    setLoading(true);
    const result = await apiPost<Order>("/api/orders", values);
    setLoading(false);
    setLastCall(result);
    setLastPayload(values);
    if (result.ok) {
      form.resetFields();
      await loadOrders();
    }
  }

  async function createInvalidOrder() {
    const payload = { accountId: "ACC001", symbol: "LME-CA", side: "BUY", quantity: -1, price: 9125.5 };
    setLoading(true);
    const result = await apiPost<Order>("/api/orders", payload);
    setLoading(false);
    setLastCall(result);
    setLastPayload(payload);
  }

  async function cancelOrder(orderId: string) {
    setLoading(true);
    const result = await apiPatch<Order>(`/api/orders/${orderId}/cancel`);
    setLoading(false);
    setLastCall(result);
    setLastPayload({ method: "PATCH", path: `/api/orders/${orderId}/cancel` });
    if (result.ok) {
      await loadOrders();
    }
  }

  useEffect(() => {
    void loadOrders();
  }, []);

  const columns: ColumnsType<Order> = [
    { title: "Order ID", dataIndex: "orderId", width: 190 },
    { title: "Account", dataIndex: "accountId", width: 110 },
    { title: "Symbol", dataIndex: "symbol", width: 110 },
    { title: "Side", dataIndex: "side", width: 90 },
    { title: "Qty", dataIndex: "quantity", width: 90 },
    { title: "Price", dataIndex: "price", width: 110 },
    { title: "Status", dataIndex: "status", width: 130, render: (status) => <StatusBadge status={status} /> },
    {
      title: "Actions",
      width: 132,
      render: (_, row) => (
        <Space>
          <Button aria-label="View order" icon={<EyeOutlined />} size="small" onClick={() => setSelectedOrder(row)} />
          <Button
            aria-label="Cancel order"
            icon={<StopOutlined />}
            size="small"
            disabled={!["NEW", "ACCEPTED"].includes(row.status)}
            onClick={() => void cancelOrder(row.orderId)}
          />
        </Space>
      )
    }
  ];

  return (
    <div className="page-stack">
      <div className="page-header">
        <div>
          <Text className="page-kicker">REST API through BFF</Text>
          <Title level={2}>Orders</Title>
        </div>
        <Button icon={<SyncOutlined />} onClick={loadOrders} loading={loading}>
          Refresh
        </Button>
      </div>

      <Card title="Create Order" className="panel-card">
        <Form
          form={form}
          layout="vertical"
          className="order-form-grid"
          initialValues={{ accountId: "ACC001", symbol: "LME-CA", side: "BUY", quantity: 10, price: 9125.5 }}
          onFinish={(values) => void createOrder(values)}
        >
          <Form.Item label="Account" name="accountId" rules={[{ required: true }]}>
            <Select options={["ACC001", "ACC002", "ACC003"].map((value) => ({ value, label: value }))} />
          </Form.Item>
          <Form.Item label="Symbol" name="symbol" rules={[{ required: true }]}>
            <Select options={["LME-CA", "LME-AL", "LME-ZN", "LME-NI"].map((value) => ({ value, label: value }))} />
          </Form.Item>
          <Form.Item label="Side" name="side" rules={[{ required: true }]}>
            <Select options={["BUY", "SELL"].map((value) => ({ value, label: value }))} />
          </Form.Item>
          <Form.Item label="Quantity" name="quantity" rules={[{ required: true }]}>
            <InputNumber min={1} className="full-width" />
          </Form.Item>
          <Form.Item label="Price" name="price" rules={[{ required: true }]}>
            <InputNumber min={0.01} step={0.01} className="full-width" />
          </Form.Item>
          <Form.Item label=" ">
            <Space wrap>
              <Button type="primary" htmlType="submit" icon={<PlusOutlined />} loading={loading}>
                Create
              </Button>
              <Button danger icon={<StopOutlined />} onClick={() => void createInvalidOrder()} loading={loading}>
                Invalid Order
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      {lastCall && !lastCall.ok ? (
        <Alert type="error" showIcon message={lastCall.error?.message} description={lastCall.error?.errorCode} />
      ) : null}

      <Table rowKey="orderId" columns={columns} dataSource={orders} loading={loading} scroll={{ x: 950 }} size="small" />

      <div className="two-column">
        <JsonViewer title="Request payload" value={lastPayload} />
        <JsonViewer
          title={`Response payload ${lastCall ? `HTTP ${lastCall.status}, ${lastCall.durationMs} ms` : ""}`}
          value={lastCall?.raw}
        />
      </div>

      <Drawer title="Order Detail" open={!!selectedOrder} width={560} onClose={() => setSelectedOrder(null)}>
        <JsonViewer value={selectedOrder} />
      </Drawer>
    </div>
  );
}

