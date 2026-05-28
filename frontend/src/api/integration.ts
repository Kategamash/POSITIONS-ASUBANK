import client from './client'

export const getFxDeals = () =>
  client.get('/integration/fx/deals').then((r) => r.data)

export const getReportsPositions = (date) =>
  client.get('/integration/reports/positions', { params: { date } }).then((r) => r.data)
