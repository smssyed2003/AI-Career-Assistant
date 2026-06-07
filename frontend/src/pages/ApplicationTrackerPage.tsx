import { ChangeEvent, useEffect, useMemo, useState } from 'react'
import axios from 'axios'

interface CandidateRead {
  id: number
  full_name: string
  email: string
}

interface JobRead {
  id: number
  title: string
  company?: string
}

interface ApplicationPackageRead {
  id: number
  candidate_id: number
  job_id: number
  match_score?: number | null
  ats_score?: number | null
  interview_probability?: number | null
  status: string
  notes?: string | null
  applied_date?: string | null
  created_at: string
  cover_letter?: string | null
  hr_introduction?: string | null
  email_template?: string | null
  screening_answers?: Record<string, string> | null
}

const applicationStatuses = [
  'prepared',
  'submitted',
  'under_review',
  'interview_scheduled',
  'rejected',
  'accepted',
  'archived',
]

function ApplicationTrackerPage() {
  const [applications, setApplications] = useState<ApplicationPackageRead[]>([])
  const [candidates, setCandidates] = useState<CandidateRead[]>([])
  const [jobs, setJobs] = useState<JobRead[]>([])
  const [status, setStatus] = useState('Loading applications...')
  const [notesDraft, setNotesDraft] = useState<Record<number, string>>({})
  const [statusFilter, setStatusFilter] = useState('all')
  const [selectedApplication, setSelectedApplication] = useState<ApplicationPackageRead | null>(null)

  const candidateById = useMemo(() => new Map(candidates.map((candidate) => [candidate.id, candidate])), [candidates])
  const jobById = useMemo(() => new Map(jobs.map((job) => [job.id, job])), [jobs])
  const filteredApplications = useMemo(
    () => applications.filter((application) => statusFilter === 'all' || application.status === statusFilter),
    [applications, statusFilter]
  )

  const loadData = async () => {
    try {
      const [applicationResponse, candidateResponse, jobResponse] = await Promise.all([
        axios.get<ApplicationPackageRead[]>('/api/application-packages'),
        axios.get<CandidateRead[]>('/api/candidates'),
        axios.get<JobRead[]>('/api/jobs'),
      ])
      setApplications(applicationResponse.data)
      setCandidates(candidateResponse.data)
      setJobs(jobResponse.data)
      setNotesDraft(
        Object.fromEntries(applicationResponse.data.map((item) => [item.id, item.notes || '']))
      )
      setStatus(applicationResponse.data.length ? 'Tracker ready' : 'No application packages yet')
    } catch (error) {
      setStatus('Unable to load application tracker')
      console.error(error)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const updateApplication = async (applicationId: number, payload: Record<string, unknown>) => {
    try {
      setStatus('Saving tracker update...')
      await axios.patch(`/api/application-packages/${applicationId}`, payload)
      await loadData()
      setStatus('Tracker updated')
    } catch (error) {
      setStatus('Unable to update application')
      console.error(error)
    }
  }

  const handleStatusChange = (applicationId: number, event: ChangeEvent<HTMLSelectElement>) => {
    const nextStatus = event.target.value
    const payload: Record<string, unknown> = { status: nextStatus }
    if (nextStatus === 'submitted') {
      payload.applied_date = new Date().toISOString()
    }
    updateApplication(applicationId, payload)
  }

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <h2>Application Tracker</h2>
          <p>{status}</p>
        </div>
        <label className="compact-label">
          Status
          <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
            <option value="all">All</option>
            {applicationStatuses.map((item) => (
              <option key={item} value={item}>
                {item.replace(/_/g, ' ')}
              </option>
            ))}
          </select>
        </label>
      </div>

      {filteredApplications.length > 0 ? (
        <div className="tracker-list">
          {filteredApplications.map((application) => {
            const candidate = candidateById.get(application.candidate_id)
            const job = jobById.get(application.job_id)
            return (
              <div key={application.id} className="tracker-row">
                <div className="tracker-main">
                  <strong>{job?.title || `Job #${application.job_id}`}</strong>
                  <span>{job?.company || 'Company unknown'}</span>
                  <span>{candidate?.full_name || `Candidate #${application.candidate_id}`}</span>
                </div>
                <div className="tracker-scores">
                  <span>Match {application.match_score ?? 0}%</span>
                  <span>ATS {application.ats_score ?? 0}%</span>
                  <span>Interview {application.interview_probability ?? 0}%</span>
                </div>
                <div className="tracker-controls">
                  <select value={application.status} onChange={(event) => handleStatusChange(application.id, event)}>
                    {applicationStatuses.map((item) => (
                      <option key={item} value={item}>
                        {item.replace(/_/g, ' ')}
                      </option>
                    ))}
                  </select>
                  <textarea
                    value={notesDraft[application.id] || ''}
                    onChange={(event) => setNotesDraft((prev) => ({ ...prev, [application.id]: event.target.value }))}
                    rows={2}
                    placeholder="Private notes"
                  />
                  <button onClick={() => updateApplication(application.id, { notes: notesDraft[application.id] || '' })}>
                    Save Notes
                  </button>
                  <button onClick={() => setSelectedApplication(application)}>View Details</button>
                </div>
              </div>
            )
          })}
        </div>
      ) : (
        <p>Prepare an application package from Job Matching to start tracking, or change the filter.</p>
      )}

      {selectedApplication && (
        <div className="result-card">
          <div className="panel-heading">
            <h3>Application Detail</h3>
            <button onClick={() => setSelectedApplication(null)}>Close</button>
          </div>
          <h4>HR Introduction</h4>
          <p>{selectedApplication.hr_introduction || 'Not generated'}</p>
          <h4>Cover Letter</h4>
          <pre>{selectedApplication.cover_letter || 'Not generated'}</pre>
          <h4>Email Template</h4>
          <pre>{selectedApplication.email_template || 'Not generated'}</pre>
          {selectedApplication.screening_answers && (
            <>
              <h4>Screening Answers</h4>
              {Object.entries(selectedApplication.screening_answers).map(([question, answer]) => (
                <p key={question}>
                  <strong>{question}</strong>
                  <br />
                  {answer}
                </p>
              ))}
            </>
          )}
        </div>
      )}
    </section>
  )
}

export default ApplicationTrackerPage
