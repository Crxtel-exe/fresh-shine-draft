import { useEffect, useState } from 'react'
import api from '../../api'
import { useGet } from '../../hooks/useApi.js'
import ContactModal from '../../components/ContactModal.jsx'

const STATUSES = ['pending', 'confirmed', 'completed', 'cancelled']
const PAYMENTS = ['unpaid', 'partial', 'paid']

export default function AdminBookings() {
  const [bookings, setBookings] = useState([])
  const { data: site } = useGet('/site')
  const [msg, setMsg] = useState('')
  const [loading, setLoading] = useState(true)
  // The customer whose details the admin is looking at (null = no pop-up).
  const [contactCustomer, setContactCustomer] = useState(null)

  const load = () => {
    api.get('/admin/bookings').then((res) => setBookings(res.data.bookings))
    setLoading(false)
  }

  useEffect(load, [])

  const updateBooking = async (id, field, value) => {
    setMsg('')
    try {
      await api.put(`/admin/bookings/${id}`, { [field]: value })
      load()
    } catch (err) {
      setMsg(err.response?.data?.error || 'Update failed.')
    }
  }

  const mapUrl = (b) =>
    `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${b.barang}, ${b.municipality}, Pampanga, Philippines`)}`

  // A booking can hold several services; fall back to the single name.
  const serviceLabel = (b) =>
    (b.service_names && b.service_names.length ? b.service_names.join(', ') : b.service_name) || '—'

  // The customer's contact details, for the Contact Customer pop-up.
  const customerContacts = (b) =>
    b
      ? [
          { key: 'email', label: 'Email', value: b.customer_email, icon: '', href: `mailto:${b.customer_email}` },
          {
            key: 'phone',
            label: 'Contact Number',
            value: b.customer_phone,
            icon: '',
            href: `tel:${String(b.customer_phone || '').replace(/\s/g, '')}`,
          },
        ].filter((c) => c.value)
      : []

  if (loading) return <div className="spinner" />

  return (
    <div className="page">
      <div className="container">
        <h1 className="section-title">All Bookings</h1>
        <p className="section-sub">Manage booking status and payment status</p>

        {msg && <div className="alert alert-error">{msg}</div>}

        {bookings.length === 0 ? (
          <div className="card empty">No bookings yet.</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Customer</th>
                  <th>Service</th>
                  <th>Schedule</th>
                  <th>Location</th>
                  <th>Status</th>
                  <th>Payment</th>
                  <th>Downpayment</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {bookings.map((b) => (
                  <tr key={b.id}>
                    <td>
                      <strong>{b.customer_name}</strong>
                      <div className="muted" style={{ fontSize: '0.8rem' }}>{b.customer_phone}</div>
                      <div className="muted" style={{ fontSize: '0.8rem' }}>{b.customer_email}</div>
                    </td>
                    <td>
                      {serviceLabel(b)}
                      {b.service_names && b.service_names.length > 1 && (
                        <div className="muted" style={{ fontSize: '0.78rem' }}>
                          {b.service_names.length} services
                        </div>
                      )}
                    </td>
                    <td>{b.schedule_date}</td>
                    <td>
                      <a href={mapUrl(b)} target="_blank" rel="noreferrer">{b.barang}, {b.municipality}</a>
                    </td>
                    <td>
                      <select value={b.status} onChange={(e) => updateBooking(b.id, 'status', e.target.value)}>
                        {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                      </select>
                    </td>
                    <td>
                      <select value={b.payment_status} onChange={(e) => updateBooking(b.id, 'payment_status', e.target.value)}>
                        {PAYMENTS.map((p) => <option key={p} value={p}>{p}</option>)}
                      </select>
                    </td>
                    <td>
                      <input
                        type="number"
                        min="0"
                        value={b.downpayment || ''}
                        onBlur={(e) => updateBooking(b.id, 'downpayment', Number(e.target.value) || 0)}
                        style={{ width: 90 }}
                      />
                    </td>
                    <td>
                      {/* Shows the customer's email and contact number only. */}
                      <button
                        className="btn btn-outline btn-sm"
                        onClick={() => setContactCustomer(b)}
                      >
                        Contact Customer
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {contactCustomer && (
        <ContactModal
          title="Contact Customer"
          subtitle={`${contactCustomer.customer_name} · Booking #${contactCustomer.id}`}
          contacts={customerContacts(contactCustomer)}
          onClose={() => setContactCustomer(null)}
        />
      )}
    </div>
  )
}
