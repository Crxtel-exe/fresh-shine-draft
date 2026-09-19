import { useGet } from '../hooks/useApi.js'

export default function About() {
  const { data: site, loading } = useGet('/site')

  if (loading || !site) return <div className="spinner" />

  return (
    <div className="page">
      <div className="container">
        <section className="hero">
          <div className="badge"> <h1>About Us</h1> </div>
          <h1>{site.company_name}</h1>
          <p>{site.tagline}</p>
        </section>

        <div className="grid grid-2" style={{ alignItems: 'start' }}>
          <div className="card">
            <h2 className="section-title">Who We Are</h2>
            <p className="mt-2">
              <strong>Location:</strong>{" "}
              <a
                href="https://maps.app.goo.gl/mKeR3jdNx9L8qX6U9"
                target="_blank"
                rel="noopener noreferrer"
              >
                Lot 21 Block 15, Richtofen Cor. Pear St. Hensonville Homes, Barangay Malabanias, Angeles City
              </a>
            </p>
          </div>

          <div className="card">
            <h2 className="section-title">Contact Us</h2>
            <div className="form-group">
              <label>Email</label>
              <p><a href={`mailto:hello@freshshine.ph`}>hello@freshshine.ph</a></p>
            </div>
            <div className="form-group">
              <label>Phone</label>
              <p><a href={`tel:0960 662 7021`}> 0960 662 7021 </a></p>
            </div>
            <div className="form-group">
              <label>Facebook</label>
              <p><a href={`https://www.facebook.com/people/Fresh-Shine-Cleaning-Services/61590070245356/`} target="_blank" rel="noreferrer"> Fresh Shine Cleaning Services </a> </p>
            </div>
            <div className="form-group">
              <label>TikTok</label>
              <p><a href={`https://www.tiktok.com/@fresh.shine.clean6?_r=1&_t=ZS-99qCsMqwyay`} target="_blank" rel="noreferrer"> Fresh Shine Cleaning Service </a></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}