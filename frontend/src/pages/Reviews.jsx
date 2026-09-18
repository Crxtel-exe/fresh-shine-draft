import { useEffect, useState } from 'react'
import api from '../api'
import { useAuth } from '../context/AuthContext.jsx'
import { useGet } from '../hooks/useApi.js'
import StarRating from '../components/StarRating.jsx'

export default function Reviews() {
  const { user } = useAuth()
  const { data: site } = useGet('/site')
  const [reviews, setReviews] = useState([])
  const [myBookings, setMyBookings] = useState([])
  const [rating, setRating] = useState(0)
  const [comment, setComment] = useState('')
  const [bookingId, setBookingId] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const reviewsRes = await api.get('/reviews')
      const publicReviews = reviewsRes.data.reviews || []
      setReviews(publicReviews)

      if (user) {
        const bookingsRes = await api.get('/bookings')
        const reviewedBookingIds = new Set(
          publicReviews
            .filter((r) => String(r.user_id) === String(user.id))
            .map((r) => Number(r.booking_id))
        )
        setMyBookings(
          (bookingsRes.data.bookings || []).filter(
            (b) => b.status === 'completed' && !reviewedBookingIds.has(Number(b.id))
          )
        )
      } else {
        setMyBookings([])
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [user])

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    if (!bookingId) return setError('Please select a completed booking.')
    if (!rating) return setError('Please select a rating.')
    try {
      await api.post('/reviews', { booking_id: Number(bookingId), rating, comment })
      setSuccess('Thank you for your review!')
      setRating(0)
      setComment('')
      setBookingId('')
      load()
    } catch (err) {
      setError(err.response?.data?.error || 'Could not submit review.')
    }
  }

  if (loading) return <div className="spinner" />

  return (
    <div className="page">
      <div className="container">
        <h1 className="section-title">Reviews &amp; Ratings</h1>
        <p className="section-sub">See what our customers say and rate your completed booking</p>

        {/* Rate a booking */}
        {user && (
          <div className="card mb-2" style={{ maxWidth: 640 }}>
            <h3>Rate your booking</h3>
            {error && <div className="alert alert-error">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}
            <form onSubmit={submit}>
              <div className="form-group">
                <label>Completed Booking</label>
                <select value={bookingId} onChange={(e) => setBookingId(e.target.value)}>
                  <option value="">Select a completed booking…</option>
                  {myBookings.map((b) => (
                    <option key={b.id} value={b.id}>{b.service_name} — {b.schedule_date}</option>
                  ))}
                </select>
                {myBookings.length === 0 && (
                  <p className="muted mt-1" style={{ fontSize: '0.85rem' }}>
                    You can only rate a booking once it's completed.
                  </p>
                )}
              </div>
              <div className="form-group">
                <label>Rating</label>
                <StarRating value={rating} onChange={setRating} />
              </div>
              <div className="form-group">
                <label>Comment</label>
                <textarea rows="3" value={comment} onChange={(e) => setComment(e.target.value)} placeholder="Tell us about your experience…" />
              </div>
              <button className="btn btn-primary" disabled={myBookings.length === 0}>Submit Review</button>
            </form>
          </div>
        )}

        {/* All reviews */}
        <section>
          <h2 className="section-title">Customer Reviews</h2>
          {reviews.length === 0 ? (
            <div className="card empty">No reviews yet. Be the first!</div>
          ) : (
            <div className="card">
              {reviews.map((r) => (
                <div className="review-item" key={r.id}>
                  <div className="review-head">
                    <strong>{r.user_name}</strong>
                    <StarRating value={r.rating} size="1rem" />
                  </div>
                  <p>{r.comment}</p>
                  {r.admin_reply && (
                    <div className="review-reply">
                      <strong>{site?.company_name || 'Company'} replied:</strong> {r.admin_reply}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}