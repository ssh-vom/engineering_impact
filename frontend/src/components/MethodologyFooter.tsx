import type { Methodology } from "../types"

export function MethodologyFooter({
  methodology,
}: {
  methodology: Methodology
}) {
  const w = methodology.weights
  const pct = (v: number) => (v * 100).toFixed(0)

  return (
    <footer className="methodology-footer">
      <p className="methodology-def">{methodology.definition}</p>

      <div className="impact-formula-panel">
        <div className="impact-formula-title">Impact score</div>
        <p className="impact-formula-line">
          Each metric is min–max normalized across engineers, then combined:
        </p>
        <code className="impact-formula-code">
          {pct(w.mergedPrs)}% × shipped + {pct(w.meaningfulPrs)}% × depth +{" "}
          {pct(w.reviewsGiven)}% × reviews
        </code>
        <p className="impact-formula-note">
          Raw counts (merged PRs, meaningful PRs, reviews given) appear on
          cards; the score uses normalized values so the field is comparable.
        </p>
      </div>
    </footer>
  )
}
