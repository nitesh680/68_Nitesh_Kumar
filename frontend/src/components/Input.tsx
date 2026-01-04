import type { InputHTMLAttributes } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: string
}

export default function Input({ className = '', error, ...props }: InputProps) {
  return (
    <div className="w-full">
      <input
        className={`w-full rounded-lg border border-white/60 bg-white/70 px-3 py-2 text-sm text-slate-900 shadow-sm outline-none backdrop-blur transition placeholder:text-slate-400 focus:border-indigo-300 focus:ring-2 focus:ring-indigo-200 ${className}`}
        {...props}
      />
      {error ? <div className="mt-1 text-xs font-medium text-rose-600">{error}</div> : null}
    </div>
  )
}
