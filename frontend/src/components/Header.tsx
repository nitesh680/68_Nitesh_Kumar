import { Link, NavLink, useNavigate } from 'react-router-dom'

import { clearToken, getToken } from '../lib/storage'
import { setAuthToken } from '../lib/api'

function MenuLink({ to, label }: { to: string; label: string }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `rounded-md px-3 py-2 text-sm font-medium ${
          isActive ? 'bg-slate-800 text-white' : 'text-slate-200 hover:bg-slate-800'
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
    <div className="bg-slate-900">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
        <Link to="/" className="flex items-center gap-2 text-white">
          <div className="rounded-md bg-amber-300 px-2 py-1 text-xs font-bold text-slate-900">AI</div>
          <div className="text-sm font-semibold">Expense</div>
        </Link>

        <div className="hidden items-center gap-1 md:flex">
          <MenuLink to="/dashboard" label="Dashboard" />
          <MenuLink to="/history" label="History" />
          <MenuLink to="/upload" label="Upload" />
          <MenuLink to="/export" label="Export" />
          <MenuLink to="/insights" label="AI Insights" />
        </div>

        <div className="flex items-center gap-2">
          {token ? (
            <button
              className="rounded-md bg-slate-800 px-3 py-2 text-sm font-medium text-slate-200 hover:bg-slate-700"
              onClick={() => {
                clearToken()
                setAuthToken(null)
                navigate('/login')
              }}
            >
              Logout
            </button>
          ) : (
            <>
              <NavLink
                to="/login"
                className={({ isActive }) =>
                  `rounded-md px-3 py-2 text-sm font-medium ${
                    isActive ? 'bg-slate-800 text-white' : 'text-slate-200 hover:bg-slate-800'
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

      <div className="border-t border-slate-800 md:hidden">
        <div className="mx-auto flex max-w-6xl items-center gap-1 overflow-x-auto px-4 py-2">
          <MenuLink to="/dashboard" label="Dashboard" />
          <MenuLink to="/history" label="History" />
          <MenuLink to="/upload" label="Upload" />
          <MenuLink to="/export" label="Export" />
          <MenuLink to="/insights" label="AI Insights" />
        </div>
      </div>
    </div>
  )
}
