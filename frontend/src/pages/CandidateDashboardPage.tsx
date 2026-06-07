import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'

interface CandidateDashboard {
  profile_count: number
  active_candidate_id?: number | null
  profile_completion: number
  resume_versions: number
  job_count: number
  application_count: number
  high_match_count: number
  interview_prep_count: number
  career_report_count: number
  application_status_counts: Record<string, number>
  next_actions: string[]
}

function CandidateDashboardPage() {
  const [dashboard, setDashboard] = useState<CandidateDashboard | null>(null)
  const [status, setStatus] = useState('Loading dashboard...')

  useEffect(() => {
    axios
      .get<CandidateDashboard>('/api/dashboard/candidate')
      .then((response) => {
        setDashboard(response.data)
        setStatus('Dashboard ready')
      })
      .catch((error) => {
        setStatus('Unable to load dashboard')
        console.error(error)
      })
  }, [])

  if (!dashboard) {
    return (
      <section className="panel">
        <h2>Candidate Dashboard</h2>
        <div className="status-card info">{status}</div>
      </section>
    )
  }

  const statusEntries = Object.entries(dashboard.application_status_counts)

  return (
    <div>
      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Candidate Dashboard</h2>
            <p>{status}</p>
          </div>
          <Link className="button-link" to="/match">
            Open Workspace
          </Link>
        </div>
        <div className="metric-grid">
          <div className="metric-card">
            <span>Profile</span>
            <strong>{dashboard.profile_completion}%</strong>
          </div>
          <div className="metric-card">
            <span>Resume Versions</span>
            <strong>{dashboard.resume_versions}</strong>
          </div>
          <div className="metric-card">
            <span>Saved Jobs</span>
            <strong>{dashboard.job_count}</strong>
          </div>
          <div className="metric-card">
            <span>Applications</span>
            <strong>{dashboard.application_count}</strong>
          </div>
          <div className="metric-card">
            <span>High Matches</span>
            <strong>{dashboard.high_match_count}</strong>
          </div>
          <div className="metric-card">
            <span>Interview Prep</span>
            <strong>{dashboard.interview_prep_count}</strong>
          </div>
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h3>Application Pipeline</h3>
          <Link className="button-link secondary" to="/applications">
            View Tracker
          </Link>
        </div>
        {statusEntries.length > 0 ? (
          <div className="pipeline-grid">
            {statusEntries.map(([name, count]) => (
              <div key={name} className="pipeline-item">
                <span>{name.replace(/_/g, ' ')}</span>
                <strong>{count}</strong>
              </div>
            ))}
          </div>
        ) : (
          <p>No application packages yet. Prepare one from the matching workspace after adding a job.</p>
        )}
      </section>

      <section className="panel">
        <h3>Next Actions</h3>
        {dashboard.next_actions.length > 0 ? (
          <ul className="action-list">
            {dashboard.next_actions.map((action) => (
              <li key={action}>{action}</li>
            ))}
          </ul>
        ) : (
          <p>Your core workflow is in good shape. Keep tracking applications and refreshing reports weekly.</p>
        )}
      </section>
    </div>
  )
}

export default CandidateDashboardPage
