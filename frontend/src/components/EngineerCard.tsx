import type { EngineerDetail } from "../types"
import { AreaPills } from "./AreaPills"
import { ScoreBreakdown } from "./ScoreBreakdown"

function formatScore(n: number): string {
  return n % 1 === 0 ? n.toFixed(0) : n.toFixed(1)
}

function fmtHours(h: number | null): string {
  if (h === null) return "—"
  if (h < 1) return `${(h * 60).toFixed(0)}m`
  return `${h.toFixed(1)}h`
}

export function EngineerCard({ detail }: { detail: EngineerDetail }) {
  return (
    <article className="engineer-card" data-rank={detail.rank}>
      <div className="card-identity">
        <span className="rank-num">{detail.rank}</span>
        <img
          className="avatar"
          src={detail.avatarUrl}
          alt=""
          loading="lazy"
        />
        <div className="card-name-score">
          <span className="engineer-name">{detail.displayName}</span>
          <span className="impact-score">
            {formatScore(detail.impactScore)}
          </span>
        </div>
      </div>

      <ScoreBreakdown breakdown={detail.scoreBreakdown} />

      <div className="stats-row">
        <div className="stat">
          <span className="stat-val">{detail.stats.mergedPrs}</span>
          <span className="stat-lbl">merged</span>
        </div>
        <div className="stat">
          <span className="stat-val">{detail.stats.meaningfulPrs}</span>
          <span className="stat-lbl">meaningful</span>
        </div>
        <div className="stat">
          <span className="stat-val">{detail.stats.reviewsGiven}</span>
          <span className="stat-lbl">reviews</span>
        </div>
        <div className="stat">
          <span className="stat-val">
            {fmtHours(detail.stats.medianTimeToMergeHours)}
          </span>
          <span className="stat-lbl">TTM</span>
        </div>
      </div>

      <span className="stats-line">
        {detail.stats.uniqueAreasTouched} areas ·{" "}
        {detail.stats.uniqueAuthorsReviewed} authors reviewed
      </span>

      <ul className="reasons">
        {detail.whyThisPersonRanksHighly.slice(0, 2).map((r, i) => (
          <li className="reason" key={i}>
            {r}
          </li>
        ))}
      </ul>

      <div className="prs">
        {detail.representativePrs.map((pr) => (
          <div className="pr-block" key={pr.number}>
            <div className="pr-title-row">
              {pr.isMeaningful && <span className="pr-dot" />}
              <a
                className="pr-link"
                href={pr.url}
                target="_blank"
                rel="noopener noreferrer"
              >
                #{pr.number} {pr.title}
              </a>
            </div>
            <span className="pr-meta-line">
              {pr.changedFiles} files · {pr.reviewCount} reviews
            </span>
            <AreaPills areas={pr.areas} />
          </div>
        ))}
      </div>
    </article>
  )
}
