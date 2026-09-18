import { useEffect, useState } from 'react'
import api from '../api'

/**
 * Loads data from an API endpoint with loading/error state.
 * Returns { data, loading, error, reload }.
 * Pass `deps` to re-fetch when they change (default: run once on mount).
 */
export function useApi(fetcher, deps = []) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = () => {
    setLoading(true)
    setError('')
    fetcher()
      .then((res) => setData(res.data))
      .catch((err) => setError(err.response?.data?.error || 'Something went wrong.'))
      .finally(() => setLoading(false))
  }

  useEffect(load, deps) // eslint-disable-line react-hooks/exhaustive-deps
  return { data, loading, error, reload: load }
}

/** Convenience wrapper: fetch a single endpoint by URL. */
export function useGet(url, deps = []) {
  return useApi(() => api.get(url), deps)
}