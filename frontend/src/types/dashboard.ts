export type DashboardSummary = {
  repo: string
  windowDays: number
  generatedAt: string
  prsAnalyzed: number
  engineersAnalyzed: number
  mergedPrRate: number
  medianTimeToMergeHours: number | null
  impactDefinition: string
}

export type EngineerStats = {
  mergedPrs: number
  meaningfulPrs: number
  reviewsGiven: number
  uniqueAreasTouched: number
  uniqueAuthorsReviewed: number
  medianTimeToMergeHours: number | null
}

export type TopEngineer = {
  login: string
  displayName: string
  avatarUrl: string
  rank: number
  impactScore: number
  headline: string
  stats: EngineerStats
}

export type ScoreBreakdown = {
  mergedPrsScore: number
  meaningfulPrsScore: number
  reviewsGivenScore: number
}

export type RepresentativePr = {
  number: number
  title: string
  url: string
  mergedAt: string | null
  changedFiles: number
  areas: string[]
  reviewCount: number
  isMeaningful: boolean
  whyItMatters: string
}

export type EngineerDetail = {
  login: string
  displayName: string
  avatarUrl: string
  rank: number
  impactScore: number
  headline: string
  whyThisPersonRanksHighly: string[]
  scoreBreakdown: ScoreBreakdown
  stats: EngineerStats
  representativePrs: RepresentativePr[]
}

export type Methodology = {
  definition: string
  weights: {
    mergedPrs: number
    meaningfulPrs: number
    reviewsGiven: number
  }
  meaningfulPrDefinition: string
  notes: string[]
}

export type DashboardData = {
  summary: DashboardSummary
  topEngineers: TopEngineer[]
  engineerDetails: Record<string, EngineerDetail>
  methodology: Methodology
}
