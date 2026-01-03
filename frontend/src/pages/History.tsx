import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'

import { Card, CardHint, CardTitle } from '../components/Card'
import Input from '../components/Input'
import { api } from '../lib/api'
import { formatCurrency } from '../lib/format'
import type { TransactionOut } from '../types'

export default function History() {
  const [limit, setLimit] = useState(50)

  const q = useQuery({
    queryKey: ['recent', limit],
    queryFn: async () => (await api.get<TransactionOut[]>(`/transactions/recent?limit=${limit}`)).data,
  })

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <div className="text-2xl font-semibold text-slate-900">History</div>
          <div className="mt-1 text-sm text-slate-500">Browse your recent transactions</div>
        </div>

        <div className="w-32">
          <div className="mb-1 text-xs font-medium text-slate-700">Limit</div>
          <Input value={String(limit)} onChange={(e) => setLimit(Number(e.target.value || '50'))} type="number" />
        </div>
      </div>

      <div className="mt-6">
        <Card>
          <CardTitle>Transactions</CardTitle>
          <CardHint>{q.isFetching ? 'Loading…' : `${q.data?.length || 0} items`}</CardHint>

          <div className="mt-4 divide-y divide-slate-100">
            {(q.data || []).map((t) => (
              <div key={t.id} className="flex items-start justify-between gap-4 py-3">
                <div className="min-w-0">
                  <div className="truncate text-sm font-medium text-slate-900">{t.description}</div>
                  <div className="mt-1 text-xs text-slate-500">
                    {new Date(t.date).toLocaleString()} · {t.category || '—'}
                    {t.source ? ` · ${t.source}` : ''}
                    {t.confidence != null ? ` · ${(t.confidence * 100).toFixed(0)}%` : ''}
                  </div>
                  {t.explanation ? <div className="mt-1 text-xs text-slate-400">{t.explanation}</div> : null}
                </div>

                <div className="shrink-0 text-sm font-semibold text-slate-900">{formatCurrency(t.amount)}</div>
              </div>
            ))}
            {q.data?.length === 0 ? <div className="py-6 text-sm text-slate-500">No data yet.</div> : null}
          </div>
        </Card>
      </div>
    </div>
  )
}
