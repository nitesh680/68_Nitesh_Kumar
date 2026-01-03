import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import Button from '../components/Button'
import Input from '../components/Input'
import { api, setAuthToken } from '../lib/api'
import { setToken } from '../lib/storage'
import type { TokenResponse } from '../types'

export default function Signup() {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const res = await api.post<TokenResponse>('/auth/signup', { name, email, password })
      setToken(res.data.access_token)
      setAuthToken(res.data.access_token)
      navigate('/dashboard')
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Signup failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-md px-4 py-10">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="text-lg font-semibold text-slate-900">Create your account</div>
        <div className="mt-1 text-sm text-slate-500">Start tracking and categorizing expenses</div>

        <form className="mt-6 space-y-3" onSubmit={onSubmit}>
          <div>
            <div className="mb-1 text-xs font-medium text-slate-700">Name</div>
            <Input value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
          <div>
            <div className="mb-1 text-xs font-medium text-slate-700">Email</div>
            <Input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required />
          </div>
          <div>
            <div className="mb-1 text-xs font-medium text-slate-700">Password</div>
            <Input value={password} onChange={(e) => setPassword(e.target.value)} type="password" required />
          </div>

          {error ? <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div> : null}

          <Button type="submit" disabled={loading} className="w-full">
            {loading ? 'Creating…' : 'Create account'}
          </Button>
        </form>

        <div className="mt-4 text-sm text-slate-600">
          Already have an account?{' '}
          <Link to="/login" className="font-medium text-slate-900 hover:underline">
            Sign in
          </Link>
        </div>
      </div>
    </div>
  )
}
