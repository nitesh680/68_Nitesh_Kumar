import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'

import Button from '../components/Button'
import Input from '../components/Input'
import { Card, CardHint, CardTitle } from '../components/Card'
import { api } from '../lib/api'
import { ymNow } from '../lib/format'

export default function Insights() {
  const [month, setMonth] = useState(() => localStorage.getItem('selected_month') || ymNow())
  const [year, setYear] = useState(() => String(new Date().getFullYear()))
  const queryClient = useQueryClient()
  const budget = localStorage.getItem('monthly_budget_inr') || ''

  const formatINR = (value: number) =>
    new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(value)

  const q = useQuery({
    queryKey: ['insights', month],
    queryFn: async () => {
      const b = budget.trim() ? `&budget_inr=${encodeURIComponent(budget.trim())}` : ''
      return (await api.get(`/insights/advanced?month=${encodeURIComponent(month)}&year=${encodeURIComponent(year)}${b}`))
        .data as any
    },
    enabled: !!month,
    staleTime: 30000, // Cache for 30 seconds
    retry: 1,
  })

  const handleMonthChange = (newMonth: string) => {
    setMonth(newMonth)
    localStorage.setItem('selected_month', newMonth)
    queryClient.invalidateQueries({ queryKey: ['insights'] })
  }

  const bar = (q.data?.charts?.bar_by_category || []) as Array<{ category: string; total: number }>
  const pie = (q.data?.charts?.pie_distribution || []) as Array<{ category: string; value: number; pct: number }>
  const maxBar = Math.max(1, ...bar.map((b) => Number(b.total || 0)))

  const pieColors = [
    '#4f46e5',
    '#06b6d4',
    '#22c55e',
    '#f97316',
    '#ef4444',
    '#a855f7',
    '#0ea5e9',
    '#f59e0b',
    '#10b981',
    '#e11d48',
  ]

  const pieBg = pie.length
    ? `conic-gradient(${pie
        .map((p, idx) => {
          const start = pie.slice(0, idx).reduce((s, x) => s + Number(x.pct || 0), 0)
          const end = start + Number(p.pct || 0)
          const c = pieColors[idx % pieColors.length]
          return `${c} ${start * 100}% ${end * 100}%`
        })
        .join(', ')})`
    : 'conic-gradient(#e2e8f0 0% 100%)'

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="rounded-3xl border border-white/60 bg-white/60 p-6 shadow-sm backdrop-blur">
        <div className="text-2xl font-semibold text-slate-900">AI Insights</div>
        <div className="mt-1 text-sm text-slate-500">Actionable monthly insights generated from your uploaded transactions</div>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card>
          <CardTitle>Month</CardTitle>
          <CardHint>Format YYYY-MM</CardHint>
          <div className="mt-3 flex items-center gap-2">
            <Input value={month} onChange={(e) => handleMonthChange(e.target.value)} />
            <Button onClick={() => q.refetch()} disabled={q.isFetching}>
              Generate
            </Button>
          </div>
          <div className="mt-3">
            <CardHint>Year (for yearly summary)</CardHint>
            <div className="mt-2">
              <Input value={year} onChange={(e) => setYear(e.target.value)} />
            </div>
          </div>
        </Card>

        <div className="md:col-span-2">
          <Card>
            <CardTitle>Summary</CardTitle>
            <CardHint>{q.isFetching ? 'Generating…' : 'Click Generate'}</CardHint>
            {q.isError ? (
              <div className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
                {(q.error as any)?.response?.data?.detail || 'Failed to generate'}
              </div>
            ) : null}
            {q.data?.summary ? <div className="mt-4 whitespace-pre-wrap text-sm text-slate-800">{q.data.summary}</div> : null}
            {q.data?.ai_enabled ? (
              <div className="mt-2 text-xs text-green-600">✓ AI-generated summary</div>
            ) : q.data ? (
              <div className="mt-2 text-xs text-blue-600">ℹ️ Data-based summary</div>
            ) : null}
          </Card>
        </div>
      </div>

      {q.data?.kpis ? (
        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-4">
          <Card>
            <CardTitle>Income</CardTitle>
            <div className="mt-2 text-lg font-semibold text-slate-900">{formatINR(Number(q.data.kpis.income || 0))}</div>
          </Card>
          <Card>
            <CardTitle>Expenses</CardTitle>
            <div className="mt-2 text-lg font-semibold text-slate-900">{formatINR(Number(q.data.kpis.expenses || 0))}</div>
          </Card>
          <Card>
            <CardTitle>Savings</CardTitle>
            <div className="mt-2 text-lg font-semibold text-slate-900">{formatINR(Number(q.data.kpis.savings || 0))}</div>
            <CardHint>{Number(q.data.kpis.savings || 0) < 0 ? 'Spending exceeds income' : 'Positive cash flow'}</CardHint>
          </Card>
          <Card>
            <CardTitle>Health score</CardTitle>
            <div className="mt-2 text-lg font-semibold text-slate-900">{Number(q.data.kpis.health_score || 0)}/100</div>
            <CardHint>Based on savings rate, budget and patterns</CardHint>
          </Card>
        </div>
      ) : null}

      {q.data?.alerts?.length ? (
        <div className="mt-6">
          <Card>
            <CardTitle>Alerts</CardTitle>
            <CardHint>Budget and overspending warnings</CardHint>
            <div className="mt-4 grid gap-2">
              {q.data.alerts.map((a: any, idx: number) => (
                <div
                  key={idx}
                  className={`rounded-lg px-3 py-2 text-sm ${
                    a.level === 'danger'
                      ? 'bg-rose-50 text-rose-800'
                      : a.level === 'warning'
                        ? 'bg-amber-50 text-amber-800'
                        : 'bg-blue-50 text-blue-800'
                  }`}
                >
                  {a.message}
                </div>
              ))}
            </div>
          </Card>
        </div>
      ) : null}

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardTitle>Monthly expenses by category</CardTitle>
          <CardHint>Bar chart</CardHint>
          <div className="mt-4 space-y-2">
            {bar.length ? (
              bar.map((b, idx) => (
                <div key={idx} className="grid grid-cols-12 gap-2 items-center">
                  <div className="col-span-5 text-xs font-medium text-slate-800 truncate">{b.category}</div>
                  <div className="col-span-5">
                    <div className="h-2 w-full rounded-full bg-slate-200 overflow-hidden">
                      <div
                        className="h-2 rounded-full bg-indigo-600"
                        style={{ width: `${(Number(b.total || 0) / maxBar) * 100}%` }}
                      />
                    </div>
                  </div>
                  <div className="col-span-2 text-right text-xs text-slate-700">{formatINR(Number(b.total || 0))}</div>
                </div>
              ))
            ) : (
              <div className="text-sm text-slate-600">No category data yet.</div>
            )}
          </div>
        </Card>

        <Card>
          <CardTitle>Expense distribution</CardTitle>
          <CardHint>Pie chart</CardHint>
          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 items-center">
            <div className="flex items-center justify-center">
              <div
                className="h-40 w-40 rounded-full border border-white/60"
                style={{ background: pieBg }}
              />
            </div>
            <div className="space-y-2">
              {pie.length ? (
                pie.slice(0, 8).map((p, idx) => (
                  <div key={idx} className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2 min-w-0">
                      <span
                        className="h-3 w-3 rounded-sm flex-shrink-0"
                        style={{ backgroundColor: pieColors[idx % pieColors.length] }}
                      />
                      <span className="text-xs font-medium text-slate-800 truncate">{p.category}</span>
                    </div>
                    <span className="text-xs text-slate-700">{Math.round(Number(p.pct || 0) * 100)}%</span>
                  </div>
                ))
              ) : (
                <div className="text-sm text-slate-600">No data yet.</div>
              )}
            </div>
          </div>
        </Card>
      </div>

      {q.data?.wasteful?.length ? (
        <div className="mt-6">
          <Card>
            <CardTitle>Wasteful spending signals</CardTitle>
            <CardHint>Repeated or spiking patterns</CardHint>
            <div className="mt-4 grid gap-2">
              {q.data.wasteful.slice(0, 8).map((w: any, idx: number) => (
                <div key={idx} className="rounded-lg border border-slate-100 bg-white/50 px-3 py-2 text-sm text-slate-800">
                  {w.message}
                </div>
              ))}
            </div>
          </Card>
        </div>
      ) : null}

      {q.data?.prediction ? (
        <div className="mt-6">
          <Card>
            <CardTitle>Next-month prediction</CardTitle>
            <CardHint>Based on your recent spending history</CardHint>
            <div className="mt-3 text-sm text-slate-800">
              Estimated expenses next month: <span className="font-semibold">{formatINR(Number(q.data.prediction.next_month_expense || 0))}</span>
            </div>
            <div className="mt-1 text-xs text-slate-500">Basis: {q.data.prediction.basis}</div>
          </Card>
        </div>
      ) : null}

      <div className="mt-4 text-xs text-slate-500">Set GEMINI_API_KEY on backend to enable richer AI explanations.</div>
    </div>
  )
}
