import client from './client'

export const getPositions = (params) =>
  client.get('/positions/', { params }).then((r) => r.data)

export const getPosition = (accountId, params) =>
  client.get(`/positions/${accountId}`, { params }).then((r) => r.data)

export const getOpeningBalances = (params) =>
  client.get('/positions/opening-balances/', { params }).then((r) => r.data)

export const createOpeningBalance = (data) =>
  client.post('/positions/opening-balances/', data).then((r) => r.data)
