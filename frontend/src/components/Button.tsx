import type { ButtonHTMLAttributes } from 'react'

export default function Button({ className = '', ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={`inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium shadow-sm transition focus:outline-none focus:ring-2 focus:ring-slate-400 disabled:opacity-50 bg-slate-900 text-white hover:bg-slate-800 ${className}`}
      {...props}
    />
  )
}
