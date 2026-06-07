import { BrowserRouter, Link, NavLink, Route, Routes, useLocation, useSearchParams } from 'react-router-dom'
import HomePage from './pages/HomePage'
import MatchPage from './pages/MatchPage'

function Breadcrumbs() {
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const segments = location.pathname.split('/').filter(Boolean)
  const crumbs = ['Home', ...segments.map((segment) => segment.replace(/-/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase()))]
  const section = searchParams.get('section')

  if (section) {
    crumbs.push(section.replace(/-/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase()))
  }

  return (
    <div className="breadcrumbs">
      {crumbs.map((crumb, index) => {
        const path = index === 0 ? '/' : `/${segments.slice(0, index).join('/')}`
        const isLast = index === crumbs.length - 1
        const isActiveCrumb = path === location.pathname

        return (
          <span key={crumb} className="breadcrumb-item">
            {isLast ? (
              <span className="breadcrumb-current">{crumb}</span>
            ) : (
              <Link to={path} className={isActiveCrumb ? 'breadcrumb-link breadcrumb-active' : 'breadcrumb-link'}>
                {crumb}
              </Link>
            )}
            {index < crumbs.length - 1 && <span className="breadcrumb-separator">/</span>}
          </span>
        )
      })}
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <div className="page-header">
          <header>
            <h1>AI Career Agent</h1>
          </header>

          <nav className="main-nav">
            <NavLink to="/" className={({ isActive }) => (isActive ? 'nav-link active-link' : 'nav-link')}>
              Home
            </NavLink>
            <NavLink to="/match" className={({ isActive }) => (isActive ? 'nav-link active-link' : 'nav-link')}>
              Job Matching
            </NavLink>
          </nav>
        </div>

        <Breadcrumbs />

        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/match" element={<MatchPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
