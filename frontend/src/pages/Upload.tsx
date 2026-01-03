import { useState } from 'react'

import Button from '../components/Button'
import Input from '../components/Input'
import { Card, CardHint, CardTitle } from '../components/Card'
import { api } from '../lib/api'

export default function Upload() {
  const [file, setFile] = useState<File | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function onUpload() {
    if (!file) return
    setMessage(null)
    setError(null)
    setLoading(true)
    console.log('Auth token before upload:', api.defaults.headers.common.Authorization)
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await api.post<{ inserted: number }>('/transactions/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setMessage(`Uploaded. Inserted: ${res.data.inserted}`)
    } catch (err: any) {
      const detail = err?.response?.data?.detail
      const status = err?.response?.status
      const msg = detail ? `[${status}] ${detail}` : `${status || 'Network'} Upload failed`
      setError(msg)
      console.error('Upload error', { status, detail, err })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <div className="text-2xl font-semibold text-slate-900">Upload CSV</div>
      <div className="mt-1 text-sm text-slate-500">CSV must include: date, amount, description</div>

      <div className="mt-6">
        <Card>
          <CardTitle>Upload</CardTitle>
          <CardHint>Example row: 2026-01-01,120.5,Walmart groceries</CardHint>

          <div className="mt-4 space-y-3">
            <Input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0] || null)} />

            {message ? <div className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-700">{message}</div> : null}
            {error ? <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div> : null}

            <Button onClick={onUpload} disabled={!file || loading}>
              {loading ? 'Uploading…' : 'Upload'}
            </Button>
          </div>
        </Card>
      </div>
    </div>
  )
}
