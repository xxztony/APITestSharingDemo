import {
  ApiOutlined,
  BarChartOutlined,
  CloudServerOutlined,
  DeploymentUnitOutlined,
  DollarOutlined,
  ExperimentOutlined,
  FileSearchOutlined,
  LogoutOutlined,
  UserOutlined
} from "@ant-design/icons";
import { Button, ConfigProvider, Layout, Menu, Typography, theme } from "antd";
import { useMemo, useState } from "react";
import Dashboard from "./pages/Dashboard";
import Orders from "./pages/Orders";
import Portfolio from "./pages/Portfolio";
import Pricing from "./pages/Pricing";
import TestRuns from "./pages/TestRuns";
import Tracing from "./pages/Tracing";
import { keycloak } from "./auth/keycloak";

const { Sider, Content } = Layout;
const { Text, Title } = Typography;

type PageKey = "dashboard" | "orders" | "portfolio" | "pricing" | "test-runs" | "tracing";

export default function App() {
  const [currentPage, setCurrentPage] = useState<PageKey>("dashboard");
  const username = keycloak.tokenParsed?.preferred_username || "Signed in";
  const displayName = keycloak.tokenParsed?.name || username;

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
      case "tracing":
        return <Tracing />;
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
              { key: "test-runs", icon: <ExperimentOutlined />, label: "Test Runs" },
              { key: "tracing", icon: <DeploymentUnitOutlined />, label: "Tracing" }
            ]}
          />
          <div className="session-panel">
            <div className="session-avatar" aria-hidden="true">
              <UserOutlined />
            </div>
            <div className="session-copy">
              <Text title={displayName}>{displayName}</Text>
              <Text title={username}>{username}</Text>
            </div>
            <Button
              type="text"
              icon={<LogoutOutlined />}
              aria-label="Sign out"
              title="Sign out"
              onClick={() => void keycloak.logout({ redirectUri: window.location.origin })}
            />
          </div>
        </Sider>
        <Layout>
          <Content className="content-shell">{page}</Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
}
