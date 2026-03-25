import type { EngineerDetail } from "../types"
import { ScoreBreakdown } from "./ScoreBreakdown"

function formatScore(n: number): string {
  return n % 1 === 0 ? n.toFixed(0) : n.toFixed(1)
}

function formatHours(h: number | null): string {
  if (h === null) return "—"
  if (h < 1) return `${(h * 60).toFixed(0)}m`
  return `${h.toFixed(1)}h`
}

export function EngineerCard({ detail }: { detail: EngineerDetail }) {
  return (
    <article className="engineer-card" data-rank={detail.rank}>
      <div className="card-identity">
        <div className="rank-badge" data-rank={detail.rank}>
          {detail.rank}
        </div>
        <img
          className="avatar"
          src={detail.avatarUrl}
          alt={detail.displayName}
          loading="lazy"
        />
        <div className="card-name-score">
          <span className="engineer-name">{detail.displayName}</span>
          <span className="impact-score">{formatScore(detail.impactScore)}</span>
        </div>
      </div>

      <p className="headline">{detail.headline}</p>

      <div className="stats-grid">
        <div className="stat-item">
          <span className="stat-value">{detail.stats.mergedPrs}</span>
          <span className="stat-label">Merged</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">{detail.stats.meaningfulPrs}</span>
          <span className="stat-label">Meaningful</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">{detail.stats.reviewsGiven}</span>
          <span className="stat-label">Reviews</span>
        </div>
      </div>

      <p className="stats-supporting">
        {detail.stats.uniqueAreasTouched} area
        {detail.stats.uniqueAreasTouched !== 1 && "s"} ·{" "}
        {detail.stats.uniqueAuthorsReviewed} author
        {detail.stats.uniqueAuthorsReviewed !== 1 && "s"} reviewed ·{" "}
        {formatHours(detail.stats.medianTimeToMergeHours)} TTM
      </p>

      <ScoreBreakdown breakdown={detail.scoreBreakdown} />

      <div className="representative-prs">
        <span className="section-label">Key PRs</span>
        {detail.representativePrs.map((pr) => (
          <div className="pr-item" key={pr.number}>
            <div className="pr-title-row">
              <a
                className="pr-link"
                href={pr.url}
                target="_blank"
                rel="noopener noreferrer"
              >
                #{pr.number} {pr.title}
              </a>
              {pr.isMeaningful && (
                <span className="meaningful-badge">meaningful</span>
              )}
            </div>
            <span className="pr-meta">
              {pr.changedFiles} files · {pr.reviewCount} reviews ·{" "}
              {pr.areas.join(", ")}
            </span>
          </div>
        ))}
      </div>
    </article>
  )
}
