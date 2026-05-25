import client from './client'

export const getFxDeals = () =>
  client.get('/integration/fx/deals').then((r) => r.data)

export const getReportsPositions = (дата) =>
  client.get('/integration/reports/positions', { params: { дата } }).then((r) => r.data)

export const sendFxNotify = (body) =>
  client.post('/integration/fx/notify', body).then((r) => r.data)
