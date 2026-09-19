import { useEffect, useState } from 'react'
import api from '../api'

/**
 * Pampanga municipality + barangay picker (restricted to Pampanga only).
 * Props: value {municipality, barangay}, onChange(next), optional `required`.
 */
export default function PampangaPicker({ value, onChange, required = false }) {
  const [pampanga, setPampanga] = useState({})

  useEffect(() => {
    api.get('/pampanga').then((res) => setPampanga(res.data)).catch(() => {})
  }, [])

  const setMunicipality = (m) => onChange({ municipality: m, barangay: '' })
  const setBarangay = (b) => onChange({ ...value, barangay: b })

  return (
    <div className="form-row">
      <div className="form-group">
        <label>Municipality (Pampanga)</label>
        <select
          value={value.municipality || ''}
          onChange={(e) => setMunicipality(e.target.value)}
          required={required}
        >
          <option value="">Select municipality…</option>
          {Object.keys(pampanga).map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
      </div>
      <div className="form-group">
        <label>Barangay</label>
        <select
          value={value.barangay || ''}
          onChange={(e) => setBarangay(e.target.value)}
          required={required}
          disabled={!value.municipality}
        >
          <option value="">Select barangay…</option>
          {(pampanga[value.municipality] || []).map((b) => (
            <option key={b} value={b}>{b}</option>
          ))}
        </select>
      </div>
    </div>
  )
}