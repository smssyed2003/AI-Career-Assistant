import { useEffect, useState } from 'react'
import axios from 'axios'

interface AdminUser {
  id: number
  email: string
  full_name: string
  role: string
  is_active: boolean
  created_at: string
}

interface AdminAnalytics {
  total_users: number
  active_users: number
  admin_users: number
  candidate_users: number
  candidate_profiles: number
  jobs: number
  resumes: number
  application_packages: number
  application_status_counts: Record<string, number>
  system_health: {
    database?: string
    safe_application_mode?: string
    auto_apply_enabled?: boolean
    llm_queue?: {
      enabled: boolean
      requests_per_minute: number
      available_now: number
    }
  }
}

interface SystemSetting {
  id: number
  key: string
  category: string
  value: unknown
  description?: string
}

function AdminPage() {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [analytics, setAnalytics] = useState<AdminAnalytics | null>(null)
  const [settings, setSettings] = useState<SystemSetting[]>([])
  const [settingDrafts, setSettingDrafts] = useState<Record<string, string>>({})
  const [status, setStatus] = useState('Loading users...')

  const loadAdminData = async () => {
    try {
      const [userResponse, analyticsResponse, settingsResponse] = await Promise.all([
        axios.get<AdminUser[]>('/api/admin/users'),
        axios.get<AdminAnalytics>('/api/admin/analytics'),
        axios.get<{ settings: SystemSetting[] }>('/api/admin/settings'),
      ])
      setUsers(userResponse.data)
      setAnalytics(analyticsResponse.data)
      setSettings(settingsResponse.data.settings)
      setSettingDrafts(
        Object.fromEntries(settingsResponse.data.settings.map((setting) => [setting.key, stringifySetting(setting.value)]))
      )
      setStatus(userResponse.data.length ? 'Admin data loaded' : 'No users yet')
    } catch (error) {
      setStatus('Admin access required')
      console.error(error)
    }
  }

  const updateRole = async (userId: number, role: string) => {
    try {
      await axios.patch(`/api/admin/users/${userId}/role`, { role })
      await loadAdminData()
    } catch (error) {
      setStatus('Unable to update role')
      console.error(error)
    }
  }

  const updateStatus = async (userId: number, isActive: boolean) => {
    try {
      await axios.patch(`/api/admin/users/${userId}/status`, { is_active: isActive })
      await loadAdminData()
    } catch (error) {
      setStatus('Unable to update user status')
      console.error(error)
    }
  }

  const updateSetting = async (setting: SystemSetting) => {
    try {
      const draft = settingDrafts[setting.key] ?? ''
      await axios.patch(`/api/admin/settings/${setting.key}`, { value: parseSettingValue(draft) })
      await loadAdminData()
      setStatus(`Updated ${setting.key}`)
    } catch (error) {
      setStatus('Unable to update setting')
      console.error(error)
    }
  }

  useEffect(() => {
    loadAdminData()
  }, [])

  return (
    <div>
      <section className="panel">
        <h2>Admin</h2>
        <div className="status-card info">{status}</div>
        {analytics && (
          <div className="metric-grid">
            <div className="metric-card">
              <span>Total Users</span>
              <strong>{analytics.total_users}</strong>
            </div>
            <div className="metric-card">
              <span>Profiles</span>
              <strong>{analytics.candidate_profiles}</strong>
            </div>
            <div className="metric-card">
              <span>Jobs</span>
              <strong>{analytics.jobs}</strong>
            </div>
            <div className="metric-card">
              <span>Applications</span>
              <strong>{analytics.application_packages}</strong>
            </div>
            <div className="metric-card">
              <span>LLM RPM</span>
              <strong>{analytics.system_health.llm_queue?.requests_per_minute ?? 0}</strong>
            </div>
            <div className="metric-card">
              <span>Auto Apply</span>
              <strong>{analytics.system_health.auto_apply_enabled ? 'On' : 'Off'}</strong>
            </div>
          </div>
        )}
      </section>

      <section className="panel">
        <h3>User Management</h3>
        <div className="list-card">
          {users.map((user) => (
            <div key={user.id} className="admin-user-row">
              <div>
                <strong>{user.full_name}</strong>
                <p>{user.email}</p>
                <p>Status: {user.is_active ? 'Active' : 'Inactive'}</p>
              </div>
              <div className="admin-actions">
                <select value={user.role} onChange={(event) => updateRole(user.id, event.target.value)}>
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
                <button onClick={() => updateStatus(user.id, !user.is_active)}>
                  {user.is_active ? 'Deactivate' : 'Activate'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="panel">
        <h3>System Health</h3>
        {analytics ? (
          <div className="health-grid">
            <div>
              <span>Database</span>
              <strong>{analytics.system_health.database || 'unknown'}</strong>
            </div>
            <div>
              <span>Application Mode</span>
              <strong>{analytics.system_health.safe_application_mode || 'manual'}</strong>
            </div>
            <div>
              <span>LLM Available Now</span>
              <strong>{analytics.system_health.llm_queue?.available_now ?? 0}</strong>
            </div>
          </div>
        ) : (
          <p>Analytics not loaded.</p>
        )}
      </section>

      <section className="panel">
        <h3>Prompts and Integrations</h3>
        <div className="settings-list">
          {settings.map((setting) => (
            <div key={setting.key} className="setting-row">
              <div>
                <strong>{setting.key}</strong>
                <span>{setting.category}</span>
                {setting.description && <p>{setting.description}</p>}
              </div>
              <textarea
                value={settingDrafts[setting.key] || ''}
                onChange={(event) => setSettingDrafts((prev) => ({ ...prev, [setting.key]: event.target.value }))}
                rows={3}
              />
              <button onClick={() => updateSetting(setting)}>Save</button>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

const stringifySetting = (value: unknown) => {
  if (value === null || value === undefined) return ''
  if (typeof value === 'string') return value
  return JSON.stringify(value)
}

const parseSettingValue = (value: string) => {
  const trimmed = value.trim()
  if (!trimmed) return ''
  if (/^-?\d+(\.\d+)?$/.test(trimmed)) return Number(trimmed)
  if (trimmed === 'true') return true
  if (trimmed === 'false') return false
  try {
    return JSON.parse(trimmed)
  } catch {
    return value
  }
}

export default AdminPage
