import type { Methodology } from "../types"

export function MethodologyFooter({
  methodology,
}: {
  methodology: Methodology
}) {
  return (
    <footer className="methodology-footer">
      <span className="methodology-text">{methodology.definition}</span>
      <div className="methodology-weights">
        <span className="weight-pill">
          <span className="weight-value">
            {(methodology.weights.mergedPrs * 100).toFixed(0)}%
          </span>{" "}
          Merged
        </span>
        <span className="weight-pill">
          <span className="weight-value">
            {(methodology.weights.meaningfulPrs * 100).toFixed(0)}%
          </span>{" "}
          Meaningful
        </span>
        <span className="weight-pill">
          <span className="weight-value">
            {(methodology.weights.reviewsGiven * 100).toFixed(0)}%
          </span>{" "}
          Reviews
        </span>
      </div>
    </footer>
  )
}
