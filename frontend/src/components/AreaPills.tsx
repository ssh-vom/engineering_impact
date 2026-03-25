const MAX_VISIBLE = 6

function shortLabel(name: string): string {
  if (name.length <= 16) return name
  return `${name.slice(0, 14)}…`
}

export function AreaPills({ areas }: { areas: string[] }) {
  if (!areas.length) {
    return (
      <div className="area-pills">
        <span className="area-pill area-pill-empty">—</span>
      </div>
    )
  }

  const visible = areas.slice(0, MAX_VISIBLE)
  const rest = areas.length - visible.length

  return (
    <div className="area-pills">
      {visible.map((a, i) => (
        <span className="area-pill" key={`${i}-${a}`} title={a}>
          {shortLabel(a)}
        </span>
      ))}
      {rest > 0 && (
        <span className="area-pill area-pill-more" title={areas.join(", ")}>
          +{rest}
        </span>
      )}
    </div>
  )
}
