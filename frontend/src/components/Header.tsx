import { Link, NavLink, useNavigate } from 'react-router-dom'

import { clearToken, getToken } from '../lib/storage'
import { setAuthToken } from '../lib/api'
import UserProfileAvatar from './UserProfileAvatar'

function MenuLink({ to, label }: { to: string; label: string }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `rounded-lg px-3 py-2 text-sm font-semibold transition ${
          isActive
            ? 'bg-white/10 text-white ring-1 ring-white/10'
            : 'text-slate-200 hover:bg-white/10 hover:text-white'
        }`
      }
    >
      {label}
    </NavLink>
  )
}

function AccountLink({ to, label }: { to: string; label: string }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `rounded-md px-3 py-2 text-sm font-medium ${
          isActive ? 'bg-amber-400 text-slate-900' : 'bg-amber-300 text-slate-900 hover:bg-amber-400'
        }`
      }
    >
      {label}
    </NavLink>
  )
}

export default function Header() {
  const navigate = useNavigate()
  const token = getToken()

  return (
    <div className="sticky top-0 z-50 border-b border-white/10 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
        <Link to="/" className="flex items-center gap-2 text-white">
          <div className="rounded-md bg-gradient-to-r from-amber-300 to-amber-200 px-2 py-1 text-xs font-extrabold text-slate-900">
            AI
          </div>
          <div className="text-sm font-semibold tracking-tight">Expense</div>
        </Link>

        <div className="hidden items-center gap-1 md:flex">
          <MenuLink to="/dashboard" label="Dashboard" />
          <MenuLink to="/history" label="History" />
          <MenuLink to="/upload" label="Upload" />
          <MenuLink to="/export" label="Export" />
          <MenuLink to="/profile" label="Profile" />
          <MenuLink to="/insights" label="AI Insights" />
        </div>

        <div className="flex items-center gap-2">
          {token ? (
            <>
              <UserProfileAvatar
                onLogout={() => {
                  clearToken()
                  setAuthToken(null)
                  navigate('/login')
                }}
              />
            </>
          ) : (
            <>
              <NavLink
                to="/login"
                className={({ isActive }) =>
                  `rounded-lg px-3 py-2 text-sm font-semibold transition ${
                    isActive ? 'bg-white/10 text-white ring-1 ring-white/10' : 'text-slate-200 hover:bg-white/10'
                  }`
                }
              >
                Login
              </NavLink>
              <AccountLink to="/signup" label="Sign up" />
            </>
          )}
        </div>
      </div>

      <div className="border-t border-white/10 md:hidden">
        <div className="mx-auto flex max-w-6xl items-center gap-1 overflow-x-auto px-4 py-2">
          <MenuLink to="/dashboard" label="Dashboard" />
          <MenuLink to="/history" label="History" />
          <MenuLink to="/upload" label="Upload" />
          <MenuLink to="/export" label="Export" />
          <MenuLink to="/profile" label="Profile" />
          <MenuLink to="/insights" label="AI Insights" />
        </div>
      </div>
    </div>
  )
}
