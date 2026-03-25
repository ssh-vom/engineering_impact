import { useEffect, useState, useCallback } from "react"
import type { DashboardData, EngineerDetail } from "./types"
import { fetchDashboardData } from "./lib/dashboard"
import { SummaryHeader } from "./components/SummaryHeader"
import { EngineerCard } from "./components/EngineerCard"
import { FocusPanel } from "./components/FocusPanel"
import { MethodologyFooter } from "./components/MethodologyFooter"

export default function App() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [focusLogin, setFocusLogin] = useState<string | null>(null)
  const [lastDetail, setLastDetail] = useState<EngineerDetail | null>(null)

  useEffect(() => {
    fetchDashboardData()
      .then(setData)
      .catch((e: Error) => setError(e.message))
  }, [])

  const closeFocus = useCallback(() => setFocusLogin(null), [])

  useEffect(() => {
    if (!focusLogin) return
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeFocus()
    }
    window.addEventListener("keydown", handler)
    return () => window.removeEventListener("keydown", handler)
  }, [focusLogin, closeFocus])

  const focusedDetail =
    focusLogin && data ? data.engineerDetails[focusLogin] : null

  if (focusedDetail && focusedDetail !== lastDetail) {
    setLastDetail(focusedDetail)
  }

  const panelOpen = !!focusedDetail
  const panelDetail = focusedDetail ?? lastDetail

  if (error) {
    return <div className="state-screen error">{error}</div>
  }
  if (!data) {
    return <div className="state-screen">Loading dashboard…</div>
  }

  return (
    <div className={`dashboard${panelOpen ? " dashboard--focus" : ""}`}>
      <SummaryHeader summary={data.summary} />

      <div className="dashboard-body">
        <main className="engineer-grid">
          {data.topEngineers.map((eng) => {
            const detail = data.engineerDetails[eng.login]
            if (!detail) return null
            return (
              <EngineerCard
                key={eng.login}
                detail={detail}
                selected={eng.login === focusLogin}
                onClick={() =>
                  setFocusLogin(eng.login === focusLogin ? null : eng.login)
                }
              />
            )
          })}
        </main>

        {panelDetail && (
          <FocusPanel
            detail={panelDetail}
            open={panelOpen}
            onClose={closeFocus}
          />
        )}
      </div>

      <MethodologyFooter methodology={data.methodology} />
    </div>
  )
}
