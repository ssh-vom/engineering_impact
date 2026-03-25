import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts"
import type { ScoreBreakdown as BreakdownType } from "../types"

const COLORS = ["#6366f1", "#8b5cf6", "#06b6d4"]

export function ScoreBreakdown({ breakdown }: { breakdown: BreakdownType }) {
  const data = [
    { name: "Merged", score: breakdown.mergedPrsScore },
    { name: "Meaningful", score: breakdown.meaningfulPrsScore },
    { name: "Reviews", score: breakdown.reviewsGivenScore },
  ]

  return (
    <div className="score-breakdown">
      <span className="section-label">Score Breakdown</span>
      <ResponsiveContainer width="100%" height={68}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 2, right: 4, bottom: 2, left: 0 }}
        >
          <XAxis type="number" domain={[0, 100]} hide />
          <YAxis
            type="category"
            dataKey="name"
            width={62}
            tick={{ fontSize: 10, fill: "#6e6e73" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            formatter={(value: number) => [`${value.toFixed(1)}`, "Score"]}
            contentStyle={{
              fontSize: 11,
              borderRadius: 8,
              border: "none",
              boxShadow: "0 2px 8px rgba(0,0,0,0.12)",
            }}
          />
          <Bar dataKey="score" radius={[0, 4, 4, 0]} barSize={12}>
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
