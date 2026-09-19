import { useEffect, useState } from 'react'
import api from '../api'
import { useGet } from '../hooks/useApi.js'
import Badge from '../components/Badge.jsx'
import ContactModal from '../components/ContactModal.jsx'
import { companyContactRows } from '../config/companyContact.js'

export default function MyBookings() {
  const [bookings, setBookings] = useState([])
  const { data: site } = useGet('/site')
  const [loading, setLoading] = useState(true)
  // Which booking's "Contact Admin" pop-up is open (null = none).
  const [contactOpen, setContactOpen] = useState(false)

  const load = () => {
    api.get('/bookings').then((res) => setBookings(res.data.bookings))
    setLoading(false)
  }

  useEffect(load, [])


  // A booking can hold several services; fall back to the single name.
  const serviceLabel = (b) =>
    (b.service_names && b.service_names.length ? b.service_names.join(', ') : b.service_name) || '—'

  if (loading) return <div className="spinner" />

  return (
    <div className="page">
      <div className="container">
        <h1 className="section-title">My Bookings</h1>
        <p className="section-sub">Track your bookings and contact the company</p>

        

        {bookings.length === 0 ? (
          <div className="card empty">
            <p>You have no bookings yet.</p>
            <a href="/booking" className="btn btn-primary mt-2">Book a Cleaning</a>
          </div>
        ) : (
          <div className="grid">
            {bookings.map((b) => (
              <div className="card" key={b.id}>
                <div className="flex between wrap">
                  <div>
                    <h3>{serviceLabel(b)}</h3>
                    <p className="muted">{b.schedule_date}</p>
                    <p className="muted">{b.barang}, {b.municipality}</p>
                  </div>
                  <div className="flex wrap">
                    <Badge value={b.status} />
                    <Badge value={b.payment_status} />
                  </div>
                </div>

                {/* All the services this booking covers */}
                {b.service_names && b.service_names.length > 1 && (
                  <div className="mt-1">
                    <span className="muted" style={{ fontSize: '0.85rem' }}>
                      Services availed ({b.service_names.length}):
                    </span>
                    <ul className="selected-list">
                      {b.service_names.map((n) => <li key={n}><span>{n}</span></li>)}
                    </ul>
                  </div>
                )}

                {b.notes && <p className="mt-1 muted">{b.notes}</p>}
                {(b.floor_area_sqm || b.rooms || b.stories) && (
                  <p className="mt-1 muted">
                    {b.floor_area_sqm ? `${Number(b.floor_area_sqm).toLocaleString()} sqm` : ''}
                    {b.rooms ? ` · ${b.rooms} room${b.rooms > 1 ? 's' : ''}` : ''}
                    {b.stories ? ` · ${b.stories} stor${b.stories > 1 ? 'ies' : 'y'}` : ''}
                  </p>
                )}
                {b.price > 0 && <p className="mt-1">Estimated price: ₱{Number(b.price).toLocaleString()}</p>}
                {b.downpayment > 0 && <p className="mt-1">Downpayment paid: ₱{Number(b.downpayment).toLocaleString()}</p>}

                <div className="flex wrap mt-2" style={{ gap: 10 }}>
                  <button
                    className="btn btn-outline btn-sm"
                    onClick={() => setContactOpen(true)}
                  >
                    Contact Admin
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {contactOpen && (
        <ContactModal
          title="Contact Admin"
          subtitle="Reach us through any of the details below."
          contacts={companyContactRows()}
          onClose={() => setContactOpen(false)}
        />
      )}
    </div>
  )
}
