import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  ResponsiveContainer,
} from "recharts"
import type { EngineerDetail } from "../types"
import { AreaPills } from "./AreaPills"

function fmtScore(n: number): string {
  return n % 1 === 0 ? n.toFixed(0) : n.toFixed(1)
}

function fmtHours(h: number | null): string {
  if (h === null) return "—"
  if (h < 1) return `${(h * 60).toFixed(0)}m`
  return `${h.toFixed(1)}h`
}

export function FocusPanel({
  detail,
  onClose,
}: {
  detail: EngineerDetail
  onClose: () => void
}) {
  const breakdown = detail.scoreBreakdown
  const radarData = [
    { axis: "Shipped", value: breakdown.mergedPrsScore },
    { axis: "Depth", value: breakdown.meaningfulPrsScore },
    { axis: "Reviews", value: breakdown.reviewsGivenScore },
  ]

  return (
    <aside className="focus-panel">
      <button className="focus-close" onClick={onClose}>
        <span aria-hidden>&#x2715;</span>
      </button>

      <div className="focus-body">
        {/* ── left: identity + chart + stats ── */}
        <div className="focus-left">
          <div className="focus-identity">
            <span className="focus-rank">#{detail.rank}</span>
            <img className="focus-avatar" src={detail.avatarUrl} alt="" />
            <div>
              <div className="focus-name">{detail.displayName}</div>
              <div className="focus-score">{fmtScore(detail.impactScore)}</div>
            </div>
          </div>

          <div className="focus-radar">
            <ResponsiveContainer width="100%" height={180}>
              <RadarChart data={radarData} outerRadius="60%">
                <PolarGrid stroke="#2e2b28" />
                <PolarAngleAxis
                  dataKey="axis"
                  tick={{ fontSize: 11, fill: "#a09890" }}
                />
                <Radar
                  dataKey="value"
                  fill="rgba(224, 122, 58, 0.18)"
                  stroke="#e07a3a"
                  strokeWidth={1.5}
                  dot={{ r: 3.5, fill: "#e07a3a", strokeWidth: 0 }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          <div className="focus-stats">
            <div className="focus-stat">
              <span className="focus-stat-val">{detail.stats.mergedPrs}</span>
              <span className="focus-stat-lbl">merged PRs</span>
            </div>
            <div className="focus-stat">
              <span className="focus-stat-val">
                {detail.stats.meaningfulPrs}
              </span>
              <span className="focus-stat-lbl">meaningful</span>
            </div>
            <div className="focus-stat">
              <span className="focus-stat-val">
                {detail.stats.reviewsGiven}
              </span>
              <span className="focus-stat-lbl">reviews given</span>
            </div>
            <div className="focus-stat">
              <span className="focus-stat-val">
                {fmtHours(detail.stats.medianTimeToMergeHours)}
              </span>
              <span className="focus-stat-lbl">median TTM</span>
            </div>
            <div className="focus-stat">
              <span className="focus-stat-val">
                {detail.stats.uniqueAreasTouched}
              </span>
              <span className="focus-stat-lbl">areas touched</span>
            </div>
            <div className="focus-stat">
              <span className="focus-stat-val">
                {detail.stats.uniqueAuthorsReviewed}
              </span>
              <span className="focus-stat-lbl">authors reviewed</span>
            </div>
          </div>

          <div className="focus-breakdown">
            <span className="focus-section-title">Normalized scores</span>
            {[
              { label: "Shipped", val: breakdown.mergedPrsScore },
              { label: "Depth", val: breakdown.meaningfulPrsScore },
              { label: "Reviews", val: breakdown.reviewsGivenScore },
            ].map((d) => (
              <div className="focus-bar-row" key={d.label}>
                <span className="focus-bar-label">{d.label}</span>
                <div className="focus-bar-track">
                  <div
                    className="focus-bar-fill"
                    style={{ width: `${d.val}%` }}
                  />
                </div>
                <span className="focus-bar-value">{fmtScore(d.val)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* ── right: reasons + PRs ── */}
        <div className="focus-right">
          <div className="focus-reasons">
            <span className="focus-section-title">
              Why #{detail.rank}
            </span>
            <ul className="focus-reason-list">
              {detail.whyThisPersonRanksHighly.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>

          <div className="focus-prs">
            <span className="focus-section-title">Representative PRs</span>
            <div className="focus-pr-list">
              {detail.representativePrs.map((pr) => (
                <div className="focus-pr" key={pr.number}>
                  <div className="focus-pr-header">
                    {pr.isMeaningful && <span className="focus-pr-dot" />}
                    <a
                      className="focus-pr-link"
                      href={pr.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      #{pr.number} {pr.title}
                    </a>
                  </div>
                  <p className="focus-pr-why">{pr.whyItMatters}</p>
                  <span className="focus-pr-meta">
                    {pr.changedFiles} files · {pr.reviewCount} reviews
                  </span>
                  <AreaPills areas={pr.areas} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}
