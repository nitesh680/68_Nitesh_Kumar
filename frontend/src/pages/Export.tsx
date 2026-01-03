import { useState } from 'react'

import Button from '../components/Button'
import Input from '../components/Input'
import { Card, CardHint, CardTitle } from '../components/Card'
import { api } from '../lib/api'

export default function Export() {
  const [month, setMonth] = useState('')
  const [loading, setLoading] = useState<null | 'csv' | 'pdf'>(null)
  const [error, setError] = useState<string | null>(null)

  function qp() {
    return month.trim() ? `?month=${encodeURIComponent(month.trim())}` : ''
  }

  function downloadBlob(blob: Blob, filename: string) {
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  }

  async function download(kind: 'csv' | 'pdf') {
    setError(null)
    setLoading(kind)
    try {
      const path = kind === 'csv' ? `/export/transactions.csv${qp()}` : `/export/transactions.pdf${qp()}`
      const res = await api.get(path, { responseType: 'blob' })
      const filename = kind === 'csv'
        ? `transactions${month.trim() ? '-' + month.trim() : ''}.csv`
        : `transactions${month.trim() ? '-' + month.trim() : ''}.pdf`
      downloadBlob(res.data, filename)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Export failed')
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <div className="text-2xl font-semibold text-slate-900">Export</div>
      <div className="mt-1 text-sm text-slate-500">Download your categorized transactions</div>

      <div className="mt-6">
        <Card>
          <CardTitle>Filters</CardTitle>
          <CardHint>Optional month filter: YYYY-MM</CardHint>
          <div className="mt-3 max-w-xs">
            <Input value={month} onChange={(e) => setMonth(e.target.value)} placeholder="2026-01" />
          </div>
        </Card>
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card>
          <CardTitle>CSV</CardTitle>
          <CardHint>Best for Excel / Sheets</CardHint>
          <div className="mt-4">
            <Button onClick={() => download('csv')} disabled={loading !== null}>
              {loading === 'csv' ? 'Downloading…' : 'Download CSV'}
            </Button>
          </div>
        </Card>

        <Card>
          <CardTitle>PDF</CardTitle>
          <CardHint>Quick printable summary (first 200 rows)</CardHint>
          <div className="mt-4">
            <Button onClick={() => download('pdf')} disabled={loading !== null}>
              {loading === 'pdf' ? 'Downloading…' : 'Download PDF'}
            </Button>
          </div>
        </Card>
      </div>

      {error ? <div className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div> : null}

      <div className="mt-4 text-xs text-slate-500">Exports require you to be logged in (Bearer token).</div>
    </div>
  )
}
