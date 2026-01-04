import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'

import { useProfile } from '../hooks/useProfile'

export default function UserProfileAvatar({ onLogout }: { onLogout: () => void }) {
  const { data: profile, isLoading } = useProfile()
  const [open, setOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (!menuRef.current) return
      if (!menuRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', onDocClick)
    return () => document.removeEventListener('mousedown', onDocClick)
  }, [])

  if (isLoading) {
    return (
      <div className="w-10 h-10 rounded-full bg-slate-700 animate-pulse"></div>
    )
  }

  if (!profile) {
    return null
  }

  return (
    <div ref={menuRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-3 rounded-lg px-2 py-1 transition hover:bg-white/10"
      >
        <div className="hidden sm:block text-left">
          <p className="text-sm font-semibold text-white leading-tight">{profile.name}</p>
        </div>
        <div className="w-10 h-10 rounded-full overflow-hidden bg-gradient-to-br from-indigo-500 to-purple-600 p-0.5 flex-shrink-0">
          <div className="w-full h-full rounded-full overflow-hidden bg-slate-900 flex items-center justify-center">
            {profile.avatar_url ? (
              <img
                src={profile.avatar_url}
                alt="Avatar"
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="text-sm font-bold text-white">{profile.name.charAt(0).toUpperCase()}</div>
            )}
          </div>
        </div>
      </button>

      {open ? (
        <div className="absolute right-0 mt-2 w-52 overflow-hidden rounded-xl border border-white/10 bg-slate-950/95 shadow-lg backdrop-blur">
          <div className="px-3 py-2">
            <div className="text-xs text-slate-400">Signed in as</div>
            <div className="text-sm font-semibold text-white truncate">{profile.name}</div>
          </div>
          <div className="h-px bg-white/10" />
          <Link
            to="/profile"
            onClick={() => setOpen(false)}
            className="block px-3 py-2 text-sm text-slate-200 hover:bg-white/10"
          >
            View profile
          </Link>
          <Link
            to="/settings"
            onClick={() => setOpen(false)}
            className="block px-3 py-2 text-sm text-slate-200 hover:bg-white/10"
          >
            Settings
          </Link>
          <button
            type="button"
            onClick={() => {
              setOpen(false)
              onLogout()
            }}
            className="block w-full px-3 py-2 text-left text-sm text-rose-200 hover:bg-rose-500/10"
          >
            Logout
          </button>
        </div>
      ) : null}
    </div>
  )
}
