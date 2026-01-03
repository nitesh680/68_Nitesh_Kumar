import type { PropsWithChildren } from 'react'

export function Card({ children }: PropsWithChildren) {
  return <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">{children}</div>
}

export function CardTitle({ children }: PropsWithChildren) {
  return <div className="text-sm font-semibold text-slate-900">{children}</div>
}

export function CardHint({ children }: PropsWithChildren) {
  return <div className="mt-1 text-xs text-slate-500">{children}</div>
}
