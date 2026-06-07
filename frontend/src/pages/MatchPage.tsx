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
  overall_label?: string
  interview_probability?: string
  skill_match_score?: number
  experience_match_score?: number
  project_match_score?: number
  keyword_match_score?: number
}

interface SkillGapAnalysis {
  candidate_id: number
  job_id: number
  candidate_skills: string[]
  required_skills: string[]
  missing_skills: string[]
  extra_candidate_skills?: string[]
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

interface ResumeRead {
  id: number
  candidate_id: number
  resume_type: string
  content: string
  optimized_for_job_id?: number | null
  ats_score?: number | null
}

interface ResumeGenerationResult {
  candidate_id: number
  generated_count: number
  resumes: ResumeRead[]
}

interface ApplicationPackageRead {
  id: number
  candidate_id: number
  job_id: number
  match_score?: number
  ats_score?: number
  interview_probability?: number
  optimized_resume_id?: number
  cover_letter?: string
  hr_introduction?: string
  email_template?: string
  screening_answers?: Record<string, string>
  status: string
}

interface InterviewPrepRead {
  id: number
  question_type: string
  question_text: string
  suggested_answer?: string
  keyword_highlights: string[]
  difficulty_level: string
}

interface CareerReportRead {
  id: number
  interview_rate?: number
  ats_average?: number
  new_skills: string[]
  trending_jobs: string[]
  resume_suggestions: string[]
  certification_suggestions: string[]
  salary_growth?: string
  career_roadmap: string[]
}

interface LlmQueueStatus {
  enabled: boolean
  requests_per_minute: number
  used_in_current_window: number
  available_now: number
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
  const [resumeVersions, setResumeVersions] = useState<ResumeRead[]>([])
  const [applicationPackage, setApplicationPackage] = useState<ApplicationPackageRead | null>(null)
  const [interviewQuestions, setInterviewQuestions] = useState<InterviewPrepRead[]>([])
  const [careerReport, setCareerReport] = useState<CareerReportRead | null>(null)
  const [llmQueueStatus, setLlmQueueStatus] = useState<LlmQueueStatus | null>(null)
  const [discoverySource, setDiscoverySource] = useState('company_careers')
  const [sourceUrl, setSourceUrl] = useState('')
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
    { key: 'discovery', label: 'Discovery', id: 'job-discovery' },
    { key: 'matches', label: 'Matches', id: 'matches' },
    { key: 'skill-gap', label: 'Skill Gap Analysis', id: 'skill-gap' },
    { key: 'readiness', label: 'Interview Readiness', id: 'interview-readiness' },
    { key: 'package', label: 'Application Package', id: 'application-package' },
    { key: 'interview-prep', label: 'Interview Prep', id: 'interview-prep' },
    { key: 'career-coach', label: 'Career Coach', id: 'career-coach' },
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
      setResumeVersions([])
      setApplicationPackage(null)
      setInterviewQuestions([])
      setCareerReport(null)
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
      setApplicationPackage(null)
      setInterviewQuestions([])
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
      setResumeVersions([])
      setApplicationPackage(null)
      setInterviewQuestions([])
      setCareerReport(null)
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
      setApplicationPackage(null)
      setInterviewQuestions([])
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

  const handleGenerateResumes = async () => {
    if (!candidate) {
      setStatusType('error')
      setStatus('Create or select a candidate before generating resume versions')
      return
    }

    try {
      setStatusType('info')
      setStatus('Generating resume versions...')
      const response = await axios.post<ResumeGenerationResult>(`/api/candidates/${candidate.id}/resumes/generate`)
      setResumeVersions(response.data.resumes)
      setStatusType('success')
      setStatus(`Generated ${response.data.generated_count} resume versions`)
    } catch (error) {
      setStatusType('error')
      setStatus('Failed to generate resume versions')
      console.error(error)
    }
  }

  const handlePrepareApplicationPackage = async () => {
    if (!candidate || !job) {
      setStatusType('error')
      setStatus('Candidate and job are required to prepare an application package')
      return
    }

    try {
      setStatusType('info')
      setStatus('Preparing application package...')
      const response = await axios.post<ApplicationPackageRead>(`/api/jobs/${job.id}/application-package/${candidate.id}`)
      setApplicationPackage(response.data)
      setStatusType('success')
      setStatus('Application package prepared for review')
    } catch (error) {
      setStatusType('error')
      setStatus('Failed to prepare application package')
      console.error(error)
    }
  }

