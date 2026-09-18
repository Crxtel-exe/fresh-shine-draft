/** Colored status badge. Maps a status value to a CSS badge class. */
const BADGE_MAP = {
  pending: 'badge-pending',
  confirmed: 'badge-confirmed',
  completed: 'badge-completed',
  cancelled: 'badge-cancelled',
  unpaid: 'badge-unpaid',
  partial: 'badge-partial',
  paid: 'badge-paid',
  new: 'badge-pending',
  read: 'badge-confirmed',
  replied: 'badge-completed',
}

export default function Badge({ value }) {
  return <span className={`badge ${BADGE_MAP[value] || 'badge-pending'}`}>{value}</span>
}