import { Link, NavLink, useNavigate } from 'react-router-dom'

import { clearToken, getToken } from '../lib/storage'
import { setAuthToken } from '../lib/api'

function NavItem({ to, label }: { to: string; label: string }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `rounded-lg px-3 py-2 text-sm ${isActive ? 'bg-slate-900 text-white' : 'text-slate-700 hover:bg-slate-100'}`
      }
    >
      {label}
    </NavLink>
  )
}

export default function Navbar() {
  const navigate = useNavigate()
  const token = getToken()

  return (
    <div className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link to="/" className="text-sm font-semibold text-slate-900">
          Expense AI
        </Link>

        <div className="flex items-center gap-2">
          {token ? (
            <>
              <NavItem to="/dashboard" label="Dashboard" />
              <NavItem to="/history" label="History" />
              <NavItem to="/upload" label="Upload" />
              <NavItem to="/insights" label="AI Insights" />
              <button
                className="ml-2 rounded-lg px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
                onClick={() => {
                  clearToken()
                  setAuthToken(null)
                  navigate('/login')
                }}
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <NavItem to="/login" label="Login" />
              <NavItem to="/signup" label="Sign up" />
            </>
          )}
        </div>
      </div>
    </div>
  )
}