  const handleDiscoverJob = async () => {
    if (!validateJobText(jobText)) {
      setStatusType('error')
      setStatus('Add a valid job description before discovery ingest.')
      return
    }

    try {
      setStatusType('info')
      setStatus('Saving discovered job with source tracking...')
      const response = await axios.post('/api/job-discovery/ingest', {
        source: discoverySource,
        source_url: sourceUrl || null,
        job_texts: [jobText],
      })
      const createdJobs = response.data.jobs || []
      if (createdJobs.length > 0) {
        setJob(createdJobs[0])
        setStatus(`Discovered job saved. Duplicates skipped: ${response.data.duplicate_count}`)
      } else {
        setStatus(`Duplicate job skipped. Existing job ids: ${response.data.duplicate_job_ids.join(', ')}`)
      }
      setStatusType('success')
      await loadSavedData()
    } catch (error) {
      setStatusType('error')
      setStatus('Failed to save discovered job')
      console.error(error)
    }
  }

  const handleGenerateInterviewPrep = async () => {
    if (!candidate || !job) {
      setStatusType('error')
      setStatus('Candidate and job are required to generate interview prep')
      return
    }

    try {
      setStatusType('info')
      setStatus('Generating interview prep...')
      const packageQuery = applicationPackage ? `?application_package_id=${applicationPackage.id}` : ''
      const response = await axios.post<InterviewPrepRead[]>(`/api/jobs/${job.id}/interview-prep/${candidate.id}${packageQuery}`)
      setInterviewQuestions(response.data)
      setStatusType('success')
      setStatus('Interview prep generated')
    } catch (error) {
      setStatusType('error')
      setStatus('Failed to generate interview prep')
      console.error(error)
    }
  }

  const handleGenerateCareerReport = async () => {
    if (!candidate) {
      setStatusType('error')
      setStatus('Select a candidate before generating a career report')
      return
    }

    try {
      setStatusType('info')
      setStatus('Generating career coach report...')
      const response = await axios.post<CareerReportRead>(`/api/candidates/${candidate.id}/career-reports/generate`)
      setCareerReport(response.data)
      setStatusType('success')
      setStatus('Career coach report generated')
    } catch (error) {
      setStatusType('error')
      setStatus('Failed to generate career report')
      console.error(error)
    }
  }

  const loadLlmQueueStatus = async () => {
    try {
      const response = await axios.get<LlmQueueStatus>('/api/llm/queue/status')
      setLlmQueueStatus(response.data)
    } catch (error) {
      console.error('Failed to load LLM queue status', error)
    }
  }

