import { useEffect, useState } from 'react'

import Button from '../components/Button'
import Card from '../components/Card'
import Input from '../components/Input'

export default function Settings() {
  const [monthlyBudget, setMonthlyBudget] = useState('')
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    const v = localStorage.getItem('monthly_budget_inr') || ''
    setMonthlyBudget(v)
  }, [])

  function save() {
    localStorage.setItem('monthly_budget_inr', monthlyBudget.trim())
    setSaved(true)
    window.setTimeout(() => setSaved(false), 1500)
  }

  return (
    <div className="py-2 sm:py-4">
      <div className="mx-auto max-w-2xl">
        <Card>
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Settings</h1>
              <p className="mt-1 text-sm text-slate-600">Preferences saved locally for now.</p>
            </div>
          </div>

          <div className="mt-6 grid gap-5">
            <div>
              <label className="block text-sm font-semibold text-slate-800">Monthly budget (₹)</label>
              <div className="mt-2">
                <Input
                  inputMode="numeric"
                  placeholder="e.g. 25000"
                  value={monthlyBudget}
                  onChange={(e) => setMonthlyBudget(e.target.value)}
                />
              </div>
              <p className="mt-2 text-xs text-slate-500">
                This will be used for overspending warnings in AI Insights.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <Button type="button" onClick={save}>
                Save
              </Button>
              {saved ? <span className="text-sm font-semibold text-emerald-700">Saved</span> : null}
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
