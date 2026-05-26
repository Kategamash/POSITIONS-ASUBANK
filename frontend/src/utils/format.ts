import dayjs from 'dayjs'

export const formatAmount = (val) => {
  if (val == null) return '—'
  return new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(val))
}

export const formatDate = (val) => {
  if (!val) return '—'
  return dayjs(val).format('DD.MM.YYYY')
}

export const formatDateTime = (val) => {
  if (!val) return '—'
  return dayjs(val).format('DD.MM.YYYY HH:mm:ss')
}

export const generateUUID = () =>
  'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0
    return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16)
  })
