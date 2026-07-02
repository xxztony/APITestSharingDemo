import { Tag } from "antd";

const COLOR_BY_STATUS: Record<string, string> = {
  ACCEPTED: "green",
  NEW: "blue",
  CANCELLED: "orange",
  REJECTED: "red",
  PASSED: "green",
  FAILED: "red",
  SKIPPED: "default",
  RUNNING: "processing",
  COMPLETED: "green",
  NO_RUN: "default",
  OK: "green",
  NOT_FOUND: "red"
};

export default function StatusBadge({ status }: { status?: string }) {
  const value = status || "UNKNOWN";
  return <Tag color={COLOR_BY_STATUS[value] || "default"}>{value}</Tag>;
}

