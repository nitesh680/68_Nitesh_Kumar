import type { PropsWithChildren } from 'react'

export function Card({ children }: PropsWithChildren) {
  return (
    <div className="rounded-2xl border border-white/50 bg-white/70 p-5 shadow-sm backdrop-blur transition hover:shadow-md">
      {children}
    </div>
  )
}

export default Card

export function CardTitle({ children }: PropsWithChildren) {
  return <div className="text-sm font-semibold text-slate-900">{children}</div>
}

export function CardHint({ children }: PropsWithChildren) {
  return <div className="mt-1 text-xs text-slate-500">{children}</div>
}
