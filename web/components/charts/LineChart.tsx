'use client';

import { useState } from 'react';
import {
  LineChart as RechartsLine,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format, parseISO, subDays } from 'date-fns';
import type { ScansByDay } from '@/types';

interface LineChartProps {
  data: ScansByDay[];
}

export default function LineChart({ data }: LineChartProps) {
  const [range, setRange] = useState<7 | 30>(30);

  const filtered = (() => {
    const cutoff = subDays(new Date(), range);
    return data
      .filter((d) => {
        try {
          return parseISO(d.date) >= cutoff;
        } catch {
          return true;
        }
      })
      .map((d) => ({
        ...d,
        label: (() => {
          try {
            return format(parseISO(d.date), 'MMM d');
          } catch {
            return d.date;
          }
        })(),
      }));
  })();

  return (
    <div>
      {/* Toggle */}
      <div className="flex justify-end gap-2 mb-4">
        {([7, 30] as const).map((r) => (
          <button
            key={r}
            onClick={() => setRange(r)}
            className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
              range === r
                ? 'bg-accent text-white'
                : 'bg-background-secondary text-muted hover:text-white border border-border'
            }`}
          >
            {r}d
          </button>
        ))}
      </div>

      <ResponsiveContainer width="100%" height={260}>
        <RechartsLine data={filtered}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
          <XAxis dataKey="label" tick={{ fontSize: 11, fill: '#6B7280' }} />
          <YAxis tick={{ fontSize: 11, fill: '#6B7280' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1A2234',
              border: '1px solid #1F2937',
              borderRadius: '12px',
              color: '#fff',
            }}
          />
          <Legend wrapperStyle={{ fontSize: '12px' }} />
          <Line
            type="monotone"
            dataKey="count"
            name="Total Scans"
            stroke="#3B82F6"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
          <Line
            type="monotone"
            dataKey="high_risk"
            name="High Risk"
            stroke="#EF4444"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        </RechartsLine>
      </ResponsiveContainer>
    </div>
  );
}
