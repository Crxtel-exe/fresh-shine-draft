import { useEffect, useState } from 'react'
import api from '../../api'
import StarRating from '../../components/StarRating.jsx'

export default function AdminReviews() {
  const [reviews, setReviews] = useState([])
  const [replies, setReplies] = useState({})
  const [msg, setMsg] = useState('')
  const [loading, setLoading] = useState(true)

  const load = () => {
    api.get('/admin/reviews').then((res) => {
      setReviews(res.data.reviews)
      const r = {}
      res.data.reviews.forEach((rev) => (r[rev.id] = rev.admin_reply || ''))
      setReplies(r)
    })
    setLoading(false)
  }

  useEffect(load, [])

  const saveReply = async (id) => {
    setMsg('')
    try {
      await api.put(`/admin/reviews/${id}`, { admin_reply: replies[id] })
      setMsg('Reply saved!')
      load()
    } catch (err) {
      setMsg(err.response?.data?.error || 'Could not save reply.')
    }
  }

  if (loading) return <div className="spinner" />

  return (
    <div className="page">
      <div className="container">
        <h1 className="section-title">Manage Reviews</h1>
        <p className="section-sub">Review customer feedback and reply</p>

        {msg && <div className="alert alert-success">{msg}</div>}

        {reviews.length === 0 ? (
          <div className="card empty">No reviews yet.</div>
        ) : (
          <div className="grid">
            {reviews.map((r) => (
              <div className="card" key={r.id}>
                <div className="flex between wrap">
                  <div>
                    <strong>{r.customer_name}</strong>
                    <div className="muted" style={{ fontSize: '0.85rem' }}>{r.service_name} — {r.schedule_date}</div>
                  </div>
                  <StarRating value={r.rating} size="1rem" />
                </div>
                <p className="mt-1">{r.comment}</p>
                <div className="form-group mt-2">
                  <label>Your Reply</label>
                  <textarea
                    rows="2"
                    value={replies[r.id] || ''}
                    onChange={(e) => setReplies((prev) => ({ ...prev, [r.id]: e.target.value }))}
                    placeholder="Reply to this review…"
                  />
                </div>
                <button className="btn btn-primary btn-sm" onClick={() => saveReply(r.id)}>Save Reply</button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}