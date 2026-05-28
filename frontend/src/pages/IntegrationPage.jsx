import React, { useState } from 'react'
import {
  Card, Button, Typography, Space, Table, DatePicker, Row, Col,
  message, Descriptions, Alert, Tag, Spin,
} from 'antd'
import { ApiOutlined, ExportOutlined, SyncOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { getFxDeals, getFxHealth, getReportsPositions } from '../api/integration'
import { formatAmount, formatDate } from '../utils/format'

const { Title, Paragraph, Text } = Typography

export default function IntegrationPage() {
  const [reportDate, setReportDate] = useState(dayjs())
  const [reportData, setReportData] = useState(null)
  const [reportLoading, setReportLoading] = useState(false)
  const [fxData, setFxData] = useState(null)
  const [fxHealth, setFxHealth] = useState(null)
  const [fxLoading, setFxLoading] = useState(false)

  const loadFx = async () => {
    setFxLoading(true)
    try {
      const [health, deals] = await Promise.all([getFxHealth(), getFxDeals()])
      setFxHealth(health)
      setFxData(deals)
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

  const positionsCols = [
    { title: 'Счёт', dataIndex: 'account_number', key: 'account_number', width: 220 },
    { title: 'Название', dataIndex: 'name', key: 'name' },
    { title: 'Валюта', dataIndex: 'currency_code', key: 'currency_code', width: 90 },
    {
      title: 'Входящий',
      dataIndex: 'opening_balance',
      key: 'opening_balance',
      width: 160,
      align: 'right',
      render: (v) => formatAmount(v),
    },
    {
      title: 'Оборот IN',
      dataIndex: 'turnover_in',
      key: 'turnover_in',
      width: 140,
      align: 'right',
      render: (v) => formatAmount(v),
    },
    {
      title: 'Оборот OUT',
      dataIndex: 'turnover_out',
      key: 'turnover_out',
      width: 140,
      align: 'right',
      render: (v) => formatAmount(v),
    },
    {
      title: 'Текущая',
      dataIndex: 'current_position',
      key: 'current_position',
      width: 160,
      align: 'right',
      render: (v) => <Text strong>{formatAmount(v)}</Text>,
    },
  ]

  const fxDealCols = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 260, render: (v) => <Text code>{v}</Text> },
    { title: 'Тип', dataIndex: 'type', key: 'type', width: 90, render: (v) => <Tag>{v}</Tag> },
    { title: 'Статус', dataIndex: 'status', key: 'status', width: 150, render: (v) => <Tag color="green">{v}</Tag> },
    { title: 'Покупка', dataIndex: 'buy_currency', key: 'buy_currency', width: 100, render: (v) => <Tag color="blue">{v}</Tag> },
    { title: 'Продажа', dataIndex: 'sell_currency', key: 'sell_currency', width: 100, render: (v) => <Tag color="orange">{v}</Tag> },
    { title: 'Сумма', dataIndex: 'amount', key: 'amount', align: 'right', render: (v) => formatAmount(v) },
    { title: 'Курс', dataIndex: 'rate', key: 'rate', align: 'right' },
    { title: 'Дата валютирования', dataIndex: 'value_date', key: 'value_date', render: formatDate },
    { title: 'Трейдер', dataIndex: 'trader', key: 'trader' },
  ]

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Title level={4} style={{ margin: 0 }}>
        Интеграции
      </Title>

      <Alert
        type="info"
        showIcon
        message="Реальные интеграции, без моков"
        description={
          <Space direction="vertical">
            <Text>
              <b>FX-DEAL-MANAGER → POSITIONS-АСУБАНК</b>: при подтверждении сделки
              позиционером FX вызывает <code>POST /payments/incoming</code> для каждой
              ноги сделки. Платежи можно посмотреть в разделе «Платежи».
            </Text>
            <Text>
              <b>POSITIONS-АСУБАНК → ОТЧЁТЫ-АСУБАНК</b>: ОТЧЁТЫ периодически тянут позиции
              через GET <code>/integration/reports/positions</code> (см. ниже).
            </Text>
            <Text>
              <b>Identity Provider</b>: единая точка входа. Все API валидируют JWT через
              JWKS <code>http://185.17.3.75:8083/.well-known/jwks.json</code>, ролевую модель ведёт IdP.
            </Text>
          </Space>
        }
      />

      <Card
        title={
          <Space>
            <SyncOutlined />
            <Text>FX-DEAL-MANAGER</Text>
          </Space>
        }
        extra={
          <Button type="primary" icon={<ApiOutlined />} loading={fxLoading} onClick={loadFx}>
            Проверить FX
          </Button>
        }
      >
        <Paragraph type="secondary">
          Реальный контракт: <code>GET http://185.17.3.75:8000/api/v1/deals</code> с Bearer JWT из IdP.
        </Paragraph>
        {fxLoading && <Spin />}
        {fxHealth && (
          <Descriptions column={3} bordered size="small" style={{ marginBottom: 16 }}>
            <Descriptions.Item label="Сервис">{fxHealth.service}</Descriptions.Item>
            <Descriptions.Item label="Статус">{fxHealth.status}</Descriptions.Item>
            <Descriptions.Item label="БД">{fxHealth.database}</Descriptions.Item>
          </Descriptions>
        )}
        {fxData && (
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Descriptions column={4} bordered size="small">
              <Descriptions.Item label="Источник">{fxData.source}</Descriptions.Item>
              <Descriptions.Item label="Фильтр">{fxData.status || 'все'}</Descriptions.Item>
              <Descriptions.Item label="Всего">{fxData.total}</Descriptions.Item>
              <Descriptions.Item label="На странице">{fxData.deals?.length || 0}</Descriptions.Item>
            </Descriptions>
            <Table
              rowKey="id"
              dataSource={fxData.deals}
              columns={fxDealCols}
              pagination={false}
              bordered
              size="small"
              scroll={{ x: 'max-content' }}
            />
          </Space>
        )}
      </Card>

      <Card
        title={
          <Space>
            <ExportOutlined />
            <Text>Экспорт позиций для ОТЧЁТЫ-АСУБАНК</Text>
          </Space>
        }
      >
        <Paragraph type="secondary">
          Тот же ответ, который ОТЧЁТЫ-АСУБАНК получает в <code>job_sync_positions</code>.
        </Paragraph>
        <Row gutter={[12, 12]} align="middle">
          <Col>
            <DatePicker value={reportDate} onChange={setReportDate} format="DD.MM.YYYY" allowClear={false} />
          </Col>
          <Col>
            <Button type="primary" icon={<ApiOutlined />} loading={reportLoading} onClick={loadReport}>
              Запросить
            </Button>
          </Col>
        </Row>

        {reportData && (
          <Space direction="vertical" size="middle" style={{ width: '100%', marginTop: 16 }}>
            <Descriptions column={3} bordered size="small">
              <Descriptions.Item label="Источник">{reportData.source}</Descriptions.Item>
              <Descriptions.Item label="Дата">{formatDate(reportData.date)}</Descriptions.Item>
              <Descriptions.Item label="Счетов">{reportData.account_count}</Descriptions.Item>
            </Descriptions>
            <Table
              rowKey="account_number"
              dataSource={reportData.positions}
              columns={positionsCols}
              pagination={false}
              bordered
              size="small"
            />
          </Space>
        )}
      </Card>
    </Space>
  )
}
