import React, { useState } from 'react'
import {
  Card, Button, Typography, Space, Table, Tag, DatePicker,
  Row, Col, message, Descriptions, Spin, Alert,
} from 'antd'
import {
  ApiOutlined, SyncOutlined, ExportOutlined, EyeOutlined,
} from '@ant-design/icons'
import dayjs from 'dayjs'
import { getFxDeals, getReportsPositions } from '../api/integration'
import { formatAmount, formatDate } from '../utils/format'

const { Title, Text, Paragraph } = Typography

export default function IntegrationPage() {
  const [fxDeals, setFxDeals] = useState(null)
  const [fxLoading, setFxLoading] = useState(false)
  const [reportDate, setReportDate] = useState(dayjs())
  const [reportData, setReportData] = useState(null)
  const [reportLoading, setReportLoading] = useState(false)

  const loadFxDeals = async () => {
    setFxLoading(true)
    try {
      setFxDeals(await getFxDeals())
    } catch (err) {
      message.error(err.response?.data?.detail || 'Ошибка получения данных FX')
    } finally {
      setFxLoading(false)
    }
  }

  const loadReport = async () => {
    setReportLoading(true)
    try {
      setReportData(await getReportsPositions(reportDate.format('YYYY-MM-DD')))
    } catch (err) {
      message.error(err.response?.data?.detail || 'Ошибка экспорта позиций')
    } finally {
      setReportLoading(false)
    }
  }

  const fxDealColumns = [
    { title: 'Тип', dataIndex: 'type', key: 'тип', width: 60, render: (v) => <Tag>{v}</Tag> },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'статус',
      width: 130,
      render: (v) => <Tag color="success">{v}</Tag>,
    },
    { title: 'Валюта покупки', dataIndex: 'buy_currency', key: 'валюта_покупки', width: 130, render: (v) => <Tag color="blue">{v}</Tag> },
    { title: 'Валюта продажи', dataIndex: 'sell_currency', key: 'валюта_продажи', width: 130, render: (v) => <Tag color="orange">{v}</Tag> },
    { title: 'Сумма', dataIndex: 'amount', key: 'amount', align: 'right', render: formatAmount },
    { title: 'Дата валютирования', dataIndex: 'value_date', key: 'value_date', render: formatDate },
    { title: 'Трейдер', dataIndex: 'trader', key: 'трейдер', render: (v) => <span style={{ fontFamily: 'monospace' }}>{v}</span> },
  ]

  const reportColumns = [
    {
      title: 'Счёт',
      dataIndex: 'account_number',
      key: 'счет',
      render: (v) => <span style={{ fontFamily: 'monospace', fontWeight: 500 }}>{v}</span>,
    },
    { title: 'Валюта', dataIndex: 'currency_code', key: 'валюта', width: 80, render: (v) => <Tag color="blue">{v}</Tag> },
    { title: 'Вх. остаток', dataIndex: 'opening_balance', key: 'opening_balance', align: 'right', render: formatAmount },
    {
      title: 'Корректировки',
      dataIndex: 'corrections_amount',
      key: 'корректировки',
      align: 'right',
      render: (v) => {
        const n = Number(v)
        if (n > 0) return <span style={{ color: '#3f8600' }}>+{formatAmount(v)}</span>
        if (n < 0) return <span style={{ color: '#cf1322' }}>{formatAmount(v)}</span>
        return formatAmount(v)
      },
    },
    { title: 'Оборот IN', dataIndex: 'turnover_in', key: 'turnover_in', align: 'right', render: (v) => <span style={{ color: '#3f8600' }}>{formatAmount(v)}</span> },
    { title: 'Оборот OUT', dataIndex: 'turnover_out', key: 'turnover_out', align: 'right', render: (v) => <span style={{ color: '#cf1322' }}>{formatAmount(v)}</span> },
    {
      title: 'Тек. позиция',
      dataIndex: 'current_position',
      key: 'current_position',
      align: 'right',
      render: (v) => <span style={{ fontWeight: 700, color: '#1677ff' }}>{formatAmount(v)}</span>,
    },
  ]

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Title level={4} style={{ margin: 0 }}>
        Интеграция (моки)
      </Title>

      <Alert
        type="info"
        showIcon
        message="Заглушки интеграции"
        description={
          <span>
            Данный раздел содержит симуляцию взаимодействия с внешними системами:
            <br />• <b>FX-АСУБАНК</b> — источник платёжных инструкций и сделок
            <br />• <b>ОТЧЕТЫ-АСУБАНК</b> — потребитель данных о позициях
          </span>
        }
      />

      <Row gutter={16}>
        <Col span={12}>
          <Card
            title={
              <Space>
                <SyncOutlined style={{ color: '#1677ff' }} />
                <span>FX-АСУБАНК — Список сделок</span>
              </Space>
            }
            extra={
              <Button
                type="primary"
                icon={<EyeOutlined />}
                onClick={loadFxDeals}
                loading={fxLoading}
              >
                Получить сделки
              </Button>
            }
          >
            <Paragraph type="secondary" style={{ fontSize: 13 }}>
              Симулирует ответ FX-АСУБАНК со списком подтверждённых валютных сделок.
              В реальной интеграции этот эндпоинт предоставляет FX-система.
            </Paragraph>

            {fxLoading && (
              <div style={{ textAlign: 'center', padding: 24 }}>
                <Spin />
              </div>
            )}

            {fxDeals && (
              <Space direction="vertical" style={{ width: '100%' }}>
                <Descriptions size="small" bordered>
                  <Descriptions.Item label="Источник">{fxDeals.source}</Descriptions.Item>
                  <Descriptions.Item label="Сделок">{fxDeals.deals?.length || 0}</Descriptions.Item>
                </Descriptions>
                <Table
                  rowKey="id"
                  dataSource={fxDeals.deals}
                  columns={fxDealColumns}
                  pagination={false}
                  size="small"
                  bordered
                  scroll={{ x: 'max-content' }}
                />
              </Space>
            )}
          </Card>
        </Col>

        <Col span={12}>
          <Card
            title={
              <Space>
                <ExportOutlined style={{ color: '#52c41a' }} />
                <span>ОТЧЕТЫ-АСУБАНК — Экспорт позиций</span>
              </Space>
            }
            extra={
              <Space>
                <DatePicker
                  value={reportDate}
                  onChange={(d) => setReportDate(d || dayjs())}
                  format="DD.MM.YYYY"
                  allowClear={false}
                />
                <Button
                  type="primary"
                  icon={<ExportOutlined />}
                  onClick={loadReport}
                  loading={reportLoading}
                >
                  Экспортировать
                </Button>
              </Space>
            }
          >
            <Paragraph type="secondary" style={{ fontSize: 13 }}>
              Возвращает позиции по всем активным счетам на выбранную дату.
              В реальной интеграции этот эндпоинт вызывает система ОТЧЕТЫ-АСУБАНК.
            </Paragraph>

            {reportLoading && (
              <div style={{ textAlign: 'center', padding: 24 }}>
                <Spin />
              </div>
            )}

            {reportData && (
              <Space direction="vertical" style={{ width: '100%' }}>
                <Descriptions size="small" bordered>
                  <Descriptions.Item label="Дата">{reportData.date}</Descriptions.Item>
                  <Descriptions.Item label="Счетов">{reportData.account_count}</Descriptions.Item>
                  <Descriptions.Item label="Источник">{reportData.source}</Descriptions.Item>
                </Descriptions>
                <Table
                  rowKey="account_number"
                  dataSource={reportData.positions}
                  columns={reportColumns}
                  pagination={false}
                  size="small"
                  bordered
                  scroll={{ x: 'max-content' }}
                />
              </Space>
            )}
          </Card>
        </Col>
      </Row>

      <Card
        title={
          <Space>
            <ApiOutlined />
            <span>Эндпоинты интеграции</span>
          </Space>
        }
        size="small"
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          {[
            { method: 'GET', path: '/integration/fx/deals', desc: 'Мок: список подтверждённых FX-сделок' },
            { method: 'POST', path: '/integration/fx/notify', desc: 'Мок: приём уведомления о превышении лимита от ПОЗИЦИИ' },
            { method: 'GET', path: '/integration/reports/positions', desc: 'Экспорт позиций для ОТЧЕТЫ-АСУБАНК' },
            { method: 'POST', path: '/payments/incoming', desc: 'Приём платежа от FX-АСУБАНК (без аутентификации)' },
          ].map((ep) => (
            <div key={ep.path} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <Tag color={ep.method === 'GET' ? 'blue' : 'green'} style={{ width: 44, textAlign: 'center' }}>
                {ep.method}
              </Tag>
              <code style={{ fontSize: 12, background: '#f5f5f5', padding: '2px 8px', borderRadius: 4 }}>
                {ep.path}
              </code>
              <Text type="secondary" style={{ fontSize: 13 }}>{ep.desc}</Text>
            </div>
          ))}
        </Space>
      </Card>
    </Space>
  )
}
