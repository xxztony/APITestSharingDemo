import { Tag } from "antd";

export default function ProtocolBadge({ protocol }: { protocol?: string }) {
  const value = protocol || "UNKNOWN";
  const normalized = value.toLowerCase();
  const color = normalized.includes("graphql") ? "magenta" : normalized.includes("grpc") ? "geekblue" : "green";
  return <Tag color={color}>{value}</Tag>;
}

