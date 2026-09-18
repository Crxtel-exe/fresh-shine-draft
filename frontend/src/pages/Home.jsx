import { Link } from 'react-router-dom'
import { useGet } from '../hooks/useApi.js'

export default function Home() {
  const { data, loading } = useGet('/site')

  if (loading || !data) return <div className="spinner" />

  const { site, services, projects } = data

  return (
    <div className="page">
      <div className="container">
        {/* Hero */}
        <section className="hero">
          <div className="badge">{site.tagline || 'Clean Spaces.Brighter Places.'}</div>
          <h1>{site.company_name || 'Fresh & Shine Cleaning Services'}</h1>
          <p>{site.description || 'Your home, our passion. Professional cleaning services across Pampanga.'}</p>
          <Link to="/booking" className="btn btn-primary">Book a Cleaning</Link>
        </section>

        {/* Services */}
        <section className="mb-2">
          <h2 className="section-title">Our Services</h2>
          <p className="section-sub">Choose the cleaning service that fits your needs</p>
          <div className="grid grid-3">
            {services.map((s) => (
              <div className="media-card" key={s.id}>
                {s.image ? (
                  <img src={s.image} alt={s.name} />
                ) : (
                  <div style={{ height: 190, background: 'var(--bg-secondary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>No image</div>
                )}
                <div className="body">
                  <h3>{s.name}</h3>
                  <p>{s.description}</p>
                  {s.min_price != null || s.max_price != null ? (
                    <div className="price">
                      {s.min_price != null ? `₱${Number(s.min_price).toLocaleString()}` : ''}
                      {s.min_price != null && s.max_price != null ? ' – ' : ''}
                      {s.max_price != null ? `₱${Number(s.max_price).toLocaleString()}` : ''}
                    </div>
                  ) : null}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Past projects */}
        <section className="mt-3">
          <h2 className="section-title">Past Projects</h2>
          <p className="section-sub">A few of the spaces we've made sparkle</p>
          <div className="grid grid-3">
            {projects.map((p) => (
              <div className="media-card" key={p.id}>
                {p.image ? (
                  <img src={p.image} alt={p.title} />
                ) : (
                  <div style={{ height: 190, background: 'var(--bg-secondary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>No image</div>
                )}
                <div className="body">
                  <h3>{p.title}</h3>
                  <p>{p.description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}