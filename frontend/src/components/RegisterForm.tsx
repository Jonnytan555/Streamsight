import { useState, FormEvent } from 'react'
import { register } from '../api/auth'
import type { User } from '../api/auth'

interface Props {
  onRegister: (user: User) => void
  onBack: () => void
}

function RegisterForm({ onRegister, onBack }: Props) {
  const [username, setUsername] = useState('')
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [error, setError]       = useState<string | null>(null)
  const [loading, setLoading]   = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const user = await register(username, email, password)
      onRegister(user)
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center">
      <div className="card shadow" style={{ width: '360px' }}>
        <div className="card-body p-4">
          <h4 className="card-title mb-1">Create account</h4>
          <p className="text-muted small mb-4">Commodity News Tracker</p>

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label">Username</label>
              <input
                type="text"
                className="form-control"
                value={username}
                onChange={e => setUsername(e.target.value)}
                autoComplete="username"
                required
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Email</label>
              <input
                type="email"
                className="form-control"
                value={email}
                onChange={e => setEmail(e.target.value)}
                autoComplete="email"
                required
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Password</label>
              <input
                type="password"
                className="form-control"
                value={password}
                onChange={e => setPassword(e.target.value)}
                autoComplete="new-password"
                required
              />
            </div>

            {error && <div className="alert alert-danger py-2 small">{error}</div>}

            <button type="submit" className="btn btn-primary w-100" disabled={loading}>
              {loading ? <><span className="spinner-border spinner-border-sm me-2" />Creating…</> : 'Create account'}
            </button>
          </form>

          <hr />
          <button className="btn btn-outline-secondary w-100 btn-sm" onClick={onBack}>
            Back to sign in
          </button>
        </div>
      </div>
    </div>
  )
}

export default RegisterForm
