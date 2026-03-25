import { useEffect, useState } from "react"
import type { DashboardData } from "./types"
import { fetchDashboardData } from "./lib/dashboard"
import { SummaryHeader } from "./components/SummaryHeader"
import { EngineerCard } from "./components/EngineerCard"
import { MethodologyFooter } from "./components/MethodologyFooter"

export default function App() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDashboardData()
      .then(setData)
      .catch((e: Error) => setError(e.message))
  }, [])

  if (error) {
    return <div className="state-screen error">{error}</div>
  }
  if (!data) {
    return <div className="state-screen">Loading dashboard…</div>
  }

  return (
    <div className="dashboard">
      <SummaryHeader summary={data.summary} />

      <main className="engineer-grid">
        {data.topEngineers.map((eng) => {
          const detail = data.engineerDetails[eng.login]
          if (!detail) return null
          return <EngineerCard key={eng.login} detail={detail} />
        })}
      </main>

      <MethodologyFooter methodology={data.methodology} />
    </div>
  )
}
