import { FormEvent, useEffect, useState } from 'react'
import { BrowserRouter, Link, NavLink, Route, Routes, useLocation, useSearchParams } from 'react-router-dom'
import axios from 'axios'
import CandidateDashboardPage from './pages/CandidateDashboardPage'
import MatchPage from './pages/MatchPage'
import AdminPage from './pages/AdminPage'
import ApplicationTrackerPage from './pages/ApplicationTrackerPage'
import ProfilePage from './pages/ProfilePage'
import ResumeLibraryPage from './pages/ResumeLibraryPage'

interface AuthUser {
  id: number
  email: string
  full_name: string
  role: string
}

interface TokenResponse {
  access_token: string
  user: AuthUser
}

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
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login')
  const [authForm, setAuthForm] = useState({ full_name: '', email: '', password: '' })
  const [authUser, setAuthUser] = useState<AuthUser | null>(null)
  const [authStatus, setAuthStatus] = useState('')

  useEffect(() => {
    const token = localStorage.getItem('career_agent_token')
    const user = localStorage.getItem('career_agent_user')
    if (token) {
      axios.defaults.headers.common.Authorization = `Bearer ${token}`
    }
    if (user) {
      setAuthUser(JSON.parse(user))
    }
  }, [])

  const handleAuthSubmit = async (event: FormEvent) => {
    event.preventDefault()
    try {
      setAuthStatus('Authenticating...')
      const endpoint = authMode === 'signup' ? '/api/auth/signup' : '/api/auth/login'
      const payload =
        authMode === 'signup'
          ? authForm
          : { email: authForm.email, password: authForm.password }
      const response = await axios.post<TokenResponse>(endpoint, payload)
      localStorage.setItem('career_agent_token', response.data.access_token)
      localStorage.setItem('career_agent_user', JSON.stringify(response.data.user))
      axios.defaults.headers.common.Authorization = `Bearer ${response.data.access_token}`
      setAuthUser(response.data.user)
      setAuthStatus('')
    } catch (error) {
      setAuthStatus('Login or signup failed. Check your details and try again.')
      console.error(error)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('career_agent_token')
    localStorage.removeItem('career_agent_user')
    delete axios.defaults.headers.common.Authorization
    setAuthUser(null)
  }

  return (
    <BrowserRouter>
      <div className="app-shell">
        <div className="page-header">
          <header>
            <h1>AI Career Agent</h1>
          </header>

          <nav className="main-nav">
            <NavLink to="/" className={({ isActive }) => (isActive ? 'nav-link active-link' : 'nav-link')}>
              Dashboard
            </NavLink>
            <NavLink to="/match" className={({ isActive }) => (isActive ? 'nav-link active-link' : 'nav-link')}>
              Job Matching
            </NavLink>
            <NavLink to="/profile" className={({ isActive }) => (isActive ? 'nav-link active-link' : 'nav-link')}>
              Profile
            </NavLink>
            <NavLink to="/resumes" className={({ isActive }) => (isActive ? 'nav-link active-link' : 'nav-link')}>
              Resumes
            </NavLink>
            <NavLink to="/applications" className={({ isActive }) => (isActive ? 'nav-link active-link' : 'nav-link')}>
              Applications
            </NavLink>
            {authUser?.role === 'admin' && (
              <NavLink to="/admin" className={({ isActive }) => (isActive ? 'nav-link active-link' : 'nav-link')}>
                Admin
              </NavLink>
            )}
          </nav>
        </div>

        <div className="auth-bar">
          {authUser ? (
            <>
              <span>{authUser.full_name} ({authUser.email})</span>
              <button onClick={handleLogout}>Logout</button>
            </>
          ) : (
            <span>Login required for candidate, job, resume, and report data.</span>
          )}
        </div>

        <Breadcrumbs />

        <main>
          {!authUser ? (
            <section className="panel auth-panel">
              <h2>{authMode === 'signup' ? 'Create Account' : 'Login'}</h2>
              <form onSubmit={handleAuthSubmit}>
                {authMode === 'signup' && (
                  <label>
                    Name
                    <input
                      value={authForm.full_name}
                      onChange={(event) => setAuthForm((prev) => ({ ...prev, full_name: event.target.value }))}
                    />
                  </label>
                )}
                <label>
                  Email
                  <input
                    value={authForm.email}
                    onChange={(event) => setAuthForm((prev) => ({ ...prev, email: event.target.value }))}
                  />
                </label>
                <label>
                  Password
                  <input
                    type="password"
                    value={authForm.password}
                    onChange={(event) => setAuthForm((prev) => ({ ...prev, password: event.target.value }))}
                  />
                </label>
                <button type="submit">{authMode === 'signup' ? 'Sign Up' : 'Login'}</button>
              </form>
              <button onClick={() => setAuthMode(authMode === 'signup' ? 'login' : 'signup')}>
                {authMode === 'signup' ? 'Use Login' : 'Create Account'}
              </button>
              {authStatus && <p>{authStatus}</p>}
            </section>
          ) : (
            <Routes>
              <Route path="/" element={<CandidateDashboardPage />} />
              <Route path="/match" element={<MatchPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/resumes" element={<ResumeLibraryPage />} />
              <Route path="/applications" element={<ApplicationTrackerPage />} />
              {authUser.role === 'admin' && <Route path="/admin" element={<AdminPage />} />}
            </Routes>
          )}
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
