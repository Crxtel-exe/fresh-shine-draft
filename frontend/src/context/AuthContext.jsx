import { createContext, useContext, useEffect, useState } from 'react'
import api from '../api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('user')) || null
    } catch {
      return null
    }
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      api
        .get('/auth/me')
        .then((res) => {
          setUser(res.data.user)
          localStorage.setItem('user', JSON.stringify(res.data.user))
        })
        .catch(() => {
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          setUser(null)
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const setSession = (token, userData) => {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(userData))
    setUser(userData)
  }

  const login = async (identifier, password) => {
    const res = await api.post('/auth/login', { identifier, password })
    setSession(res.data.token, res.data.user)
    return res.data.user
  }

  const signup = async (payload) => {
    const res = await api.post('/auth/signup', payload)
    setSession(res.data.token, res.data.user)
    return res.data.user
  }

  const logout = async () => {
    // Invalidate the token server-side (best-effort; ignore failures so
    // logout still works even if the backend is unreachable).
    try {
      await api.post(isAdmin ? '/admin/logout' : '/auth/logout')
    } catch {
      /* token may already be invalid */
    }
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
  }

  const updateUser = (userData) => {
    setUser(userData)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const isAdmin = user?.role === 'admin'

  return (
    <AuthContext.Provider
      value={{ user, loading, login, signup, logout, updateUser, isAdmin }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}