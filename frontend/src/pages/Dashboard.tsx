import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'

import { Card, CardHint, CardTitle } from '../components/Card'
import Button from '../components/Button'
import Input from '../components/Input'
import { api } from '../lib/api'
import { formatCurrency, ymNow } from '../lib/format'
import type { DashboardSummary, TrendPoint, TransactionOut } from '../types'

export default function Dashboard() {
  const [month, setMonth] = useState(ymNow())

  const dashQ = useQuery({
    queryKey: ['dashboard', month],
    queryFn: async () => (await api.get<DashboardSummary>(`/analytics/dashboard?month=${month}`)).data,
  })

  const trendQ = useQuery({
    queryKey: ['trend'],
    queryFn: async () => (await api.get<TrendPoint[]>('/analytics/trend')).data,
  })

  const recentQ = useQuery({
    queryKey: ['recent'],
    queryFn: async () => (await api.get<TransactionOut[]>('/transactions/recent?limit=8')).data,
  })

  const trendMax = useMemo(() => {
    const vals = trendQ.data?.map((t) => t.total_spend) || []
    return Math.max(1, ...vals)
  }, [trendQ.data])

  return (
    <div>
      <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="text-2xl font-semibold text-slate-900">Your Dashboard</div>
            <div className="mt-1 text-sm text-slate-500">Track spending, trends, and recent activity</div>
          </div>

          <div className="flex items-center gap-2">
            <div className="w-40">
              <div className="mb-1 text-xs font-medium text-slate-700">Month (YYYY-MM)</div>
              <Input value={month} onChange={(e) => setMonth(e.target.value)} placeholder="2026-01" />
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
            {dashQ.data ? formatCurrency(dashQ.data.total_spend) : '--'}
          </div>
          <CardHint>For {month}</CardHint>
        </Card>
        <Card>
          <CardTitle>Top category</CardTitle>
          <div className="mt-2 text-xl font-semibold text-slate-900">
            {dashQ.data?.top_category || '--'}
          </div>
          <CardHint>
            {dashQ.data ? `${formatCurrency(dashQ.data.top_category_spend)} spent` : '—'}
          </CardHint>
        </Card>
        <Card>
          <CardTitle>Avg confidence</CardTitle>
          <div className="mt-2 text-3xl font-semibold text-slate-900">
            {dashQ.data?.avg_confidence != null ? `${(dashQ.data.avg_confidence * 100).toFixed(0)}%` : '--'}
          </div>
          <CardHint>Higher means more reliable categories</CardHint>
        </Card>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card>
          <CardTitle>Monthly trend</CardTitle>
          <CardHint>Last months available in your data</CardHint>
          <div className="mt-4 flex h-40 items-end gap-2">
            {(trendQ.data || []).slice(-10).map((p) => {
              const h = Math.max(6, Math.round((p.total_spend / trendMax) * 160))
              return (
                <div key={p.month} className="flex w-8 flex-col items-center gap-2">
                  <div className="w-full rounded-md bg-slate-900" style={{ height: h }} />
                  <div className="text-[10px] text-slate-500">{p.month.slice(5)}</div>
                </div>
              )
            })}
          </div>
        </Card>

        <Card>
          <CardTitle>Recent transactions</CardTitle>
          <CardHint>Last 8 transactions</CardHint>
          <div className="mt-4 space-y-2">
            {(recentQ.data || []).map((t) => (
              <div key={t.id} className="flex items-center justify-between rounded-lg border border-slate-100 px-3 py-2">
                <div className="min-w-0">
                  <div className="truncate text-sm font-medium text-slate-900">{t.description}</div>
                  <div className="text-xs text-slate-500">
                    {new Date(t.date).toLocaleDateString()} · {t.category || '—'}
                    {t.confidence != null ? ` · ${(t.confidence * 100).toFixed(0)}%` : ''}
                  </div>
                </div>
                <div className="text-sm font-semibold text-slate-900">{formatCurrency(t.amount)}</div>
              </div>
            ))}
            {recentQ.data?.length === 0 ? <div className="text-sm text-slate-500">No data yet.</div> : null}
          </div>
        </Card>
      </div>
    </div>
  )
}
