import type { PropsWithChildren } from 'react'

import Footer from './Footer'
import Header from './Header'

export default function Layout({ children }: PropsWithChildren) {
  return (
    <div className="min-h-full bg-gradient-to-br from-slate-50 via-white to-indigo-50">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-24 -right-24 h-72 w-72 rounded-full bg-indigo-200/40 blur-3xl" />
        <div className="absolute top-48 -left-24 h-72 w-72 rounded-full bg-sky-200/40 blur-3xl" />
        <div className="absolute bottom-0 right-24 h-72 w-72 rounded-full bg-amber-200/30 blur-3xl" />
      </div>

      <div className="relative">
        <Header />
        <main className="mx-auto max-w-6xl px-4 py-8 md:py-10">{children}</main>
        <Footer />
      </div>
    </div>
  )
}
