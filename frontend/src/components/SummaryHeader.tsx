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
        <span className="header-meta">
          {summary.windowDays} days · {date}
        </span>
      </div>

      <div className="summary-kpis">
        <div className="kpi">
          <span className="kpi-value">{summary.prsAnalyzed}</span>
          <span className="kpi-label">PRs</span>
        </div>
        <div className="kpi">
          <span className="kpi-value">
            {(summary.mergedPrRate * 100).toFixed(0)}%
          </span>
          <span className="kpi-label">merged</span>
        </div>
        <div className="kpi">
          <span className="kpi-value">
            {summary.medianTimeToMergeHours?.toFixed(1) ?? "—"}h
          </span>
          <span className="kpi-label">median TTM</span>
        </div>
        <div className="kpi">
          <span className="kpi-value">{summary.engineersAnalyzed}</span>
          <span className="kpi-label">engineers</span>
        </div>
      </div>
    </header>
  )
}
