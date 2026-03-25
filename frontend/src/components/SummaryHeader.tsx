import type { DashboardSummary } from "../types"

function fmtHours(h: number | null): string {
  if (h === null) return "—"
  if (h < 1) return `${(h * 60).toFixed(0)}m`
  return `${h.toFixed(1)}h`
}

export function SummaryHeader({ summary }: { summary: DashboardSummary }) {
  const date = new Date(summary.generatedAt).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  })

  return (
    <header className="summary-header">
      <div className="summary-left">
        <h1 className="repo-name">{summary.repo}</h1>
        <span className="header-meta">
          {summary.windowDays} days · {date}
        </span>
      </div>

      <div className="summary-kpis">
        <div className="kpi">
          <span className="kpi-value">{summary.prsAnalyzed}</span>
          <span className="kpi-label">PRs analyzed</span>
        </div>
        <div className="kpi">
          <span className="kpi-value">
            {(summary.mergedPrRate * 100).toFixed(0)}%
          </span>
          <span className="kpi-label">Merge rate</span>
        </div>
        <div className="kpi">
          <span className="kpi-value">
            {fmtHours(summary.medianTimeToMergeHours)}
          </span>
          <span className="kpi-label">Median TTM</span>
        </div>
        <div className="kpi">
          <span className="kpi-value">{summary.engineersAnalyzed}</span>
          <span className="kpi-label">Engineers</span>
        </div>
      </div>
    </header>
  )
}
