import { useEffect, useState } from 'react'
import api from '../api'
import { useAuth } from '../context/AuthContext.jsx'
import PampangaPicker from '../components/PampangaPicker.jsx'
import ImageUpload from '../components/ImageUpload.jsx'

export default function Profile() {
  const { user, updateUser } = useAuth()
  const [form, setForm] = useState({
    first_name: '', last_name: '', phone: '', email: '',
    municipality: '', barangay: '', address: '', profile_pic: '',
  })
  const [pw, setPw] = useState({ current_password: '', new_password: '', confirm: '' })
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')
  const [pwMsg, setPwMsg] = useState('')
  const [pwErr, setPwErr] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (user) {
      setForm({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone: user.phone || '',
        email: user.email || '',
        municipality: user.municipality || '',
        barangay: user.barangay || '',
        address: user.address || '',
        profile_pic: user.profile_pic || '',
      })
    }
  }, [user])

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const saveProfile = async (e) => {
    e.preventDefault()
    setErr('')
    setMsg('')
    setSaving(true)
    try {
      const res = await api.put('/profile', form)
      updateUser(res.data.user)
      setMsg('Profile updated successfully!')
    } catch (err) {
      setErr(err.response?.data?.error || 'Could not update profile.')
    } finally {
      setSaving(false)
    }
  }

  const changePassword = async (e) => {
    e.preventDefault()
    setPwErr('')
    setPwMsg('')
    if (pw.new_password !== pw.confirm) return setPwErr('New passwords do not match.')
    try {
      await api.put('/profile/password', { current_password: pw.current_password, new_password: pw.new_password })
      setPwMsg('Password updated successfully!')
      setPw({ current_password: '', new_password: '', confirm: '' })
    } catch (err) {
      setPwErr(err.response?.data?.error || 'Could not change password.')
    }
  }

  const initials = `${user?.first_name?.[0] || ''}${user?.last_name?.[0] || ''}`

  return (
    <div className="page">
      <div className="container">
        <h1 className="section-title">My Profile</h1>

        <div className="profile-head">
          {form.profile_pic ? (
            <img className="profile-pic" src={form.profile_pic} alt="profile" />
          ) : (
            <div className="profile-pic">{initials}</div>
          )}
          <div>
            <h2>{user?.first_name} {user?.last_name}</h2>
            <p className="muted">{user?.email}</p>
            <p className="muted">{user?.barangay}, {user?.municipality}</p>
          </div>
        </div>

        <div className="grid grid-2" style={{ alignItems: 'start' }}>
          <form className="card" onSubmit={saveProfile}>
            <h3>Edit Information</h3>
            {msg && <div className="alert alert-success">{msg}</div>}
            {err && <div className="alert alert-error">{err}</div>}

            <div className="form-row">
              <div className="form-group">
                <label>First Name</label>
                <input value={form.first_name} onChange={set('first_name')} required />
              </div>
              <div className="form-group">
                <label>Last Name</label>
                <input value={form.last_name} onChange={set('last_name')} required />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Cellphone Number</label>
                <input value={form.phone} onChange={set('phone')} required />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input type="email" value={form.email} onChange={set('email')} required />
              </div>
            </div>

            <PampangaPicker value={form} onChange={(loc) => setForm((f) => ({ ...f, ...loc }))} />

            <div className="form-group">
              <label>Address / Street</label>
              <input value={form.address} onChange={set('address')} placeholder="House no., street, subdivision" />
            </div>

            <div className="form-group">
              <label>Profile Picture</label>
              <ImageUpload value={form.profile_pic} onChange={(url) => set('profile_pic', url)} placeholder="Upload a photo" />
            </div>

            <button className="btn btn-primary" disabled={saving}>{saving ? 'Saving…' : 'Save Changes'}</button>
          </form>

          <form className="card" onSubmit={changePassword}>
            <h3>Change Password</h3>
            {pwMsg && <div className="alert alert-success">{pwMsg}</div>}
            {pwErr && <div className="alert alert-error">{pwErr}</div>}
            <div className="form-group">
              <label>Current Password</label>
              <input type="password" value={pw.current_password} onChange={(e) => setPw((p) => ({ ...p, current_password: e.target.value }))} required />
            </div>
            <div className="form-group">
              <label>New Password</label>
              <input type="password" value={pw.new_password} onChange={(e) => setPw((p) => ({ ...p, new_password: e.target.value }))} required />
            </div>
            <div className="form-group">
              <label>Confirm New Password</label>
              <input type="password" value={pw.confirm} onChange={(e) => setPw((p) => ({ ...p, confirm: e.target.value }))} required />
            </div>
            <button className="btn btn-secondary">Update Password</button>
          </form>
        </div>
      </div>
    </div>
  )
}