import type { DashboardSummary } from "../types"

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
        <span className="header-badge">Last {summary.windowDays} days</span>
        <span className="header-badge">{date}</span>
      </div>

      <div className="summary-kpis">
        <div className="kpi">
          <span className="kpi-value">{summary.prsAnalyzed}</span>
          <span className="kpi-label">PRs Analyzed</span>
        </div>
        <div className="kpi">
          <span className="kpi-value">
            {(summary.mergedPrRate * 100).toFixed(0)}%
          </span>
          <span className="kpi-label">Merge Rate</span>
        </div>
        <div className="kpi">
          <span className="kpi-value">
            {summary.medianTimeToMergeHours?.toFixed(1) ?? "—"}h
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
