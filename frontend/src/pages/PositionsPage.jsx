import React, { useState, useEffect } from 'react'
import {
  Table, DatePicker, Select, Space, Typography, Tag, Row, Col, Card,
  Statistic, Badge, Tooltip, Spin,
} from 'antd'
import {
  ExclamationCircleOutlined, ArrowUpOutlined, CheckCircleOutlined,
} from '@ant-design/icons'
import dayjs from 'dayjs'
import { getPositions } from '../api/positions'
import { getCurrencies } from '../api/currencies'
import { formatAmount } from '../utils/format'

const { Title } = Typography

export default function PositionsPage() {
  const [data, setData] = useState([])
  const [currencies, setCurrencies] = useState([])
  const [loading, setLoading] = useState(false)
  const [date, setDate] = useState(dayjs())
  const [currencyFilter, setCurrencyFilter] = useState(null)

  const load = async () => {
    setLoading(true)
    try {
      const params = { дата: date.format('YYYY-MM-DD') }
      if (currencyFilter) params.код_валюты = currencyFilter
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

  const exceededCount = data.filter((d) => d.превышение_лимита).length

  const columns = [
    {
      title: 'Номер счёта',
      dataIndex: 'номер_счета',
      key: 'номер_счета',
      fixed: 'left',
      width: 180,
      render: (v) => <span style={{ fontFamily: 'monospace', fontWeight: 500 }}>{v}</span>,
    },
    {
      title: 'Наименование',
      dataIndex: 'наименование_счета',
      key: 'наименование_счета',
      ellipsis: true,
    },
    {
      title: 'Валюта',
      dataIndex: 'код_валюты',
      key: 'код_валюты',
      width: 80,
      align: 'center',
      render: (v) => <Tag color="blue">{v}</Tag>,
    },
    {
      title: 'Вх. остаток',
      dataIndex: 'входящий_остаток',
      key: 'входящий_остаток',
      align: 'right',
      render: (v) => formatAmount(v),
    },
    {
      title: 'Корректировки',
      dataIndex: 'сумма_корректировок',
      key: 'сумма_корректировок',
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
      dataIndex: 'оборот_in',
      key: 'оборот_in',
      align: 'right',
      render: (v) => <span style={{ color: '#3f8600' }}>{formatAmount(v)}</span>,
    },
    {
      title: 'Оборот OUT',
      dataIndex: 'оборот_out',
      key: 'оборот_out',
      align: 'right',
      render: (v) => <span style={{ color: '#cf1322' }}>{formatAmount(v)}</span>,
    },
    {
      title: 'Тек. позиция',
      dataIndex: 'текущая_позиция',
      key: 'текущая_позиция',
      align: 'right',
      fixed: 'right',
      width: 160,
      render: (v, row) => (
        <Space>
          <span
            style={{
              fontWeight: 700,
              fontSize: 14,
              color: row.превышение_лимита ? '#cf1322' : '#1677ff',
            }}
          >
            {formatAmount(v)}
          </span>
          {row.превышение_лимита && (
            <Tooltip title="Превышение лимита">
              <ExclamationCircleOutlined style={{ color: '#cf1322' }} />
            </Tooltip>
          )}
        </Space>
      ),
    },
    {
      title: 'Лимит',
      dataIndex: 'лимит',
      key: 'лимит',
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
              options={currencies.map((c) => ({ value: c.код, label: c.код }))}
            />
          </Space>
        }
      >
        <Table
          rowKey="id_счета"
          dataSource={data}
          columns={columns}
          loading={loading}
          scroll={{ x: 'max-content' }}
          rowClassName={(r) =>
            r.превышение_лимита ? 'ant-table-row-selected' : ''
          }
          pagination={false}
          bordered
          size="middle"
        />
      </Card>
    </Space>
  )
}
