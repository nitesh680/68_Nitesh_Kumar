export type TokenResponse = { access_token: string; token_type: string }

export type UserPublic = { id: string; email: string; name: string; avatar_url?: string | null }

export type TransactionOut = {
  id: string
  date: string
  description: string
  amount: number
  category?: string | null
  confidence?: number | null
  source?: string | null
  explanation?: string | null
}

export type DashboardSummary = {
  month: string
  total_spend: number
  top_category?: string | null
  top_category_spend: number
  avg_confidence?: number | null
}

export type TrendPoint = { month: string; total_spend: number }

export type AnomalyPoint = { date: string; amount: number; description: string; zscore: number }
