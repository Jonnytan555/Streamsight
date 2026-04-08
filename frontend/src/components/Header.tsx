import type { User } from '../api/auth'
import { logout } from '../api/auth'

interface Props {
  user: User | null
  onLogout: () => void
}

function Header({ user, onLogout }: Props) {
  async function handleLogout() {
    await logout()
    onLogout()
  }

  return (
    <header className="mb-4">
      <div className="d-flex justify-content-between align-items-center">
        <div>
          <h1 className="h3 mb-0">Commodity News Tracker</h1>
          <p className="text-muted small mb-0">Commodity market intelligence</p>
        </div>
        {user && (
          <div className="text-end">
            <span className="text-muted small me-3">{user.name ?? user.username ?? user.sub}</span>
            <button className="btn btn-sm btn-outline-secondary" onClick={handleLogout}>
              Logout
            </button>
          </div>
        )}
      </div>
      <hr />
    </header>
  )
}

export default Header
