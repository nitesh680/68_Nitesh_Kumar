import { useMemo, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'

import { Card, CardHint, CardTitle } from '../components/Card'
import Button from '../components/Button'
import Input from '../components/Input'
import { api } from '../lib/api'
import { ymNow } from '../lib/format'
import type { DashboardSummary, TrendPoint, TransactionOut } from '../types'

export default function Dashboard() {
  const [month, setMonth] = useState(() => localStorage.getItem('selected_month') || ymNow())
  const queryClient = useQueryClient()

  const formatINR = (value: number) =>
    new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(value)

  const dashQ = useQuery({
    queryKey: ['dashboard', month],
    queryFn: async () => {
      try {
        const response = await api.get<DashboardSummary>(`/analytics/dashboard?month=${month}`)
        return response.data
      } catch (error) {
        console.error('Dashboard query error:', error)
        // Return safe default data on error
        return {
          month: month,
          total_spend: 0,
          top_category: null,
          top_category_spend: 0,
          avg_confidence: null
        }
      }
    },
    staleTime: 30000, // Cache for 30 seconds
    retry: 1, // Reduce retries to avoid endless loops
    enabled: !!month, // Only run when month is set
  })

  const trendQ = useQuery({
    queryKey: ['trend'],
    queryFn: async () => (await api.get<TrendPoint[]>('/analytics/trend')).data,
    staleTime: 60000, // Cache for 1 minute
    retry: 1,
  })

  const recentQ = useQuery({
    queryKey: ['recent'],
    queryFn: async () => (await api.get<TransactionOut[]>('/transactions/recent?limit=8')).data,
    staleTime: 15000, // Cache for 15 seconds
    retry: 1,
  })

  const handleMonthChange = (newMonth: string) => {
    setMonth(newMonth)
    localStorage.setItem('selected_month', newMonth)
    // Query key changes will refetch; invalidate to refresh cached data
    queryClient.invalidateQueries({ queryKey: ['dashboard'] })
  }

  const trendMax = useMemo(() => {
    const vals = trendQ.data?.map((t) => t.total_spend) || []
    return Math.max(1, ...vals)
  }, [trendQ.data])

  // Simple loading state
  if (dashQ.isLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="text-slate-600">Loading dashboard...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="py-2 sm:py-4">
      <div className="mx-auto max-w-7xl">
        <div className="rounded-3xl border border-white/60 bg-white/60 p-6 shadow-sm backdrop-blur">
          <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <div className="text-2xl font-semibold text-slate-900">Your Dashboard</div>
              <div className="mt-1 text-sm text-slate-500">Track spending, trends, and recent activity</div>
            </div>

            <div className="flex items-center gap-2">
              <div className="w-40">
                <div className="mb-1 text-xs font-medium text-slate-700">Month (YYYY-MM)</div>
                <Input 
                  value={month} 
                  onChange={(e) => handleMonthChange(e.target.value)} 
                  placeholder="2026-01" 
                />
              </div>
              <Button onClick={() => dashQ.refetch()} disabled={dashQ.isFetching}>
                Refresh
              </Button>
            </div>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
          <Card>
            <CardTitle>Total spend</CardTitle>
            <div className="mt-2 text-3xl font-semibold text-slate-900">
              {dashQ.data ? formatINR(dashQ.data.total_spend) : '--'}
            </div>
            <CardHint>
              {dashQ.data?.total_spend && dashQ.data.total_spend > 0 ? `For ${month}` : 'No transactions this month'}
            </CardHint>
          </Card>
          <Card>
            <CardTitle>Top category</CardTitle>
            <div className="mt-2 text-xl font-semibold text-slate-900">
              {dashQ.data?.top_category || 'No data'}
            </div>
            <CardHint>
              {dashQ.data?.top_category ? `${formatINR(dashQ.data.top_category_spend)} spent` : 'Upload transactions to see categories'}
            </CardHint>
          </Card>
          <Card>
            <CardTitle>Avg confidence</CardTitle>
            <div className="mt-2 text-3xl font-semibold text-slate-900">
              {dashQ.data?.avg_confidence != null ? `${(dashQ.data.avg_confidence * 100).toFixed(0)}%` : 'N/A'}
            </div>
            <CardHint>
              {dashQ.data?.avg_confidence != null ? 'Higher means more reliable categories' : 'No confidence data available'}
            </CardHint>
          </Card>
        </div>

        <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Card>
            <CardTitle>Monthly trend</CardTitle>
            <CardHint>Last months available in your data</CardHint>
            <div className="mt-4 flex h-40 items-end gap-2 overflow-x-auto">
              {(trendQ.data || []).slice(-10).map((p) => {
                const h = Math.max(6, Math.round((p.total_spend / trendMax) * 160))
                return (
                  <div key={p.month} className="flex w-8 flex-col items-center gap-2 flex-shrink-0">
                    <div className="w-full rounded-md bg-slate-900" style={{ height: h }} />
                    <div className="text-[10px] text-slate-500 whitespace-nowrap">{p.month.slice(5)}</div>
                  </div>
                )
              })}
            </div>
          </Card>

          <Card>
            <CardTitle>Recent transactions</CardTitle>
            <CardHint>Last 8 transactions</CardHint>
            <div className="mt-4 space-y-2 max-h-40 overflow-y-auto">
              {(recentQ.data || []).map((t) => (
                <div key={t.id} className="flex items-center justify-between rounded-lg border border-slate-100 px-3 py-2">
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-sm font-medium text-slate-900">{t.description}</div>
                    <div className="text-xs text-slate-500">
                      {new Date(t.date).toLocaleDateString()} · {t.category || '—'}
                      {t.confidence != null ? ` · ${(t.confidence * 100).toFixed(0)}%` : ''}
                    </div>
                  </div>
                  <div className="ml-2 text-sm font-semibold text-slate-900 flex-shrink-0">{formatINR(t.amount)}</div>
                </div>
              ))}
              {recentQ.data?.length === 0 ? <div className="text-sm text-slate-500">No data yet.</div> : null}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
