import { ChangeEvent, useEffect, useState } from 'react'
import axios from 'axios'

interface CandidateRead {
  id: number
  full_name: string
  email: string
  phone?: string
  summary?: string
  skills: string[]
  certifications?: string[]
  links?: string[]
}

function ProfilePage() {
  const [candidates, setCandidates] = useState<CandidateRead[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    phone: '',
    summary: '',
    skills: '',
    certifications: '',
    links: '',
  })
  const [status, setStatus] = useState('Loading profiles...')

  const loadCandidates = async () => {
    try {
      const response = await axios.get<CandidateRead[]>('/api/candidates')
      setCandidates(response.data)
      setStatus(response.data.length ? 'Profiles loaded' : 'Create a profile in Job Matching first')
      if (response.data.length && !selectedId) {
        loadCandidate(response.data[0])
      }
    } catch (error) {
      setStatus('Unable to load profiles')
      console.error(error)
    }
  }

  const loadCandidate = (candidate: CandidateRead) => {
    setSelectedId(candidate.id)
    setForm({
      full_name: candidate.full_name,
      email: candidate.email,
      phone: candidate.phone || '',
      summary: candidate.summary || '',
      skills: (candidate.skills || []).join(', '),
      certifications: (candidate.certifications || []).join(', '),
      links: (candidate.links || []).join(', '),
    })
  }

  useEffect(() => {
    loadCandidates()
  }, [])

  const handleSelect = (event: ChangeEvent<HTMLSelectElement>) => {
    const candidate = candidates.find((item) => item.id === Number(event.target.value))
    if (candidate) {
      loadCandidate(candidate)
    }
  }

  const handleSave = async () => {
    if (!selectedId) return
    try {
      setStatus('Saving profile...')
      await axios.patch(`/api/candidates/${selectedId}`, {
        full_name: form.full_name,
        email: form.email,
        phone: form.phone || null,
        summary: form.summary || null,
        skills: splitList(form.skills),
        certifications: splitList(form.certifications),
        links: splitList(form.links),
      })
      await loadCandidates()
      setStatus('Profile updated')
    } catch (error) {
      setStatus('Unable to save profile')
      console.error(error)
    }
  }

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <h2>Candidate Profile</h2>
          <p>{status}</p>
        </div>
      </div>

      {candidates.length > 0 ? (
        <>
          <label className="full-width">
            Saved profile
            <select value={selectedId ?? ''} onChange={handleSelect}>
              {candidates.map((candidate) => (
                <option key={candidate.id} value={candidate.id}>
                  {candidate.full_name} - {candidate.email}
                </option>
              ))}
            </select>
          </label>

          <div className="field-grid">
            <label>
              Name
              <input value={form.full_name} onChange={(event) => setForm((prev) => ({ ...prev, full_name: event.target.value }))} />
            </label>
            <label>
              Email
              <input value={form.email} onChange={(event) => setForm((prev) => ({ ...prev, email: event.target.value }))} />
            </label>
            <label>
              Phone
              <input value={form.phone} onChange={(event) => setForm((prev) => ({ ...prev, phone: event.target.value }))} />
            </label>
          </div>

          <label className="full-width">
            Summary
            <textarea value={form.summary} onChange={(event) => setForm((prev) => ({ ...prev, summary: event.target.value }))} />
          </label>
          <label className="full-width">
            Skills
            <input value={form.skills} onChange={(event) => setForm((prev) => ({ ...prev, skills: event.target.value }))} />
          </label>
          <label className="full-width">
            Certifications
            <input value={form.certifications} onChange={(event) => setForm((prev) => ({ ...prev, certifications: event.target.value }))} />
          </label>
          <label className="full-width">
            Links
            <input value={form.links} onChange={(event) => setForm((prev) => ({ ...prev, links: event.target.value }))} />
          </label>
          <button onClick={handleSave}>Save Profile</button>
        </>
      ) : (
        <p>Create a candidate profile in Job Matching, then return here to edit it.</p>
      )}
    </section>
  )
}

const splitList = (value: string) =>
  value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)

export default ProfilePage
