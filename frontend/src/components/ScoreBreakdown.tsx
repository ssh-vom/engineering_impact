import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  ResponsiveContainer,
} from "recharts"
import type { ScoreBreakdown as BreakdownType } from "../types"

export function ScoreBreakdown({ breakdown }: { breakdown: BreakdownType }) {
  const data = [
    { axis: "Shipped", value: breakdown.mergedPrsScore },
    { axis: "Depth", value: breakdown.meaningfulPrsScore },
    { axis: "Reviews", value: breakdown.reviewsGivenScore },
  ]

  return (
    <div className="profile-chart">
      <ResponsiveContainer width="100%" height={110}>
        <RadarChart data={data} outerRadius="62%">
          <PolarGrid stroke="#302d2a" />
          <PolarAngleAxis
            dataKey="axis"
            tick={{ fontSize: 9, fill: "#958f88" }}
          />
          <Radar
            dataKey="value"
            fill="rgba(224, 122, 58, 0.18)"
            stroke="#e07a3a"
            strokeWidth={1.5}
            dot={{ r: 2.5, fill: "#e07a3a", strokeWidth: 0 }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}
