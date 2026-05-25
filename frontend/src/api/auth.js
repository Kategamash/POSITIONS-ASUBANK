import client from './client'

export const login = (логин, пароль) =>
  client.post('/auth/login', { логин, пароль }).then((r) => r.data)

export const logout = () =>
  client.post('/auth/logout').then((r) => r.data)

export const getMe = () =>
  client.get('/auth/me').then((r) => r.data)
