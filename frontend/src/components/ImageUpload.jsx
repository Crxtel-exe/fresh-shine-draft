import { useRef, useState } from 'react'
import api from '../api'

const ACCEPTED = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml', 'image/bmp']
const MAX_SIZE = 5 * 1024 * 1024 // 5 MB

/**
 * Reusable image upload field.
 *
 * Lets the user pick a file from their device, uploads it to POST /api/upload,
 * and calls `onChange(url)` with the returned URL. Shows a preview of the
 * current value and a friendly error if the file is invalid.
 */
export default function ImageUpload({ value, onChange, label = 'Image', placeholder = 'No image selected' }) {
  const inputRef = useRef(null)
  const [uploading, setUploading] = useState(false)
  const [err, setErr] = useState('')

  const handleFile = async (e) => {
    const file = e.target.files?.[0]
    e.target.value = '' // allow re-selecting the same file
    if (!file) return
    setErr('')

    if (!ACCEPTED.includes(file.type)) {
      setErr('Only image files are allowed (JPG, PNG, GIF, WEBP, SVG, BMP).')
      return
    }
    if (file.size > MAX_SIZE) {
      setErr('Image is too large. Maximum size is 5 MB.')
      return
    }

    setUploading(true)
    try {
      const fd = new FormData()
      fd.append('file', file)
      const res = await api.post('/upload', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      onChange(res.data.url)
    } catch (err) {
      setErr(err.response?.data?.error || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="image-upload">
      <div className="image-upload-preview">
        {value ? (
          <img src={value} alt="preview" />
        ) : (
          <span className="muted">{placeholder}</span>
        )}
      </div>
      <div className="flex wrap" style={{ gap: 8, alignItems: 'center' }}>
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          style={{ display: 'none' }}
          onChange={handleFile}
        />
        <button type="button" className="btn btn-outline btn-sm" onClick={() => inputRef.current?.click()} disabled={uploading}>
          {uploading ? 'Uploading…' : label}
        </button>
        {value && (
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => onChange('')}>
            Remove
          </button>
        )}
      </div>
      {err && <div className="alert alert-error" style={{ marginTop: 8 }}>{err}</div>}
    </div>
  )
}