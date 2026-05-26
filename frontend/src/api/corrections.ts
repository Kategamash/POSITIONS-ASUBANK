import client from './client'

export const getCorrections = (params = {}) =>
  client.get('/corrections/', { params }).then((r) => r.data)

export const createCorrection = (data) =>
  client.post('/corrections/', data).then((r) => r.data)

export const getCorrection = (id) =>
  client.get(`/corrections/${id}`).then((r) => r.data)
