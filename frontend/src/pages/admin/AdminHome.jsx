import { useGet } from '../../hooks/useApi.js'

export default function AdminHome() {
  const { data, loading } = useGet('/site')

  if (loading || !data) return <div className="spinner" />

  return (
    <div className="page">
      <div className="container">
        <h1 className="section-title">Admin Dashboard</h1>
        <p className="section-sub">Manage customer bookings and reviews. Website content is managed directly in the source code.</p>

        <div className="grid grid-2">
          <div className="card">
            <h3>Website Content</h3>
            <p className="muted">
              Services, prices, descriptions, homepage project images, company information, and other public content
              are intentionally not editable from the admin panel.
            </p>
            <p className="muted mt-1">
              Edit these values manually in <code>backend/store.py</code>. Put homepage images in the frontend
              <code>public</code> folder and set their paths in the code.
            </p>
          </div>

          <div className="card">
            <h3>Logo</h3>
            <p className="muted">
              The logo is a code-managed file. Replace <code>frontend/public/sparkle.png</code> with your own logo
              or change the logo path in <code>frontend/src/components/Navbar.jsx</code>.
            </p>
          </div>

          <div className="card">
            <h3>Bookings</h3>
            <p className="muted">
              View customer bookings and update booking status or payment information from the Bookings section.
            </p>
          </div>

          <div className="card">
            <h3>Reviews</h3>
            <p className="muted">
              View customer reviews and reply to them from the Reviews section. Each completed booking can be reviewed
              only once by the customer who made it.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
