import { useState } from 'react'
import { getCurrentUser, removeToken } from './api/client'
import type { User } from './api/auth'
import LoginForm from './components/LoginForm'
import RegisterForm from './components/RegisterForm'
import Header from './components/Header'
import ArticleFeed from './components/ArticleFeed'
import ArticleDetail from './components/ArticleDetail'

type AuthScreen = 'login' | 'register'

function App() {
  // Read token from localStorage on first render — no async needed
  const [user, setUser]           = useState<User | null>(() => getCurrentUser())
  const [authScreen, setAuthScreen] = useState<AuthScreen>('login')
  const [selectedId, setSelectedId] = useState<number | null>(null)

  function handleLogout() {
    removeToken()
    setUser(null)
  }

  if (!user) {
    return authScreen === 'register'
      ? <RegisterForm onRegister={setUser} onBack={() => setAuthScreen('login')} />
      : <LoginForm    onLogin={setUser}    onRegister={() => setAuthScreen('register')} />
  }

  return (
    <div className="container py-4" style={{ maxWidth: '800px' }}>
      <Header user={user} onLogout={handleLogout} />
      <ArticleFeed onSelectArticle={setSelectedId} />
      <ArticleDetail articleId={selectedId} onClose={() => setSelectedId(null)} />
    </div>
  )
}

export default App
