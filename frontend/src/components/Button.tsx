import type { ButtonHTMLAttributes } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary'
}

export default function Button({ className = '', variant = 'primary', ...props }: ButtonProps) {
  const baseStyles = 'inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-semibold shadow-sm transition focus:outline-none focus:ring-2 focus:ring-indigo-300 disabled:cursor-not-allowed disabled:opacity-60'
  const variantStyles = {
    primary: 'bg-gradient-to-r from-slate-900 to-indigo-900 text-white hover:from-slate-800 hover:to-indigo-800',
    secondary: 'bg-white/10 text-slate-100 ring-1 ring-white/10 hover:bg-white/15',
  }
  
  return (
    <button
      className={`${baseStyles} ${variantStyles[variant]} ${className}`}
      {...props}
    />
  )
}
