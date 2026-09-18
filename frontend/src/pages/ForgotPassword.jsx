import { useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api'

export default function ForgotPassword() {
  const [step, setStep] = useState(1) // 1 = request, 2 = reset
  const [identifier, setIdentifier] = useState('')
  const [token, setToken] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const requestReset = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await api.post('/auth/forgot', { identifier })
      setMessage(res.data.message)
      if (res.data.reset_token) {
        setToken(res.data.reset_token)
        setStep(2)
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  const resetPassword = async (e) => {
    e.preventDefault()
    setError('')
    if (password !== confirm) {
      setError('Passwords do not match.')
      return
    }
    setLoading(true)
    try {
      const res = await api.post('/auth/reset-password', { token, password })
      setMessage(res.data.message)
      setStep(3)
    } catch (err) {
      setError(err.response?.data?.error || 'Reset failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <h1>Reset password</h1>
        <p className="sub">We'll help you get back in</p>

        {message && <div className="alert alert-success">{message}</div>}
        {error && <div className="alert alert-error">{error}</div>}

        {step === 1 && (
          <form onSubmit={requestReset}>
            <div className="form-group">
              <label>Email or Cellphone Number</label>
              <input
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder="you@email.com or 09171234567"
                required
              />
            </div>
            <button className="btn btn-primary btn-block" disabled={loading}>
              {loading ? 'Sending…' : 'Send reset link'}
            </button>
          </form>
        )}

        {step === 2 && (
          <form onSubmit={resetPassword}>
            <div className="form-group">
              <label>New Password</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Min. 6 characters" required />
            </div>
            <div className="form-group">
              <label>Confirm New Password</label>
              <input type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} placeholder="Re-enter password" required />
            </div>
            <button className="btn btn-primary btn-block" disabled={loading}>
              {loading ? 'Resetting…' : 'Reset password'}
            </button>
          </form>
        )}

        {step === 3 && (
          <Link to="/login" className="btn btn-primary btn-block">Go to Login</Link>
        )}

        <p className="auth-link">
          Remembered it? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  )
}