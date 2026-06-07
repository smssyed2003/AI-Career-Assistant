import { ChangeEvent, useEffect, useState } from 'react'
import axios from 'axios'

interface CandidateRead {
  id: number
  full_name: string
  email: string
}

interface ResumeRead {
  id: number
  candidate_id: number
  resume_type: string
  content: string
  optimized_for_job_id?: number | null
  ats_score?: number | null
  created_at: string
}

interface ResumeUploadRead {
  id: number
  candidate_id?: number | null
  file_name: string
  file_type: string
  source?: string | null
  extracted_text: string
  created_at: string
}

function ResumeLibraryPage() {
  const [candidates, setCandidates] = useState<CandidateRead[]>([])
  const [selectedCandidateId, setSelectedCandidateId] = useState<number | null>(null)
  const [resumes, setResumes] = useState<ResumeRead[]>([])
  const [uploads, setUploads] = useState<ResumeUploadRead[]>([])
  const [selectedContent, setSelectedContent] = useState('')
  const [status, setStatus] = useState('Loading resume library...')

  const loadCandidates = async () => {
    const response = await axios.get<CandidateRead[]>('/api/candidates')
    setCandidates(response.data)
    if (response.data.length) {
      setSelectedCandidateId(response.data[0].id)
      await loadLibrary(response.data[0].id)
    } else {
      await loadUploads()
      setStatus('Create a candidate profile before generating resume versions')
    }
  }

  const loadUploads = async (candidateId?: number) => {
    const query = candidateId ? `?candidate_id=${candidateId}` : ''
    const response = await axios.get<ResumeUploadRead[]>(`/api/resume-uploads${query}`)
    setUploads(response.data)
  }

  const loadLibrary = async (candidateId: number) => {
    try {
      setStatus('Loading resume library...')
      const [resumeResponse] = await Promise.all([
        axios.get<ResumeRead[]>(`/api/candidates/${candidateId}/resumes`),
        loadUploads(candidateId),
      ])
      setResumes(resumeResponse.data)
      setSelectedContent('')
      setStatus('Resume library ready')
    } catch (error) {
      setStatus('Unable to load resume library')
      console.error(error)
    }
  }

  useEffect(() => {
    loadCandidates().catch((error) => {
      setStatus('Unable to load resume library')
      console.error(error)
    })
  }, [])

  const handleCandidateChange = async (event: ChangeEvent<HTMLSelectElement>) => {
    const candidateId = Number(event.target.value)
    setSelectedCandidateId(candidateId)
    await loadLibrary(candidateId)
  }

  const handleUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    try {
      setStatus('Uploading and parsing resume...')
      const formData = new FormData()
      formData.append('file', file)
      if (selectedCandidateId) {
        formData.append('candidate_id', String(selectedCandidateId))
      }
      await axios.post('/api/ingest/resume', formData)
      await loadUploads(selectedCandidateId || undefined)
      setStatus('Resume upload stored')
    } catch (error) {
      setStatus('Unable to upload resume')
      console.error(error)
    } finally {
      event.target.value = ''
    }
  }

  return (
    <div>
      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Resume Library</h2>
            <p>{status}</p>
          </div>
        </div>
        {candidates.length > 0 && (
          <label className="full-width">
            Candidate
            <select value={selectedCandidateId ?? ''} onChange={handleCandidateChange}>
              {candidates.map((candidate) => (
                <option key={candidate.id} value={candidate.id}>
                  {candidate.full_name} - {candidate.email}
                </option>
              ))}
            </select>
          </label>
        )}
        <label className="full-width">
          Upload resume file
          <input type="file" accept=".pdf,.docx,.txt" onChange={handleUpload} />
        </label>
      </section>

      <section className="panel">
        <h3>Generated Versions</h3>
        {resumes.length > 0 ? (
          <div className="library-list">
            {resumes.map((resume) => (
              <button key={resume.id} className="library-row" onClick={() => setSelectedContent(resume.content)}>
                <span>{resume.resume_type.replace(/_/g, ' ')}</span>
                <strong>ATS {resume.ats_score ?? 'Pending'}</strong>
              </button>
            ))}
          </div>
        ) : (
          <p>Generate resume versions from Job Matching to fill this library.</p>
        )}
      </section>

      <section className="panel">
        <h3>Upload History</h3>
        {uploads.length > 0 ? (
          <div className="library-list">
            {uploads.map((upload) => (
              <button key={upload.id} className="library-row" onClick={() => setSelectedContent(upload.extracted_text)}>
                <span>{upload.file_name}</span>
                <strong>{new Date(upload.created_at).toLocaleDateString()}</strong>
              </button>
            ))}
          </div>
        ) : (
          <p>No resume uploads stored yet.</p>
        )}
      </section>

      {selectedContent && (
        <section className="panel">
          <h3>Preview</h3>
          <pre>{selectedContent}</pre>
        </section>
      )}
    </div>
  )
}

export default ResumeLibraryPage
