import client from './client'

export const getPayments = (params = {}) =>
  client.get('/payments/', { params }).then((r) => r.data)

export const getPayment = (id) =>
  client.get(`/payments/${id}`).then((r) => r.data)

export const sendIncomingPayment = (data) =>
  client.post('/payments/incoming', data).then((r) => r.data)
