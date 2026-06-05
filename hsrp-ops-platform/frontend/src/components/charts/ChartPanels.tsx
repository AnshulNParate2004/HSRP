import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const COLORS = ["#3b82f6", "#f97316", "#10b981", "#8b5cf6", "#ef4444", "#06b6d4", "#eab308", "#ec4899"];

interface BarChartPanelProps {
  title: string;
  data: { name: string; value: number; secondary?: number }[];
  valueKey?: string;
  secondaryKey?: string;
  valueLabel?: string;
  secondaryLabel?: string;
  formatValue?: (v: number) => string;
}

export function BarChartPanel({
  title,
  data,
  valueKey = "value",
  secondaryKey,
  valueLabel = "Value",
  secondaryLabel = "Secondary",
  formatValue = (v) => String(v),
}: BarChartPanelProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-35} textAnchor="end" height={60} />
            <YAxis tick={{ fontSize: 10 }} tickFormatter={(v) => formatValue(v)} />
            <Tooltip formatter={(v: number) => formatValue(v)} />
            <Bar dataKey={valueKey} name={valueLabel} fill="#3b82f6" radius={[4, 4, 0, 0]} />
            {secondaryKey && (
              <Bar dataKey={secondaryKey} name={secondaryLabel} fill="#f97316" radius={[4, 4, 0, 0]} />
            )}
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

export function LineChartPanel({
  title,
  data,
  lines,
}: {
  title: string;
  data: Array<Record<string, string | number>>;
  lines: { key: string; label: string; color?: string }[];
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="period" tick={{ fontSize: 10 }} />
            <YAxis tick={{ fontSize: 10 }} />
            <Tooltip />
            {lines.map((l) => (
              <Line key={l.key} type="monotone" dataKey={l.key} name={l.label} stroke={l.color ?? "#3b82f6"} strokeWidth={2} dot={false} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

export function PieChartPanel({
  title,
  data,
}: {
  title: string;
  data: { name: string; value: number }[];
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
              {data.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
