import React, { useState } from 'react'
import {
  Card, Button, Typography, Space, Table, DatePicker, Row, Col,
  message, Descriptions, Alert,
} from 'antd'
import { ApiOutlined, ExportOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { getReportsPositions } from '../api/integration'
import { formatAmount, formatDate } from '../utils/format'

const { Title, Paragraph, Text } = Typography

export default function IntegrationPage() {
  const [reportDate, setReportDate] = useState(dayjs())
  const [reportData, setReportData] = useState(null)
  const [reportLoading, setReportLoading] = useState(false)

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
              JWKS, ролевую модель ведёт IdP.
            </Text>
          </Space>
        }
      />

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
