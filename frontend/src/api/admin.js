import client from './client'

export const getUsers = () =>
  client.get('/admin/users').then((r) => r.data)

export const getAuditLog = (params) =>
  client.get('/admin/audit', { params }).then((r) => r.data)
