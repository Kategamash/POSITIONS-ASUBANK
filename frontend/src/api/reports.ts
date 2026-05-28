import axios from 'axios'

const reportsClient = axios.create({
  baseURL: '/reports-api',
})

reportsClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export interface ReportTemplate {
  code: string
  name: string
  type: string
  available_formats: string[]
}

export async function getReportTemplates(): Promise<ReportTemplate[]> {
  const res = await reportsClient.get('/api/v1/integration/reports/templates')
  return res.data
}

export async function createReport(date: string, code = 'TURNOVER_DAY', format = 'html') {
  const res = await reportsClient.post('/api/v1/reports', {
    code,
    format,
    params: { date },
  })
  return res.data
}

export async function getReport(reportId: string) {
  const res = await reportsClient.get(`/api/v1/reports/${reportId}`)
  return res.data
}

export async function pollReport(
  reportId: string,
  { timeoutMs = 60000, intervalMs = 1500 }: { timeoutMs?: number; intervalMs?: number } = {}
) {
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    const rep = await getReport(reportId)
    if (rep.status === 'DONE') return rep
    if (rep.status === 'FAILED') throw new Error(rep.error_message || 'Отчёт завершился с ошибкой')
    await new Promise((r) => setTimeout(r, intervalMs))
  }
  throw new Error('Время ожидания отчёта истекло')
}

export async function downloadReport(reportId: string, format: string, reportCode: string) {
  const res = await reportsClient.get(`/api/v1/reports/${reportId}/file`, {
    responseType: 'blob',
  })
  const ext = format === 'csv' ? 'csv' : format === 'pdf' ? 'pdf' : 'html'
  const url = URL.createObjectURL(res.data)
  const a = document.createElement('a')
  a.href = url
  a.download = `${reportCode.toLowerCase()}-report.${ext}`
  a.click()
  URL.revokeObjectURL(url)
}
