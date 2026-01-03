import type { PropsWithChildren } from 'react'

import Footer from './Footer'
import Header from './Header'

export default function Layout({ children }: PropsWithChildren) {
  return (
    <div className="min-h-full bg-slate-50">
      <Header />
      <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
      <Footer />
    </div>
  )
}
