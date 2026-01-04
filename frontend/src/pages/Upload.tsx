import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'

import Button from '../components/Button'
import Input from '../components/Input'
import { Card, CardHint, CardTitle } from '../components/Card'
import { api } from '../lib/api'
import type { TransactionUploadResponse } from '../types'

export default function Upload() {
  const [file, setFile] = useState<File | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const queryClient = useQueryClient()

  const onUpload = async () => {
    if (!file || loading) return

    setLoading(true)
    setMessage(null)
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await api.post<TransactionUploadResponse>('/transactions/upload', formData)
      setMessage(`Inserted ${response.data.inserted} transactions`)

      if (response.data.latest_month) {
        localStorage.setItem('selected_month', response.data.latest_month)
      }

      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['trend'] })
      queryClient.invalidateQueries({ queryKey: ['recent'] })
      queryClient.invalidateQueries({ queryKey: ['insights'] })
    } catch (e: any) {
      const msg = e?.response?.data?.detail || e?.message || 'Upload failed'
      setError(String(msg))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <div className="rounded-3xl border border-white/60 bg-white/60 p-6 shadow-sm backdrop-blur">
        <div className="text-2xl font-semibold text-slate-900">Upload transactions</div>
        <div className="mt-1 text-sm text-slate-500">
          Upload a CSV with <span className="font-medium text-slate-700">date</span>,{' '}
          <span className="font-medium text-slate-700">amount</span>,{' '}
          <span className="font-medium text-slate-700">description</span>.
        </div>
      </div>

      <div className="mt-6">
        <Card>
          <CardTitle>Upload</CardTitle>
          <CardHint>Example row: 2026-01-01,120.5,Walmart groceries</CardHint>

          <div className="mt-4 space-y-3">
            <div className="rounded-2xl border border-dashed border-slate-300 bg-white/60 p-4">
              <div className="text-sm font-medium text-slate-800">Choose CSV file</div>
              <div className="mt-1 text-xs text-slate-500">Max size depends on your browser. Large files may take longer.</div>
              <div className="mt-3">
                <Input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0] || null)} />
              </div>
              {file ? <div className="mt-2 text-xs text-slate-600">Selected: {file.name}</div> : null}
            </div>

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
