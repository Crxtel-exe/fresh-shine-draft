import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

/** Redirects to /login when not authenticated, and to / when not an admin. */
export default function AdminRoute({ children }) {
  const { user, loading, isAdmin } = useAuth()
  if (loading) return <div className="spinner" />
  if (!user) return <Navigate to="/login" replace />
  if (!isAdmin) return <Navigate to="/" replace />
  return children
}