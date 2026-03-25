import type { Methodology } from "../types"

export function MethodologyFooter({
  methodology,
}: {
  methodology: Methodology
}) {
  const pct = (v: number) => (v * 100).toFixed(0)

  return (
    <footer className="methodology-footer">
      <span className="methodology-def">{methodology.definition}</span>
      <div className="methodology-weights">
        <span className="weight">
          <span className="weight-num">{pct(methodology.weights.mergedPrs)}%</span>{" "}
          shipped
        </span>
        <span className="weight">
          <span className="weight-num">
            {pct(methodology.weights.meaningfulPrs)}%
          </span>{" "}
          depth
        </span>
        <span className="weight">
          <span className="weight-num">
            {pct(methodology.weights.reviewsGiven)}%
          </span>{" "}
          reviews
        </span>
      </div>
    </footer>
  )
}
