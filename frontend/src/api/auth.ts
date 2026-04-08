// Re-export from client so the rest of the app has a stable import path
export type { TokenPayload as User } from './client'
export { login, register, fetchMe as getMe, removeToken as logout } from './client'
