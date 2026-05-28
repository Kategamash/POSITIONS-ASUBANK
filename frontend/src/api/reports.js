import axios from 'axios'

const reportsClient = axios.create({
  baseURL: '/reports-api',
})

reportsClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export async function createReport(date) {
  const res = await reportsClient.post('/api/v1/reports', {
    code: 'TURNOVER_DAY',
    format: 'html',
    params: { date },
  })
  return res.data
}

export async function getReport(reportId) {
  const res = await reportsClient.get(`/api/v1/reports/${reportId}`)
  return res.data
}

export async function pollReport(reportId, { timeoutMs = 60000, intervalMs = 1500 } = {}) {
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    const rep = await getReport(reportId)
    if (rep.status === 'DONE') return rep
    if (rep.status === 'FAILED') throw new Error(rep.error_message || 'Отчёт завершился с ошибкой')
    await new Promise((r) => setTimeout(r, intervalMs))
  }
  throw new Error('Время ожидания отчёта истекло')
}

export async function downloadReport(reportId) {
  const res = await reportsClient.get(`/api/v1/reports/${reportId}/file`, {
    responseType: 'blob',
  })
  const url = URL.createObjectURL(res.data)
  const a = document.createElement('a')
  a.href = url
  a.download = `positions-report.html`
  a.click()
  URL.revokeObjectURL(url)
}
