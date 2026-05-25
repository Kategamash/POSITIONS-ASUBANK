import client from './client'

export const getCurrencies = () =>
  client.get('/currencies/').then((r) => r.data)

export const createCurrency = (data) =>
  client.post('/currencies/', data).then((r) => r.data)

export const deleteCurrency = (код) =>
  client.delete(`/currencies/${код}`).then((r) => r.data)
