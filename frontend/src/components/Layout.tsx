import { Outlet, Link } from 'react-router-dom'

export default function Layout() {
  return (
    <div className="layout">
      <header className="header">
        <nav className="navbar">
          <Link to="/" className="logo">
            RecommendHub
          </Link>
          <div className="nav-links">
            <Link to="/">Home</Link>
            <Link to="/recommendations">Recommendations</Link>
          </div>
        </nav>
      </header>

      <main className="main-content">
        <Outlet />
      </main>

      <footer className="footer">
        <p>&copy; 2026 E-commerce Recommendation System. All rights reserved.</p>
      </footer>
    </div>
  )
}
