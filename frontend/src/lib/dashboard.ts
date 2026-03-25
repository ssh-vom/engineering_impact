import type { DashboardData } from "../types"

export async function fetchDashboardData(): Promise<DashboardData> {
  const response = await fetch("/dashboard.json")
  if (!response.ok) {
    throw new Error(`Failed to load dashboard.json: ${response.status}`)
  }
  return (await response.json()) as DashboardData
}
