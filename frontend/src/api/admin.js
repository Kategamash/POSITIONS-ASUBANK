import client from './client'

export const getUsers = () =>
  client.get('/admin/users').then((r) => r.data)

export const createUser = (data) =>
  client.post('/admin/users', data).then((r) => r.data)

export const updateUser = (id, data) =>
  client.patch(`/admin/users/${id}`, data).then((r) => r.data)

export const deactivateUser = (id) =>
  client.delete(`/admin/users/${id}`)

export const getAuditLog = (params) =>
  client.get('/admin/audit', { params }).then((r) => r.data)
