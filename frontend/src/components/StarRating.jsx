/**
 * Star rating display. When `onChange` is provided, renders clickable buttons
 * (for rating input); otherwise renders a read-only display.
 */
export default function StarRating({ value, onChange, size = '1rem' }) {
  const stars = [1, 2, 3, 4, 5]
  if (onChange) {
    return (
      <div className="stars">
        {stars.map((n) => (
          <button
            type="button"
            key={n}
            className={n <= value ? 'on' : ''}
            onClick={() => onChange(n)}
          >
            ★
          </button>
        ))}
      </div>
    )
  }
  return (
    <span className="stars" style={{ fontSize: size }}>
      {stars.map((n) => (
        <span key={n} style={{ color: n <= value ? '#f5a623' : 'var(--border)' }}>★</span>
      ))}
    </span>
  )
}