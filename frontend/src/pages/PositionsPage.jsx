import React, { useState, useEffect } from 'react'
import {
  Table, DatePicker, Select, Space, Typography, Tag, Row, Col, Card,
  Statistic, Tooltip, Button, message,
} from 'antd'
import {
  ExclamationCircleOutlined, ArrowUpOutlined, CheckCircleOutlined,
  DownloadOutlined,
} from '@ant-design/icons'
import dayjs from 'dayjs'
import { getPositions } from '../api/positions'
import { getCurrencies } from '../api/currencies'
import { createReport, pollReport, downloadReport } from '../api/reports'
import { formatAmount } from '../utils/format'

const { Title } = Typography

export default function PositionsPage() {
  const [data, setData] = useState([])
  const [currencies, setCurrencies] = useState([])
  const [loading, setLoading] = useState(false)
  const [date, setDate] = useState(dayjs())
  const [currencyFilter, setCurrencyFilter] = useState(null)
  const [reportLoading, setReportLoading] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const params = { date: date.format('YYYY-MM-DD') }
      if (currencyFilter) params.currency_code = currencyFilter
      setData(await getPositions(params))
    } catch {
      setData([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    getCurrencies().then(setCurrencies).catch(() => {})
  }, [])

  useEffect(() => {
    load()
  }, [date, currencyFilter])

  const exceededCount = data.filter((d) => d.limit_exceeded).length

  const handleDownloadReport = async () => {
    setReportLoading(true)
    const key = 'report-msg'
    try {
      message.loading({ content: 'Запрос отчёта в сервисе ОТЧЁТЫ...', key, duration: 0 })
      const rep = await createReport(date.format('YYYY-MM-DD'))
      message.loading({ content: 'Генерация отчёта...', key, duration: 0 })
      await pollReport(rep.id)
      message.loading({ content: 'Скачивание...', key, duration: 0 })
      await downloadReport(rep.id)
      message.success({ content: 'Отчёт скачан', key, duration: 3 })
    } catch (err) {
      message.error({ content: err.message || 'Ошибка при получении отчёта', key, duration: 5 })
    } finally {
      setReportLoading(false)
    }
  }

  const columns = [
    {
      title: 'Номер счёта',
      dataIndex: 'account_number',
      key: 'account_number',
      fixed: 'left',
      width: 180,
      render: (v) => <span style={{ fontFamily: 'monospace', fontWeight: 500 }}>{v}</span>,
    },
    {
      title: 'Наименование',
      dataIndex: 'account_name',
      key: 'account_name',
      ellipsis: true,
    },
    {
      title: 'Валюта',
      dataIndex: 'currency_code',
      key: 'currency_code',
      width: 80,
      align: 'center',
      render: (v) => <Tag color="blue">{v}</Tag>,
    },
    {
      title: 'Вх. остаток',
      dataIndex: 'opening_balance',
      key: 'opening_balance',
      align: 'right',
      render: (v) => formatAmount(v),
    },
    {
      title: 'Корректировки',
      dataIndex: 'corrections_amount',
      key: 'corrections_amount',
      align: 'right',
      render: (v) => {
        const n = Number(v)
        if (n > 0) return <span style={{ color: '#3f8600' }}>+{formatAmount(v)}</span>
        if (n < 0) return <span style={{ color: '#cf1322' }}>{formatAmount(v)}</span>
        return <span style={{ color: '#8c8c8c' }}>{formatAmount(v)}</span>
      },
    },
    {
      title: 'Оборот IN',
      dataIndex: 'turnover_in',
      key: 'turnover_in',
      align: 'right',
      render: (v) => <span style={{ color: '#3f8600' }}>{formatAmount(v)}</span>,
    },
    {
      title: 'Оборот OUT',
      dataIndex: 'turnover_out',
      key: 'turnover_out',
      align: 'right',
      render: (v) => <span style={{ color: '#cf1322' }}>{formatAmount(v)}</span>,
    },
    {
      title: 'Тек. позиция',
      dataIndex: 'current_position',
      key: 'current_position',
      align: 'right',
      fixed: 'right',
      width: 160,
      render: (v, row) => (
        <Space>
          <span
            style={{
              fontWeight: 700,
              fontSize: 14,
              color: row.limit_exceeded ? '#cf1322' : '#1677ff',
            }}
          >
            {formatAmount(v)}
          </span>
          {row.limit_exceeded && (
            <Tooltip title="Превышение лимита">
              <ExclamationCircleOutlined style={{ color: '#cf1322' }} />
            </Tooltip>
          )}
        </Space>
      ),
    },
    {
      title: 'Лимит',
      dataIndex: 'limit',
      key: 'limit',
      align: 'right',
      width: 130,
      render: (v) =>
        v != null ? (
          formatAmount(v)
        ) : (
          <Tag style={{ margin: 0 }}>Без лимита</Tag>
        ),
    },
  ]

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Row justify="space-between" align="middle">
        <Col>
          <Title level={4} style={{ margin: 0 }}>
            Мониторинг позиций
          </Title>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Card size="small">
            <Statistic title="Счетов отслеживается" value={data.length} />
          </Card>
        </Col>
        <Col span={8}>
          <Card size="small">
            <Statistic
              title="Превышений лимита"
              value={exceededCount}
              valueStyle={{ color: exceededCount > 0 ? '#cf1322' : '#3f8600' }}
              prefix={exceededCount > 0 ? <ArrowUpOutlined /> : <CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card size="small">
            <Statistic
              title="Дата расчёта"
              value={date.format('DD.MM.YYYY')}
              valueStyle={{ fontSize: 20 }}
            />
          </Card>
        </Col>
      </Row>

      <Card
        title="Позиции по счетам"
        extra={
          <Space>
            <DatePicker
              value={date}
              onChange={(d) => setDate(d || dayjs())}
              format="DD.MM.YYYY"
              allowClear={false}
            />
            <Select
              placeholder="Все валюты"
              allowClear
              style={{ width: 120 }}
              onChange={setCurrencyFilter}
              options={currencies.map((c) => ({ value: c.code, label: c.code }))}
            />
            <Button
              icon={<DownloadOutlined />}
              loading={reportLoading}
              onClick={handleDownloadReport}
            >
              Отчёт за дату
            </Button>
          </Space>
        }
      >
        <Table
          rowKey="account_id"
          dataSource={data}
          columns={columns}
          loading={loading}
          scroll={{ x: 'max-content' }}
          rowClassName={(r) =>
            r.limit_exceeded ? 'ant-table-row-selected' : ''
          }
          pagination={false}
          bordered
          size="middle"
        />
      </Card>
    </Space>
  )
}
