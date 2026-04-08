import { useState, FormEvent } from 'react'
import { login } from '../api/auth'
import type { User } from '../api/auth'

interface Props {
  onLogin: (user: User) => void
  onRegister: () => void
}

function LoginForm({ onLogin, onRegister }: Props) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError]       = useState<string | null>(null)
  const [loading, setLoading]   = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const user = await login(username, password)
      onLogin(user)
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center">
      <div className="card shadow" style={{ width: '360px' }}>
        <div className="card-body p-4">
          <h4 className="card-title mb-1">Commodity News Tracker</h4>
          <p className="text-muted small mb-4">Sign in to continue</p>

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
              <label className="form-label">Password</label>
              <input
                type="password"
                className="form-control"
                value={password}
                onChange={e => setPassword(e.target.value)}
                autoComplete="current-password"
                required
              />
            </div>

            {error && <div className="alert alert-danger py-2 small">{error}</div>}

            <button type="submit" className="btn btn-primary w-100" disabled={loading}>
              {loading ? <><span className="spinner-border spinner-border-sm me-2" />Signing in…</> : 'Sign in'}
            </button>
          </form>

          <hr />
          <button className="btn btn-outline-secondary w-100 btn-sm" onClick={onRegister}>
            Create an account
          </button>
        </div>
      </div>
    </div>
  )
}

export default LoginForm
