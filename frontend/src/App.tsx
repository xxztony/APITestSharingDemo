import {
  ApiOutlined,
  BarChartOutlined,
  CloudServerOutlined,
  DollarOutlined,
  ExperimentOutlined,
  FileSearchOutlined
} from "@ant-design/icons";
import { ConfigProvider, Layout, Menu, Typography, theme } from "antd";
import { useMemo, useState } from "react";
import Dashboard from "./pages/Dashboard";
import Orders from "./pages/Orders";
import Portfolio from "./pages/Portfolio";
import Pricing from "./pages/Pricing";
import TestRuns from "./pages/TestRuns";

const { Sider, Content } = Layout;
const { Text, Title } = Typography;

type PageKey = "dashboard" | "orders" | "portfolio" | "pricing" | "test-runs";

export default function App() {
  const [currentPage, setCurrentPage] = useState<PageKey>("dashboard");

  const page = useMemo(() => {
    switch (currentPage) {
      case "orders":
        return <Orders />;
      case "portfolio":
        return <Portfolio />;
      case "pricing":
        return <Pricing />;
      case "test-runs":
        return <TestRuns />;
      default:
        return <Dashboard />;
    }
  }, [currentPage]);

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: "#0f766e",
          colorInfo: "#2563eb",
          colorSuccess: "#16a34a",
          colorWarning: "#d97706",
          colorError: "#dc2626",
          borderRadius: 8,
          fontFamily:
            "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
        }
      }}
    >
      <Layout className="app-shell">
        <Sider width={248} className="sidebar" breakpoint="lg" collapsedWidth={72}>
          <div className="brand-panel">
            <div className="brand-mark">
              <ApiOutlined />
            </div>
            <div className="brand-copy">
              <Title level={5}>Trading QA</Title>
              <Text>API Demo Platform</Text>
            </div>
          </div>
          <Menu
            mode="inline"
            selectedKeys={[currentPage]}
            onClick={({ key }) => setCurrentPage(key as PageKey)}
            items={[
              { key: "dashboard", icon: <BarChartOutlined />, label: "Dashboard" },
              { key: "orders", icon: <FileSearchOutlined />, label: "Orders" },
              { key: "portfolio", icon: <DollarOutlined />, label: "Portfolio" },
              { key: "pricing", icon: <CloudServerOutlined />, label: "Pricing" },
              { key: "test-runs", icon: <ExperimentOutlined />, label: "Test Runs" }
            ]}
          />
        </Sider>
        <Layout>
          <Content className="content-shell">{page}</Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
}

