import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import PampangaPicker from '../components/PampangaPicker.jsx'

export default function Signup() {
  const { signup } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    first_name: '', last_name: '', phone: '', email: '',
    password: '', confirm_password: '',
    municipality: '', barangay: '', terms: false,
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const set = (k) => (e) => {
    const val = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setForm((f) => ({ ...f, [k]: val }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const user = await signup(form)
      navigate(user.role === 'admin' ? '/admin' : '/')
    } catch (err) {
      setError(err.response?.data?.error || 'Signup failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-wrap">
      <div className="auth-card" style={{ maxWidth: 560 }}>
        <h1>Create your account</h1>
        <p className="sub">Join Fresh & Shine Cleaning Services</p>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>First Name</label>
              <input value={form.first_name} onChange={set('first_name')} placeholder="Juan" required />
            </div>
            <div className="form-group">
              <label>Last Name</label>
              <input value={form.last_name} onChange={set('last_name')} placeholder="Dela Cruz" required />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Cellphone Number</label>
              <input value={form.phone} onChange={set('phone')} placeholder="09171234567" required />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input type="email" value={form.email} onChange={set('email')} placeholder="you@email.com" required />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Password</label>
              <input type="password" value={form.password} onChange={set('password')} placeholder="Min. 6 characters" required />
            </div>
            <div className="form-group">
              <label>Confirm Password</label>
              <input type="password" value={form.confirm_password} onChange={set('confirm_password')} placeholder="Re-enter password" required />
            </div>
          </div>

          <PampangaPicker
            value={{ municipality: form.municipality, barangay: form.barangay }}
            onChange={(loc) => setForm((f) => ({ ...f, ...loc }))}
            required
          />

          <div className="form-group">
            <label className="checkbox">
              <input type="checkbox" checked={form.terms} onChange={set('terms')} required />
              <span>
                I agree to the <a href="#" onClick={(e) => e.preventDefault()}>Terms &amp; Conditions</a> and{' '}
                <a href="#" onClick={(e) => e.preventDefault()}>Privacy Policy</a>
              </span>
            </label>
          </div>

          <button className="btn btn-primary btn-block" disabled={loading}>
            {loading ? 'Creating account…' : 'Sign Up'}
          </button>
        </form>

        <p className="auth-link">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  )
}