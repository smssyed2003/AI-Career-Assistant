import { useEffect, useState } from 'react'
import axios from 'axios'

interface Summary {
  status: string
}

function HomePage() {
  const [health, setHealth] = useState<Summary | null>(null)
  const [message, setMessage] = useState('Loading backend status...')

  useEffect(() => {
    axios
      .get('/api/health')
      .then((response) => {
        setHealth(response.data)
        setMessage('Backend reachable')
      })
      .catch(() => {
        setMessage('Unable to reach backend')
      })
  }, [])

  return (
    <div>
      <section className="panel">
        <h2>Welcome to AI Career Agent</h2>
        <p>
          Use the navigation menu to move between the home dashboard and the job matching workspace.
          This app supports candidate profile creation, job description ingestion, matching, and skill gap analysis.
        </p>
      </section>

      <section className="panel">
        <h2>System Status</h2>
        <p>{message}</p>
        {health && (
          <div className="health-card">
            <pre>{JSON.stringify(health, null, 2)}</pre>
          </div>
        )}
      </section>

      <section className="panel">
        <h2>Current Capabilities</h2>
        <ul>
          <li>Candidate creation and profile storage</li>
          <li>Job description ingestion from raw text</li>
          <li>Candidate-to-job matching</li>
          <li>Skill gap analysis between candidate and job</li>
        </ul>
      </section>
    </div>
  )
}

export default HomePage
