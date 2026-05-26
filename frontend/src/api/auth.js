import client from './client'

export const login = (login, password) =>
  client.post('/auth/login', { login, password }).then((r) => r.data)

export const logout = () =>
  client.post('/auth/logout').then((r) => r.data)

export const getMe = () =>
  client.get('/auth/me').then((r) => r.data)
