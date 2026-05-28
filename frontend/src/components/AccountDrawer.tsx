import React, { useEffect, useState } from 'react'
import {
  Drawer, Descriptions, Tag, Table, Spin, Statistic, Row, Col,
  Typography, Space, Alert, Divider,
} from 'antd'
import {
  ArrowUpOutlined, ArrowDownOutlined, ExclamationCircleOutlined,
} from '@ant-design/icons'
import dayjs from 'dayjs'
import { getPosition } from '../api/positions'
import { getPayments } from '../api/payments'
import { formatAmount, formatDate } from '../utils/format'

const { Text, Title } = Typography

interface Account {
  id: string
  account_number: string
  name: string
  currency_code: string
  correspondent_bank: string
  limit: number | null
  is_active: boolean
}

interface Props {
  account: Account | null
  onClose: () => void
}

export default function AccountDrawer({ account, onClose }: Props) {
  const [position, setPosition] = useState<any>(null)
  const [payments, setPayments] = useState<any[]>([])
  const [loadingPos, setLoadingPos] = useState(false)
  const [loadingPay, setLoadingPay] = useState(false)

  useEffect(() => {
    if (!account) return
    const today = dayjs().format('YYYY-MM-DD')

    setPosition(null)
    setPayments([])

    setLoadingPos(true)
    getPosition(account.id, { date: today })
      .then(setPosition)
      .catch(() => setPosition(null))
      .finally(() => setLoadingPos(false))

    setLoadingPay(true)
    getPayments({ account_id: account.id })
      .then((data) => setPayments(data.slice(0, 30)))
      .catch(() => setPayments([]))
      .finally(() => setLoadingPay(false))
  }, [account?.id])

  const paymentColumns = [
    {
      title: 'Дата',
      dataIndex: 'value_date',
      key: 'value_date',
      width: 110,
      render: formatDate,
    },
    {
      title: 'Направление',
      dataIndex: 'direction',
      key: 'direction',
      width: 110,
      render: (v) =>
        v === 'IN' ? (
          <Tag icon={<ArrowDownOutlined />} color="success">Входящий</Tag>
        ) : (
          <Tag icon={<ArrowUpOutlined />} color="error">Исходящий</Tag>
        ),
    },
    {
      title: 'Сумма',
      dataIndex: 'amount',
      key: 'amount',
      align: 'right' as const,
      render: (v, r) => (
        <span style={{ fontWeight: 600, color: r.direction === 'IN' ? '#3f8600' : '#cf1322' }}>
          {r.direction === 'IN' ? '+' : '−'}{formatAmount(v)}
        </span>
      ),
    },
    {
      title: 'Сделка FX',
      dataIndex: 'fx_deal_id',
      key: 'fx_deal_id',
      render: (v) =>
        v ? (
          <Text code style={{ fontSize: 11 }}>
            {String(v).slice(0, 8)}…
          </Text>
        ) : (
          <Text type="secondary">—</Text>
        ),
    },
  ]

  return (
    <Drawer
      title={
        account ? (
          <Space>
            <Text strong style={{ fontFamily: 'monospace' }}>{account.account_number}</Text>
            <Tag color="blue">{account.currency_code}</Tag>
            {!account.is_active && <Tag color="default">Закрыт</Tag>}
          </Space>
        ) : null
      }
      placement="right"
      width={620}
      open={!!account}
      onClose={onClose}
      destroyOnClose
    >
      {account && (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* Реквизиты счёта */}
          <Descriptions bordered size="small" column={1}>
            <Descriptions.Item label="Наименование">{account.name}</Descriptions.Item>
            <Descriptions.Item label="Банк-корреспондент">{account.correspondent_bank}</Descriptions.Item>
            <Descriptions.Item label="Лимит">
              {account.limit != null ? formatAmount(account.limit) : <Text type="secondary">Без лимита</Text>}
            </Descriptions.Item>
            <Descriptions.Item label="Статус">
              {account.is_active
                ? <Tag color="success">Активен</Tag>
                : <Tag color="default">Закрыт</Tag>}
            </Descriptions.Item>
          </Descriptions>

          {/* Текущая позиция */}
          <div>
            <Title level={5} style={{ marginBottom: 12 }}>
              Позиция на сегодня
            </Title>
            {loadingPos ? (
              <div style={{ textAlign: 'center', padding: 16 }}><Spin /></div>
            ) : position ? (
              <>
                {position.limit_exceeded && (
                  <Alert
                    type="error"
                    showIcon
                    icon={<ExclamationCircleOutlined />}
                    message="Лимит превышен"
                    style={{ marginBottom: 12 }}
                  />
                )}
                <Row gutter={12}>
                  <Col span={12}>
                    <Statistic
                      title="Вх. остаток"
                      value={Number(position.opening_balance)}
                      precision={2}
                      valueStyle={{ fontSize: 16 }}
                    />
                  </Col>
                  <Col span={12}>
                    <Statistic
                      title="Корректировки"
                      value={Number(position.corrections_amount)}
                      precision={2}
                      valueStyle={{ fontSize: 16, color: Number(position.corrections_amount) >= 0 ? '#3f8600' : '#cf1322' }}
                      prefix={Number(position.corrections_amount) >= 0 ? '+' : ''}
                    />
                  </Col>
                  <Col span={12} style={{ marginTop: 12 }}>
                    <Statistic
                      title="Оборот IN"
                      value={Number(position.turnover_in)}
                      precision={2}
                      valueStyle={{ fontSize: 16, color: '#3f8600' }}
                      prefix={<ArrowDownOutlined />}
                    />
                  </Col>
                  <Col span={12} style={{ marginTop: 12 }}>
                    <Statistic
                      title="Оборот OUT"
                      value={Number(position.turnover_out)}
                      precision={2}
                      valueStyle={{ fontSize: 16, color: '#cf1322' }}
                      prefix={<ArrowUpOutlined />}
                    />
                  </Col>
                </Row>
                <Divider style={{ margin: '12px 0' }} />
                <Statistic
                  title="Текущая позиция"
                  value={Number(position.current_position)}
                  precision={2}
                  valueStyle={{
                    fontSize: 22,
                    fontWeight: 700,
                    color: position.limit_exceeded ? '#cf1322' : '#1677ff',
                  }}
                  suffix={account.currency_code}
                />
              </>
            ) : (
              <Text type="secondary">Нет данных о позиции на сегодня</Text>
            )}
          </div>

          {/* Последние платежи */}
          <div>
            <Title level={5} style={{ marginBottom: 12 }}>
              Последние платежи
            </Title>
            <Table
              rowKey="id"
              dataSource={payments}
              columns={paymentColumns}
              loading={loadingPay}
              pagination={false}
              size="small"
              bordered
              locale={{ emptyText: 'Платежей нет' }}
              scroll={{ y: 300 }}
            />
          </div>
        </Space>
      )}
    </Drawer>
  )
}
