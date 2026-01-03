export default function Footer() {
  return (
    <div className="mt-10 border-t border-slate-200 bg-slate-900 text-slate-200">
      <div className="mx-auto grid max-w-6xl grid-cols-1 gap-6 px-4 py-10 md:grid-cols-4">
        <div>
          <div className="text-sm font-semibold text-white">Expense AI</div>
          <div className="mt-2 text-xs text-slate-300">
            Track, categorize, and understand your expenses with hybrid AI.
          </div>
        </div>

        <div>
          <div className="text-sm font-semibold text-white">Menu</div>
          <div className="mt-2 space-y-1 text-xs text-slate-300">
            <div>Dashboard</div>
            <div>History</div>
            <div>Upload</div>
            <div>Export</div>
          </div>
        </div>

        <div>
          <div className="text-sm font-semibold text-white">Support</div>
          <div className="mt-2 space-y-1 text-xs text-slate-300">
            <div>Help Center</div>
            <div>Privacy</div>
            <div>Terms</div>
          </div>
        </div>

        <div>
          <div className="text-sm font-semibold text-white">Built for</div>
          <div className="mt-2 text-xs text-slate-300">
            Hackathons & personal finance tracking.
          </div>
        </div>
      </div>

      <div className="border-t border-slate-800">
        <div className="mx-auto max-w-6xl px-4 py-4 text-center text-xs text-slate-400">
          © {new Date().getFullYear()} Expense AI. All rights reserved.
        </div>
      </div>
    </div>
  )
}
