import axios from 'axios'
import { jwtDecode } from 'jwt-decode'

const api = axios.create({
  baseURL: '',
  timeout: 30000,
})

api.interceptors.request.use(config => {
  const token = getToken()
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  r => r,
  err => {
    if (err?.response?.status === 401) {
      removeToken()
    }
    return Promise.reject(err)
  }
)

export interface TokenPayload {
  sub: string
  name?: string
  username?: string
  exp?: number
}

export function getToken(): string | null {
  return localStorage.getItem('access_token')
}

export function setToken(token: string) {
  localStorage.setItem('access_token', token)
}

export function removeToken() {
  localStorage.removeItem('access_token')
}

export function getCurrentUser(): TokenPayload | null {
  const token = getToken()
  if (!token) return null
  try {
    const payload = jwtDecode<TokenPayload>(token)
    if (payload.exp && payload.exp * 1000 < Date.now()) {
      removeToken()
      return null
    }
    return payload
  } catch {
    return null
  }
}

export async function login(username: string, password: string): Promise<TokenPayload> {
  const res = await api.post('/api/auth/login', { username, password })
  setToken(res.data.access_token)
  return getCurrentUser()!
}

export async function register(username: string, email: string, password: string): Promise<TokenPayload> {
  const res = await api.post('/api/auth/register', { username, email, password })
  setToken(res.data.access_token)
  return getCurrentUser()!
}

export async function fetchMe(): Promise<TokenPayload | null> {
  return getCurrentUser()
}

export default api