  useEffect(() => {
    loadSavedData()
    loadLlmQueueStatus()
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
        <button disabled={!candidate} onClick={handleGenerateResumes}>
          Generate Resume Versions
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
        {resumeVersions.length > 0 && (
          <div className="list-card">
            {resumeVersions.map((resume) => (
              <div key={resume.id} className="resume-row">
                <div>
                  <strong>{resume.resume_type.replace('_', ' ')}</strong>
                  <div>ATS score: {resume.ats_score ?? 'Pending'}</div>
                </div>
                <span>Version #{resume.id}</span>
              </div>
            ))}
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

      <section id="job-discovery" className="panel">
        <h3>Discovery</h3>
        <div className="field-grid">
          <label>
            Source
            <select value={discoverySource} onChange={(event) => setDiscoverySource(event.target.value)}>
              <option value="company_careers">Company Careers</option>
              <option value="startup_careers">Startup Careers</option>
              <option value="ai_company_careers">AI Company Careers</option>
              <option value="remote_ok">RemoteOK</option>
              <option value="wellfound">Wellfound</option>
              <option value="government_jobs">Government Jobs</option>
              <option value="internship_portals">Internship Portals</option>
              <option value="manual">Manual</option>
            </select>
          </label>
          <label>
            Source URL
            <input value={sourceUrl} onChange={(event) => setSourceUrl(event.target.value)} />
          </label>
        </div>
        <button disabled={!isJobTextValid} onClick={handleDiscoverJob}>
          Save Discovered Job
        </button>
        {llmQueueStatus && (
          <div className="result-card">
            <h4>LLM Queue</h4>
            <p>
              Limit: <strong>{llmQueueStatus.requests_per_minute}/minute</strong>
            </p>
            <p>
              Available now: <strong>{llmQueueStatus.available_now}</strong>
            </p>
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
                  <div>{match.overall_label || 'Match scored'} - Interview: {match.interview_probability || 'Pending'}</div>
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
              Job skills: <strong>{skillGap.required_skills.join(', ')}</strong>
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

      <section id="application-package" className="panel">
        <div className="panel-heading">
          <h3>Application Package</h3>
          <button disabled={!candidate || !job} onClick={handlePrepareApplicationPackage}>
            Prepare Package
          </button>
        </div>
        {applicationPackage ? (
          <div className="result-card">
            <div className="score-grid">
              <div>
                <span>Match</span>
                <strong>{applicationPackage.match_score ?? 0}%</strong>
              </div>
              <div>
                <span>ATS</span>
                <strong>{applicationPackage.ats_score ?? 0}%</strong>
              </div>
              <div>
                <span>Interview</span>
                <strong>{applicationPackage.interview_probability ?? 0}%</strong>
              </div>
            </div>
            <p>
              Optimized resume version: <strong>#{applicationPackage.optimized_resume_id}</strong>
            </p>
            <h4>HR Introduction</h4>
            <p>{applicationPackage.hr_introduction}</p>
            <h4>Cover Letter</h4>
            <pre>{applicationPackage.cover_letter}</pre>
            <h4>Email Template</h4>
            <pre>{applicationPackage.email_template}</pre>
            {applicationPackage.screening_answers && (
              <>
                <h4>Screening Answers</h4>
                <div className="screening-list">
                  {Object.entries(applicationPackage.screening_answers).map(([question, answer]) => (
                    <p key={question}>
                      <strong>{question}</strong>
                      <br />
                      {answer}
                    </p>
                  ))}
                </div>
              </>
            )}
          </div>
        ) : (
          <p>Prepare a review-ready package after selecting a candidate and job.</p>
        )}
      </section>

      <section id="interview-prep" className="panel">
        <div className="panel-heading">
          <h3>Interview Prep</h3>
          <button disabled={!candidate || !job} onClick={handleGenerateInterviewPrep}>
            Generate Questions
          </button>
        </div>
        {interviewQuestions.length > 0 ? (
          <div className="list-card">
            {interviewQuestions.map((question) => (
              <div key={question.id} className="prep-row">
                <div>
                  <strong>{question.question_type.replace('_', ' ')}</strong>
                  <span>{question.difficulty_level}</span>
                </div>
                <p>{question.question_text}</p>
                {question.suggested_answer && <p>{question.suggested_answer}</p>}
              </div>
            ))}
          </div>
        ) : (
          <p>Generate likely interview questions after selecting a candidate and job.</p>
        )}
      </section>

      <section id="career-coach" className="panel">
        <div className="panel-heading">
          <h3>Career Coach</h3>
          <button disabled={!candidate} onClick={handleGenerateCareerReport}>
            Generate Report
          </button>
        </div>
        {careerReport ? (
          <div className="result-card">
            <div className="score-grid">
              <div>
                <span>Interview Rate</span>
                <strong>{careerReport.interview_rate ?? 0}%</strong>
              </div>
              <div>
                <span>ATS Average</span>
                <strong>{careerReport.ats_average ?? 0}%</strong>
              </div>
            </div>
            <h4>New Skills</h4>
            <p>{careerReport.new_skills.join(', ') || 'No urgent gaps found'}</p>
            <h4>Trending Jobs</h4>
            <p>{careerReport.trending_jobs.join(', ') || 'Add more jobs to see trends'}</p>
            <h4>Resume Suggestions</h4>
            <ul>
              {careerReport.resume_suggestions.map((suggestion) => (
                <li key={suggestion}>{suggestion}</li>
              ))}
            </ul>
            <h4>Career Roadmap</h4>
            <ul>
              {careerReport.career_roadmap.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ul>
            {careerReport.salary_growth && <p>{careerReport.salary_growth}</p>}
          </div>
        ) : (
          <p>Generate a simple weekly-style career report for the selected candidate.</p>
        )}
      </section>
    </div>
  )
}

export default MatchPage
