import { useEffect, useState } from 'react'
import api from '../api.js'

/**
 * Shows the ready-to-use sample logins on the Login page.
 *
 * This is the demo build, so the credentials come straight from the backend
 * (`GET /api/demo-accounts`, seeded in `backend/store.py`) and are shown openly
 * on purpose. Clicking a row fills the login form for you.
 *
 * If the backend is not running yet this renders nothing, so the page still
 * works normally.
 */
export default function DemoAccounts({ onUse }) {
  const [accounts, setAccounts] = useState([])

  useEffect(() => {
    let active = true
    api
      .get('/demo-accounts')
      .then((res) => {
        if (active) setAccounts(res.data?.accounts || [])
      })
      .catch(() => {
        /* backend not reachable yet - just hide the hint */
      })
    return () => {
      active = false
    }
  }, [])

  if (accounts.length === 0) return null

  
}
