import { Card, Typography } from "antd";

const { Text } = Typography;

interface JsonViewerProps {
  title?: string;
  value: unknown;
}

export default function JsonViewer({ title, value }: JsonViewerProps) {
  return (
    <Card className="json-card" size="small" title={title}>
      <pre className="json-viewer">
        <Text>{JSON.stringify(value ?? {}, null, 2)}</Text>
      </pre>
    </Card>
  );
}

