import { useState } from 'react'
import { NavLink, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { useTheme } from '../context/ThemeContext.jsx'

export default function Navbar() {
  const { user, logout, isAdmin } = useAuth()
  const { dark, toggle } = useTheme()
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()

  const handleLogout = async () => {
    setOpen(false)
    await logout()
    // Both admins and regular users return to the login page.
    navigate('/login')
  }

  const links = isAdmin
    ? [
        { to: '/admin', label: 'Home' },
        { to: '/admin/bookings', label: 'Bookings' },
        { to: '/admin/reviews', label: 'Reviews' },
      ]
    : [
        { to: '/', label: 'Home' },
        { to: '/booking', label: 'Book' },
        { to: '/my-bookings', label: 'My Bookings' },
        { to: '/reviews', label: 'Reviews' },
        { to: '/about', label: 'About Us' },
      ]

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to={isAdmin ? '/admin' : '/'} className="brand" onClick={() => setOpen(false)}>
          <img src="/sparkle.png" alt="logo" />
          <span>Fresh & Shine Cleaning Services</span>
        </Link>

        <div className={`nav-links ${open ? 'open' : ''}`}>
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) => (isActive ? 'active' : '')}
              onClick={() => setOpen(false)}
            >
              {l.label}
            </NavLink>
          ))}
          <div className="nav-links-mobile-actions">
            {user ? (
              <button className="btn btn-ghost btn-sm btn-block" onClick={handleLogout}>
                Logout
              </button>
            ) : (
              <>
                <Link to="/login" className="btn btn-outline btn-sm btn-block" onClick={() => setOpen(false)}>Login</Link>
                <Link to="/signup" className="btn btn-primary btn-sm btn-block" onClick={() => setOpen(false)}>Sign Up</Link>
              </>
            )}
          </div>
        </div>

        <div className="nav-actions">
          <button className="icon-btn" onClick={toggle} title="Toggle theme" aria-label="Toggle theme">
            {dark ? 'Light' : 'Dark'}
          </button>
          {user ? (
            <>
              <button className="btn btn-outline btn-sm" onClick={handleLogout}>
                Logout
              </button>
              <Link to="/profile" title="Profile" onClick={() => setOpen(false)}>
                {user.profile_pic ? (
                  <img className="avatar" src={user.profile_pic} alt="profile" />
                ) : (
                  <span className="avatar">
                    {user.first_name?.[0]}{user.last_name?.[0]}
                  </span>
                )}
              </Link>
            </>
          ) : (
            <div className="nav-auth-desktop">
              <Link to="/login" className="btn btn-outline btn-sm">Login</Link>
              <Link to="/signup" className="btn btn-primary btn-sm">Sign Up</Link>
            </div>
          )}
          <button
            className={`hamburger ${open ? 'open' : ''}`}
            onClick={() => setOpen((o) => !o)}
            aria-label="Toggle menu"
            aria-expanded={open}
          >
            <span />
            <span />
            <span />
          </button>
        </div>
      </div>
    </nav>
  )
}