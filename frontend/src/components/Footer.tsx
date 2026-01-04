import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <div className="mt-12 border-t border-white/10 bg-slate-950/80 text-slate-200 backdrop-blur">
      <div className="mx-auto grid max-w-6xl grid-cols-1 gap-8 px-4 py-10 sm:grid-cols-2 md:grid-cols-4">
        <div className="sm:col-span-2 md:col-span-1">
          <div className="text-sm font-semibold text-white">Expense AI</div>
          <div className="mt-2 text-xs text-slate-300 max-w-xs">
            Track, categorize, and understand your expenses with hybrid AI.
          </div>
        </div>

        <div>
          <div className="text-sm font-semibold text-white">Menu</div>
          <div className="mt-2 space-y-1 text-xs text-slate-300">
            <Link to="/dashboard" className="block hover:text-white transition">Dashboard</Link>
            <Link to="/history" className="block hover:text-white transition">History</Link>
            <Link to="/upload" className="block hover:text-white transition">Upload</Link>
            <Link to="/export" className="block hover:text-white transition">Export</Link>
            <Link to="/profile" className="block hover:text-white transition">Profile</Link>
          </div>
        </div>

        <div>
          <div className="text-sm font-semibold text-white">Support</div>
          <div className="mt-2 space-y-1 text-xs text-slate-300">
            <div className="hover:text-white transition cursor-pointer">Help Center</div>
            <div className="hover:text-white transition cursor-pointer">Privacy</div>
            <div className="hover:text-white transition cursor-pointer">Terms</div>
          </div>
        </div>

        <div className="sm:col-span-2 md:col-span-1">
          <div className="text-sm font-semibold text-white">Built for</div>
          <div className="mt-2 text-xs text-slate-300 max-w-xs">
            Hackathons & personal finance tracking.
          </div>
        </div>
      </div>

      <div className="border-t border-white/10">
        <div className="mx-auto max-w-6xl px-4 py-4 text-center text-xs text-slate-400">
          © {new Date().getFullYear()} Expense AI. All rights reserved.
        </div>
      </div>
    </div>
  )
}
