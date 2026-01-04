import { Navigate } from 'react-router-dom'
import { type ReactNode } from 'react'

import { getToken } from '../lib/storage'

export default function ProtectedRoute({ children }: { children: ReactNode }) {
  const token = getToken()
  if (!token) return <Navigate to="/login" replace />
  return <>{children}</>
}
