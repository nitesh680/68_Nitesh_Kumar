import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'

import Button from '../components/Button'
import Input from '../components/Input'
import { Card, CardHint, CardTitle } from '../components/Card'
import { api } from '../lib/api'
import { ymNow } from '../lib/format'

export default function Insights() {
  const [month, setMonth] = useState(ymNow())

  const q = useQuery({
    queryKey: ['insights', month],
    queryFn: async () => (await api.get(`/insights/summary?month=${month}`)).data as any,
    enabled: false,
  })

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="text-2xl font-semibold text-slate-900">AI Insights</div>
      <div className="mt-1 text-sm text-slate-500">Gemini-powered monthly summary</div>

      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card>
          <CardTitle>Month</CardTitle>
          <CardHint>Format YYYY-MM</CardHint>
          <div className="mt-3 flex items-center gap-2">
            <Input value={month} onChange={(e) => setMonth(e.target.value)} />
            <Button onClick={() => q.refetch()} disabled={q.isFetching}>
              Generate
            </Button>
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
          </Card>
        </div>
      </div>

      {q.data?.breakdown ? (
        <div className="mt-6">
          <Card>
            <CardTitle>Breakdown</CardTitle>
            <CardHint>Category totals</CardHint>
            <div className="mt-4 grid grid-cols-1 gap-2 md:grid-cols-2">
              {q.data.breakdown.map((r: any, idx: number) => (
                <div key={idx} className="flex items-center justify-between rounded-lg border border-slate-100 px-3 py-2">
                  <div className="text-sm font-medium text-slate-900">{r.category}</div>
                  <div className="text-sm text-slate-700">{r.total}</div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      ) : null}

      <div className="mt-4 text-xs text-slate-500">Requires backend GEMINI_API_KEY.</div>
    </div>
  )
}
