import client from './client'

export const getReportsPositions = (date) =>
  client.get('/integration/reports/positions', { params: { date } }).then((r) => r.data)
