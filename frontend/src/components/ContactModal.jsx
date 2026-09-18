import { useEffect } from 'react'

/**
 * A small reusable contact pop-up.
 *
 * Used in two places:
 *  - My Bookings   -> "Contact Admin"    shows the company's phone/email/Facebook
 *  - Admin Bookings -> "Contact Customer" shows the customer's email/phone
 *
 * Props:
 *   title    - heading shown at the top
 *   subtitle - optional small line under the heading
 *   contacts - array of { key, label, value, icon, href }
 *   onClose  - called when the user closes the pop-up
 */
export default function ContactModal({ title, subtitle, contacts, onClose }) {
  // Close on Escape, and stop the page behind from scrolling while open.
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKey)
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = previousOverflow
    }
  }, [onClose])

  const rows = (contacts || []).filter((c) => c && c.value)

  return (
    <div className="modal-backdrop" onClick={onClose} role="presentation">
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h3>{title}</h3>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>

        {subtitle && <p className="muted" style={{ fontSize: '0.85rem' }}>{subtitle}</p>}

        <div className="modal-body">
          {rows.length === 0 ? (
            <p className="muted">No contact details available.</p>
          ) : (
            rows.map((c) => (
              <div className="contact-row" key={c.key}>
                <span className="contact-icon" aria-hidden="true">{c.icon}</span>
                <div>
                  <div className="contact-label">{c.label}</div>
                  {c.href ? (
                    <a className="contact-value" href={c.href} target="_blank" rel="noreferrer">
                      {c.value}
                    </a>
                  ) : (
                    <div className="contact-value">{c.value}</div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        <div className="modal-actions">
          <button type="button" className="btn btn-primary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
