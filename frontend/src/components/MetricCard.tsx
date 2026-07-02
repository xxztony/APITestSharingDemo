import { Card, Typography } from "antd";
import type { ReactNode } from "react";

const { Text, Title } = Typography;

type Tone = "teal" | "blue" | "amber" | "red" | "gray";

interface MetricCardProps {
  title: string;
  value: ReactNode;
  subtitle?: string;
  icon?: ReactNode;
  tone?: Tone;
}

export default function MetricCard({ title, value, subtitle, icon, tone = "teal" }: MetricCardProps) {
  return (
    <Card className={`metric-card metric-card-${tone}`} variant="borderless">
      <div className="metric-card-top">
        <Text type="secondary">{title}</Text>
        {icon ? <span className="metric-icon">{icon}</span> : null}
      </div>
      <Title level={3}>{value}</Title>
      {subtitle ? <Text type="secondary">{subtitle}</Text> : null}
    </Card>
  );
}
