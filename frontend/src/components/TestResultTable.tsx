import { Button, Table } from "antd";
import { EyeOutlined } from "@ant-design/icons";
import type { ColumnsType } from "antd/es/table";
import ProtocolBadge from "./ProtocolBadge";
import StatusBadge from "./StatusBadge";

export interface TestCaseResult {
  case_id?: string;
  name?: string;
  protocol?: string;
  service?: string;
  endpoint?: string;
  method?: string;
  status?: string;
  duration_ms?: number;
  request_payload?: unknown;
  response_payload?: unknown;
  expected_result?: string;
  actual_result?: string;
  error_message?: string;
}

interface TestResultTableProps {
  cases: TestCaseResult[];
  onSelect?: (testCase: TestCaseResult) => void;
}

export default function TestResultTable({ cases, onSelect }: TestResultTableProps) {
  const columns: ColumnsType<TestCaseResult> = [
    { title: "Case", dataIndex: "case_id", width: 110 },
    { title: "Name", dataIndex: "name" },
    {
      title: "Protocol",
      dataIndex: "protocol",
      width: 120,
      render: (protocol: string) => <ProtocolBadge protocol={protocol} />
    },
    { title: "Service", dataIndex: "service", width: 150 },
    {
      title: "Status",
      dataIndex: "status",
      width: 120,
      render: (status: string) => <StatusBadge status={status} />
    },
    {
      title: "Duration",
      dataIndex: "duration_ms",
      width: 110,
      render: (value: number) => `${value ?? 0} ms`
    },
    {
      title: "",
      width: 72,
      render: (_, row) => (
        <Button aria-label="View case detail" icon={<EyeOutlined />} size="small" onClick={() => onSelect?.(row)} />
      )
    }
  ];

  return <Table rowKey={(row) => row.case_id || row.name || Math.random().toString()} columns={columns} dataSource={cases} size="small" pagination={{ pageSize: 8 }} />;
}

