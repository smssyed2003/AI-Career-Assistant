import { ChangeEvent, useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import axios from 'axios'

interface CandidateRead {
  id: number
  full_name: string
  email: string
  phone?: string
  summary?: string
  skills: string[]
}

interface JobRead {
  id: number
  title: string
  company?: string
  location?: string
  description: string
  structured_data: {
    skills: string[]
    requirements: string[]
    responsibilities: string[]
    employment_type?: string
    experience_level?: string | null
  }
}

interface JobMatch {
  job_id: number
  title: string
  company?: string
  score: number
  matched_skills?: string[]
}

interface SkillGapAnalysis {
  candidate_id: number
  job_id: number
  candidate_skills: string[]
  job_skills: string[]
  missing_skills: string[]
  extra_skills?: string[]
  score: number
}

interface ReadinessAnalysis {
  job_id: number
  candidate_id: number
  readiness_score: number
  summary: string
  top_strengths: string[]
  improvement_areas: string[]
  recommended_learning: string[]
  matched_skills: string[]
  missing_skills: string[]
}

function MatchPage() {
  const [candidateForm, setCandidateForm] = useState({
    full_name: '',
    email: '',
    phone: '',
    summary: '',
    skills: '',
  })
  const [candidate, setCandidate] = useState<CandidateRead | null>(null)
  const [jobText, setJobText] = useState('')
  const [job, setJob] = useState<JobRead | null>(null)
  const [matches, setMatches] = useState<JobMatch[]>([])
  const [skillGap, setSkillGap] = useState<SkillGapAnalysis | null>(null)
  const [readiness, setReadiness] = useState<ReadinessAnalysis | null>(null)
  const [status, setStatus] = useState('Ready')
  const [statusType, setStatusType] = useState<'info' | 'success' | 'error'>('info')
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [savedCandidates, setSavedCandidates] = useState<CandidateRead[]>([])
  const [savedJobs, setSavedJobs] = useState<JobRead[]>([])
  const [selectedCandidateId, setSelectedCandidateId] = useState<number | null>(null)
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null)
  const [searchParams, setSearchParams] = useSearchParams()

  const sections = [
    { key: 'candidate', label: 'Candidate Profile', id: 'candidate-profile' },
    { key: 'job', label: 'Job Description', id: 'job-description' },
    { key: 'matches', label: 'Matches', id: 'matches' },
    { key: 'skill-gap', label: 'Skill Gap Analysis', id: 'skill-gap' },
    { key: 'readiness', label: 'Interview Readiness', id: 'interview-readiness' },
  ]

  const activeSection = searchParams.get('section') || ''

  useEffect(() => {
    const section = searchParams.get('section')
    if (section) {
      const sectionMeta = sections.find((item) => item.key === section)
      const element = sectionMeta ? document.getElementById(sectionMeta.id) : null
      element?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [searchParams])

  const handleSectionClick = (section: string) => {
    setSearchParams({ section })
  }

  const validateEmail = (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)

  const normalizeSkills = (value: string) =>
    value
      .split(',')
      .map((skill) => skill.trim())
      .filter(Boolean)

  const validateField = (name: string, value: string) => {
    let error = ''

    if (name === 'full_name') {
      if (!value.trim()) {
        error = 'Name is required.'
      } else if (value.trim().length < 3) {
        error = 'Name must be at least 3 characters.'
      }
    }

    if (name === 'email') {
      if (!value.trim()) {
        error = 'Email is required.'
      } else if (!validateEmail(value)) {
        error = 'Enter a valid email address.'
      }
    }

    if (name === 'skills') {
      const skills = normalizeSkills(value)
      if (skills.length === 0) {
        error = 'Provide at least one skill.'
      }
    }

    if (name === 'jobText') {
      if (!value.trim()) {
        error = 'Job description is required.'
      } else if (value.trim().length < 20) {
        error = 'Job text should be at least 20 characters.'
      }
    }

    setFieldErrors((prev) => ({ ...prev, [name]: error }))
    return error === ''
  }

  const validateCandidateForm = () => {
    const validations = [
      validateField('full_name', candidateForm.full_name),
      validateField('email', candidateForm.email),
      validateField('skills', candidateForm.skills),
    ]
    return validations.every(Boolean)
  }

  const validateJobText = (value: string) => validateField('jobText', value)

  const getInputClass = (fieldName: string) => {
    const hasError = Boolean(fieldErrors[fieldName])
    if (hasError) return 'input-error'
    if (fieldName === 'full_name' && candidateForm.full_name.trim().length > 0) return 'input-valid'
    if (fieldName === 'email' && validateEmail(candidateForm.email)) return 'input-valid'
    if (fieldName === 'skills' && normalizeSkills(candidateForm.skills).length > 0) return 'input-valid'
    if (fieldName === 'jobText' && jobText.trim().length >= 20) return 'input-valid'
    return ''
  }

  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = event.target
    setCandidateForm((prev) => ({ ...prev, [name]: value }))
    if (['full_name', 'email', 'skills'].includes(name)) {
      validateField(name, value)
    }
  }

  const handleJobTextChange = (event: ChangeEvent<HTMLTextAreaElement>) => {
    const value = event.target.value
    setJobText(value)
    validateField('jobText', value)
  }

  const loadSavedData = async () => {
    try {
      const [candidateResponse, jobResponse] = await Promise.all([
        axios.get<CandidateRead[]>('/api/candidates'),
        axios.get<JobRead[]>('/api/jobs'),
      ])
      setSavedCandidates(candidateResponse.data)
      setSavedJobs(jobResponse.data)
    } catch (error) {
      console.error('Failed to load saved candidates or jobs', error)
    }
  }

  const handleSelectCandidate = (event: ChangeEvent<HTMLSelectElement>) => {
    const selectedId = Number(event.target.value) || null
    setSelectedCandidateId(selectedId)
    const saved = savedCandidates.find((item) => item.id === selectedId)
    if (saved) {
      setCandidate(saved)
      setCandidateForm({
        full_name: saved.full_name,
        email: saved.email,
        phone: saved.phone || '',
        summary: saved.summary || '',
        skills: saved.skills.join(', '),
      })
      setFieldErrors((prev) => ({ ...prev, full_name: '', email: '', skills: '' }))
      setStatusType('success')
      setStatus(`Loaded saved candidate: ${saved.full_name}`)
    } else {
      setCandidate(null)
    }
  }

  const handleSelectJob = (event: ChangeEvent<HTMLSelectElement>) => {
    const selectedId = Number(event.target.value) || null
    setSelectedJobId(selectedId)
    const saved = savedJobs.find((item) => item.id === selectedId)
    if (saved) {
      setJob(saved)
      setJobText(saved.description)
      setFieldErrors((prev) => ({ ...prev, jobText: '' }))
      setStatusType('success')
      setStatus(`Loaded saved job: ${saved.title}`)
    } else {
      setJob(null)
      setJobText('')
    }
  }

  const handleCreateCandidate = async () => {
    if (!validateCandidateForm()) {
      setStatusType('error')
      setStatus('Please fix candidate form errors before submitting.')
      return
    }

    try {
      setStatusType('info')
      setStatus('Creating candidate...')
      const payload = {
        full_name: candidateForm.full_name,
        email: candidateForm.email,
        phone: candidateForm.phone,
        summary: candidateForm.summary,
        skills: normalizeSkills(candidateForm.skills),
      }
      const response = await axios.post('/api/candidates', payload)
      setCandidate(response.data)
      setStatusType('success')
      setStatus('Candidate created successfully')
      setMatches([])
      setSkillGap(null)
      setReadiness(null)
      await loadSavedData()
    } catch (error) {
      setStatusType('error')
      setStatus('Failed to create candidate')
      console.error(error)
    }
  }

  const handleIngestJob = async () => {
    if (!validateJobText(jobText)) {
      setStatusType('error')
      setStatus('Please fix the job description before submitting.')
      return
    }

    try {
      setStatusType('info')
      setStatus('Ingesting job description...')
      const formData = new FormData()
      formData.append('text', jobText)
      const response = await axios.post('/api/jobs/ingest', formData)
      setJob(response.data)
      setStatusType('success')
      setStatus('Job ingested successfully')
      setSkillGap(null)
      setReadiness(null)
      await loadSavedData()
      if (candidate) {
        fetchMatches(candidate.id)
      }
    } catch (error) {
      setStatusType('error')
      setStatus('Failed to ingest job description')
      console.error(error)
    }
  }

  const fetchMatches = async (candidateId: number) => {
    try {
      setStatusType('info')
      setStatus('Fetching matches...')
      const response = await axios.get<JobMatch[]>(`/api/jobs/match/${candidateId}`)
      setMatches(response.data)
      setStatusType('success')
      setStatus('Matches loaded')
    } catch (error) {
      setStatusType('error')
      setStatus('Unable to fetch matches')
      console.error(error)
    }
  }

  const handleAnalyzeGap = async () => {
    if (!candidate || !job) {
      setStatusType('error')
      setStatus('Candidate and job are required to analyze skill gaps')
      return
    }

    try {
      setStatusType('info')
      setStatus('Analyzing skill gap...')
      const response = await axios.get<SkillGapAnalysis>(`/api/jobs/${job.id}/skill-gap/${candidate.id}`)
      setSkillGap(response.data)
      setStatusType('success')
      setStatus('Skill gap analysis complete')
    } catch (error) {
      setStatusType('error')
      setStatus('Failed to analyze skill gap')
      console.error(error)
    }
  }

  const handleAnalyzeReadiness = async () => {
    if (!candidate || !job) {
      setStatusType('error')
      setStatus('Candidate and job are required to evaluate readiness')
      return
    }

    try {
      setStatusType('info')
      setStatus('Analyzing interview readiness...')
      const response = await axios.get<ReadinessAnalysis>(`/api/jobs/${job.id}/readiness/${candidate.id}`)
      setReadiness(response.data)
      setStatusType('success')
      setStatus('Interview readiness evaluated')
    } catch (error) {
      setStatusType('error')
      setStatus('Failed to evaluate readiness')
      console.error(error)
    }
  }

  useEffect(() => {
    loadSavedData()
  }, [])

  const isCandidateFormValid =
    candidateForm.full_name.trim().length >= 3 &&
    validateEmail(candidateForm.email) &&
    normalizeSkills(candidateForm.skills).length > 0 &&
    !fieldErrors.full_name &&
    !fieldErrors.email &&
    !fieldErrors.skills

  const isJobTextValid = jobText.trim().length >= 20 && !fieldErrors.jobText

  return (
    <div>
      <section className="panel">
        <h2>Job Matching Workspace</h2>
        <div className={`status-card ${statusType}`} role="status">
          <strong>Status:</strong> {status}
        </div>
        <div className="feature-nav">
          {sections.map((sectionItem) => (
            <Link
              key={sectionItem.key}
              to={`?section=${sectionItem.key}`}
              className={
                activeSection === sectionItem.key
                  ? 'feature-link active-feature-link'
                  : 'feature-link'
              }
              onClick={() => handleSectionClick(sectionItem.key)}
            >
              {sectionItem.label}
            </Link>
          ))}
        </div>
      </section>

      <section id="candidate-profile" className="panel">
        <h3>Candidate Profile</h3>
        {savedCandidates.length > 0 && (
          <label className="full-width">
            Saved candidate
            <select value={selectedCandidateId ?? ''} onChange={handleSelectCandidate}>
              <option value="">Select a saved candidate</option>
              {savedCandidates.map((saved) => (
                <option key={saved.id} value={saved.id}>
                  {saved.full_name} • {saved.email}
                </option>
              ))}
            </select>
          </label>
        )}
        <div className="field-grid">
          <label>
            Name
            <input
              className={getInputClass('full_name')}
              name="full_name"
              value={candidateForm.full_name}
              onChange={handleChange}
            />
            {fieldErrors.full_name && <span className="field-error-text">{fieldErrors.full_name}</span>}
          </label>
          <label>
            Email
            <input
              className={getInputClass('email')}
              name="email"
              value={candidateForm.email}
              onChange={handleChange}
            />
            {fieldErrors.email && <span className="field-error-text">{fieldErrors.email}</span>}
          </label>
          <label>
            Phone
            <input name="phone" value={candidateForm.phone} onChange={handleChange} />
          </label>
        </div>
        <label className="full-width">
          Summary
          <textarea
            name="summary"
            value={candidateForm.summary}
            onChange={handleChange}
            rows={3}
          />
        </label>
        <label className="full-width">
          Skills (comma-separated)
          <input
            className={getInputClass('skills')}
            name="skills"
            value={candidateForm.skills}
            onChange={handleChange}
          />
          {fieldErrors.skills && <span className="field-error-text">{fieldErrors.skills}</span>}
        </label>
        <button disabled={!isCandidateFormValid} onClick={handleCreateCandidate}>
          Create Candidate
        </button>
        {candidate && (
          <div className="result-card">
            <h3>Candidate saved</h3>
            <p>
              {candidate.full_name} • {candidate.email}
            </p>
            <p>Skills: {candidate.skills.join(', ')}</p>
          </div>
        )}
      </section>

      <section id="job-description" className="panel">
        <h3>Job Description</h3>
        {savedJobs.length > 0 && (
          <label className="full-width">
            Saved job
            <select value={selectedJobId ?? ''} onChange={handleSelectJob}>
              <option value="">Select a saved job</option>
              {savedJobs.map((saved) => (
                <option key={saved.id} value={saved.id}>
                  {saved.title} • {saved.company || 'Unknown'}
                </option>
              ))}
            </select>
          </label>
        )}
        <label className="full-width">
          Job text
          <textarea
            className={getInputClass('jobText')}
            value={jobText}
            onChange={handleJobTextChange}
            rows={8}
          />
          {fieldErrors.jobText && <span className="field-error-text">{fieldErrors.jobText}</span>}
        </label>
        <button disabled={!isJobTextValid} onClick={handleIngestJob}>
          Ingest Job
        </button>
        {job && (
          <div className="result-card">
            <h3>Job saved</h3>
            <p>
              {job.title} at {job.company || 'Unknown company'}
            </p>
            <p>{job.location || 'Location unknown'}</p>
            <p>Skills: {job.structured_data.skills.join(', ') || 'None extracted'}</p>
          </div>
        )}
      </section>

      <section id="matches" className="panel">
        <div className="panel-heading">
          <h3>Matches</h3>
          <button disabled={!candidate} onClick={() => candidate && fetchMatches(candidate.id)}>
            Refresh matches
          </button>
        </div>
        {candidate ? <p>Matches for candidate <strong>{candidate.full_name}</strong>:</p> : <p>Create a candidate profile first.</p>}
        {matches.length > 0 ? (
          <div className="list-card">
            {matches.map((match) => (
              <div key={match.job_id} className="match-row">
                <div>
                  <strong>{match.title}</strong>
                  <div>{match.company || 'Company unknown'}</div>
                </div>
                <div>{(match.score * 100).toFixed(0)}%</div>
              </div>
            ))}
          </div>
        ) : (
          <p>No matches yet.</p>
        )}
      </section>

      <section id="skill-gap" className="panel">
        <h3>Skill Gap Analysis</h3>
        <button disabled={!candidate || !job} onClick={handleAnalyzeGap}>
          Analyze Skill Gap
        </button>
        {skillGap ? (
          <div className="gap-card">
            <p>
              Candidate skills: <strong>{skillGap.candidate_skills.join(', ')}</strong>
            </p>
            <p>
              Job skills: <strong>{skillGap.job_skills.join(', ')}</strong>
            </p>
            <p>
              Missing skills: <strong>{skillGap.missing_skills.join(', ') || 'None'}</strong>
            </p>
            <p>Match score: {(skillGap.score * 100).toFixed(0)}%</p>
          </div>
        ) : (
          <p>Generate a candidate and a job before running gap analysis.</p>
        )}
      </section>

      <section id="interview-readiness" className="panel">
        <h3>Interview Readiness</h3>
        <button disabled={!candidate || !job} onClick={handleAnalyzeReadiness}>
          Evaluate Readiness
        </button>
        {readiness ? (
          <div className="result-card">
            <p>
              Readiness score: <strong>{(readiness.readiness_score * 100).toFixed(0)}%</strong>
            </p>
            <p>{readiness.summary}</p>
            <p>
              Top strengths: <strong>{readiness.top_strengths.join(', ') || 'None'}</strong>
            </p>
            <p>
              Improvement areas: <strong>{readiness.improvement_areas.join(', ') || 'None'}</strong>
            </p>
            <p>
              Recommended learning: <strong>{readiness.recommended_learning.join(', ') || 'None'}</strong>
            </p>
            <p>
              Matched skills: <strong>{readiness.matched_skills.join(', ') || 'None'}</strong>
            </p>
            <p>
              Missing skills: <strong>{readiness.missing_skills.join(', ') || 'None'}</strong>
            </p>
          </div>
        ) : (
          <p>Evaluate readiness after ingesting a job and creating a candidate.</p>
        )}
      </section>
    </div>
  )
}

export default MatchPage
