import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api'
import { useAuth } from '../context/AuthContext.jsx'
import { useGet } from '../hooks/useApi.js'
import PampangaPicker from '../components/PampangaPicker.jsx'

const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December']
const DOW = ['Su','Mo','Tu','We','Th','Fr','Sa']

export default function Booking() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const { data: site } = useGet('/site')
  const { data: availability } = useGet('/bookings/availability')
  const [viewDate, setViewDate] = useState(() => {
    const d = new Date()
    return new Date(d.getFullYear(), d.getMonth(), 1)
  })
  const [selectedDate, setSelectedDate] = useState('')
  // The customer can tick any number of services in one booking.
  const [serviceIds, setServiceIds] = useState([])
  const [options, setOptions] = useState({ sqm: '', rooms: '', stories: '', hours: '' })
  const [location, setLocation] = useState({ municipality: user?.municipality || '', barangay: user?.barangay || '' })
  const [notes, setNotes] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  const services = site?.services || []

  // The services the customer has ticked, in the order they are listed.
  const selectedServices = useMemo(
    () => services.filter((s) => serviceIds.includes(s.id)),
    [services, serviceIds]
  )

  // House details (sqm / rooms / stories) are only asked for when at least one
  // house cleaning service is ticked. A booking made up of couch cleaning or
  // other non-house services skips these fields entirely.
  const needsHouseDetails = selectedServices.some((s) => !!s.is_house_service)

  // Any ticked service priced per hour turns the duration field on.
  const usesHours = selectedServices.some((s) => !!s.use_hour)

  const toggleService = (id) => {
    setServiceIds((ids) => (ids.includes(id) ? ids.filter((x) => x !== id) : [...ids, id]))
  }

  // Live price estimate: each ticked service is priced on its own and the
  // results are added together. This mirrors what the backend calculates.
  const estimate = useMemo(() => {
    if (selectedServices.length === 0) return null
    let total = 0
    for (const s of selectedServices) {
      let one = Number(s.base_price || 0)
      if (s.use_sqm) one += Number(s.price_per_sqm || 0) * Number(options.sqm || 0)
      if (s.use_room) one += Number(s.price_per_room || 0) * Number(options.rooms || 0)
      if (s.use_story) one += Number(s.price_per_story || 0) * Number(options.stories || 0)
      if (s.use_hour) one += Number(s.price_per_hour || 0) * Number(options.hours || 0)
      const lo = s.min_price
      const hi = s.max_price
      if (lo != null && one < lo) one = lo
      if (hi != null && one > hi) one = hi
      total += one
    }
    return Math.round(total)
  }, [selectedServices, options])

  const today = useMemo(() => {
    const d = new Date()
    d.setHours(0, 0, 0, 0)
    return d
  }, [])

  const daysInMonth = new Date(viewDate.getFullYear(), viewDate.getMonth() + 1, 0).getDate()
  const firstDow = new Date(viewDate.getFullYear(), viewDate.getMonth(), 1).getDay()

  const dateKey = (d) => {
    const y = d.getFullYear()
    const m = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return `${y}-${m}-${day}`
  }

  const changeMonth = (delta) => {
    setViewDate(new Date(viewDate.getFullYear(), viewDate.getMonth() + delta, 1))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    if (!selectedDate) return setError('Please select a date.')
    if (serviceIds.length === 0) return setError('Please check at least one cleaning service.')
    // House details are only required when a house cleaning service is ticked.
    if (needsHouseDetails) {
      if (!Number(options.sqm) || Number(options.sqm) <= 0) return setError('Please enter the area in square meters (sqm).')
      if (!Number(options.rooms) || Number(options.rooms) <= 0) return setError('Please enter the number of rooms.')
      if (!Number(options.stories) || Number(options.stories) <= 0) return setError('Please enter the number of stories/floors.')
    }
    setLoading(true)
    try {
      await api.post('/bookings', {
        schedule_date: selectedDate,
        service_ids: serviceIds,
        municipality: location.municipality,
        barangay: location.barangay,
        notes,
        // Sent as 0 when only non-house services were picked; the backend
        // ignores these for those bookings and stores NULL.
        sqm: needsHouseDetails ? Number(options.sqm) || 0 : 0,
        rooms: needsHouseDetails ? Number(options.rooms) || 0 : 0,
        stories: needsHouseDetails ? Number(options.stories) || 0 : 0,
        hours: Number(options.hours) || 0,
      })
      setSuccess('Booking created! You can secure your date with a downpayment in My Bookings.')
      setTimeout(() => navigate('/my-bookings'), 1200)
    } catch (err) {
      setError(err.response?.data?.error || 'Could not create booking.')
    } finally {
      setLoading(false)
    }
  }

  const renderCalendar = () => {
    const cells = []
    for (let i = 0; i < firstDow; i++) cells.push(<div key={`e${i}`} />)
    for (let day = 1; day <= daysInMonth; day++) {
      const d = new Date(viewDate.getFullYear(), viewDate.getMonth(), day)
      const key = dateKey(d)
      const isPast = d < today
      const info = availability?.dates?.[key]
      const taken = info && info.count > 0 && !(info.secured > 0)
      const secured = info && info.secured > 0
      let cls = ''
      if (selectedDate === key) cls = 'selected'
      else if (isPast) cls = ''
      else if (secured) cls = 'secured'
      else if (taken) cls = 'taken'
      cells.push(
        <button
          key={key}
          type="button"
          disabled={isPast}
          className={cls}
          onClick={() => setSelectedDate(key)}
          title={secured ? 'Secured by downpayment — still bookable' : taken ? 'Already booked' : ''}
        >
          {day}
        </button>
      )
    }
    return cells
  }

  return (
    <div className="page">
      <div className="container">
        <h1 className="section-title">Book a Cleaning </h1>
        <p className="section-sub">
          Only one booking per day — but you can secure a date by paying a downpayment (first downpayment, first served).
        </p>

        <div className="alert alert-info">
          An admin will call you to confirm your booking by paying a downpayment.
        </div>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <div className="grid grid-2" style={{ alignItems: 'start' }}>
          {/* Calendar */}
          <div className="calendar">
            <div className="calendar-header">
              <button type="button" onClick={() => changeMonth(-1)}>‹</button>
              <strong>{MONTHS[viewDate.getMonth()]} {viewDate.getFullYear()}</strong>
              <button type="button" onClick={() => changeMonth(1)}>›</button>
            </div>
            <div className="calendar-grid">
              {DOW.map((d) => <div className="dow" key={d}>{d}</div>)}
              {renderCalendar()}
            </div>
            <div className="mt-2" style={{ fontSize: '0.85rem' }}>
              <div><span className="muted">Already booked (needs downpayment to secure)</span></div>
              <div><span className="muted">Secured by another customer</span></div>
            </div>
          </div>

          {/* Form */}
          <form className="card" onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Selected Date</label>
              <input value={selectedDate} readOnly placeholder="Pick a date from the calendar" />
            </div>

            {/* Service checkboxes — tick as many as you need */}
            <div className="form-group">
              <label>Cleaning Services *</label>
              <p className="muted" style={{ fontSize: '0.85rem', marginBottom: 8 }}>
                Check every service you want to avail. You can pick more than one.
              </p>
              <div className="service-checklist">
                {services.length === 0 && <p className="muted">No services available yet.</p>}
                {services.map((s) => (
                  <label key={s.id} className={`service-check ${serviceIds.includes(s.id) ? 'on' : ''}`}>
                    <input
                      type="checkbox"
                      checked={serviceIds.includes(s.id)}
                      onChange={() => toggleService(s.id)}
                    />
                    <span className="service-check-body">
                      <span className="service-check-name">{s.name}</span>
                      {s.description && (
                        <span className="muted service-check-desc">{s.description}</span>
                      )}
                      {/* Tell the customer which services need house details */}
                      <span className="service-check-tag muted">
                        {s.is_house_service ? 'House details required' : 'No house details needed'}
                      </span>
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Selected services, shown clearly */}
            {selectedServices.length > 0 && (
              <div className="card-inner">
                <h4>Selected Services ({selectedServices.length})</h4>
                <ul className="selected-list">
                  {selectedServices.map((s) => (
                    <li key={s.id}>
                      <span>{s.name}</span>
                      <button
                        type="button"
                        className="link-btn"
                        onClick={() => toggleService(s.id)}
                        aria-label={`Remove ${s.name}`}
                      >
                        Remove
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* House details — only when a house cleaning service is checked */}
            {needsHouseDetails ? (
              <div className="card-inner">
                <h4>House Details</h4>
                <p className="muted" style={{ fontSize: '0.85rem' }}>
                  You picked a house cleaning service, so please tell us about the house. These are required.
                </p>
                <div className="grid grid-2">
                  <div className="form-group">
                    <label>Area (sqm) *</label>
                    <input type="number" min="1" value={options.sqm} onChange={(e) => setOptions((o) => ({ ...o, sqm: e.target.value }))} placeholder="e.g. 80" required />
                  </div>
                  <div className="form-group">
                    <label>Rooms *</label>
                    <input type="number" min="1" value={options.rooms} onChange={(e) => setOptions((o) => ({ ...o, rooms: e.target.value }))} placeholder="e.g. 3" required />
                  </div>
                  <div className="form-group">
                    <label>Stories / Floors *</label>
                    <input type="number" min="1" value={options.stories} onChange={(e) => setOptions((o) => ({ ...o, stories: e.target.value }))} placeholder="e.g. 2" required />
                  </div>
                  {usesHours && (
                    <div className="form-group">
                      <label>Duration (hours)</label>
                      <input type="number" min="0" value={options.hours} onChange={(e) => setOptions((o) => ({ ...o, hours: e.target.value }))} placeholder="e.g. 4" />
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="alert alert-info">
                No House Details required
              </div>
            )}

            

            <PampangaPicker value={location} onChange={setLocation} required />

            <div className="form-group">
              <label>Notes (optional)</label>
              <textarea rows="3" value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Any special instructions…" />
            </div>

            <button className="btn btn-primary btn-block" disabled={loading}>
              {loading ? 'Booking…' : 'Book Now'}
            </button>
            <p className="muted mt-1" style={{ fontSize: '0.85rem' }}>
              Payment can be done through <Link to="/my-bookings">My Bookings</Link>.
            </p>
          </form>
        </div>
      </div>
    </div>
  )
}
