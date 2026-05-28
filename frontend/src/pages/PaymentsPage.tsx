import React, { useState, useEffect } from 'react'
import {
  Table, Button, Modal, Form, Select, DatePicker, InputNumber,
  Space, Typography, Tag, message, Card, Descriptions, Spin, Divider,
} from 'antd'
import { SendOutlined, LinkOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { getPayments, sendIncomingPayment } from '../api/payments'
import { getAccounts } from '../api/accounts'
import { getCurrencies } from '../api/currencies'
import { getFxDeal } from '../api/integration'
import { formatAmount, formatDate, generateUUID } from '../utils/format'

const { Title, Text } = Typography

export default function PaymentsPage() {
  const [data, setData] = useState([])
  const [accounts, setAccounts] = useState([])
  const [currencies, setCurrencies] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [saving, setSaving] = useState(false)
  const [filterAccount, setFilterAccount] = useState(null)
  const [filterDate, setFilterDate] = useState(null)
  const [dealModalOpen, setDealModalOpen] = useState(false)
  const [dealData, setDealData] = useState<any>(null)
  const [dealLoading, setDealLoading] = useState(false)
  const [form] = Form.useForm<any>()

  const openDeal = async (dealId: string) => {
    setDealData(null)
    setDealModalOpen(true)
    setDealLoading(true)
    try {
      setDealData(await getFxDeal(dealId))
    } catch {
      message.error('Не удалось загрузить данные сделки FX')
      setDealModalOpen(false)
    } finally {
      setDealLoading(false)
    }
  }

  const load = async () => {
    setLoading(true)
    try {
      const params: Record<string, any> = {}
      if (filterAccount) params.account_id = filterAccount
      if (filterDate) params.value_date = filterDate.format('YYYY-MM-DD')
      setData(await getPayments(params))
    } catch {
      message.error('Ошибка загрузки платежей')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    getAccounts().then(setAccounts).catch(() => {})
    getCurrencies().then(setCurrencies).catch(() => {})
  }, [])

  useEffect(() => {
    load()
  }, [filterAccount, filterDate])

  const onSend = async (values) => {
    setSaving(true)
    try {
      const result = await sendIncomingPayment({
        deal_id: generateUUID(),
        currency_code: values.currency_code,
        amount: values.amount,
        value_date: values.value_date.format('YYYY-MM-DD'),
        account_id: values.account_id,
        direction: values.direction,
      })
      message.success(`Платёж принят. ID: ${result.payment_id}`)
      setModalOpen(false)
      form.resetFields()
      load()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Ошибка отправки платежа')
    } finally {
      setSaving(false)
    }
  }

  const accountMap = Object.fromEntries(accounts.map((a) => [a.id, a]))

  const columns = [
    {
      title: 'Дата обработки',
      dataIndex: 'processing_date',
      key: 'processing_date',
      width: 130,
      render: formatDate,
    },
    {
      title: 'Дата валютирования',
      dataIndex: 'value_date',
      key: 'value_date',
      width: 150,
      render: formatDate,
    },
    {
      title: 'Счёт',
      dataIndex: 'account_id',
      key: 'account_id',
      render: (v) => {
        const acc = accountMap[v]
        return acc ? (
          <Space>
            <span style={{ fontFamily: 'monospace', fontWeight: 500 }}>{acc.account_number}</span>
            <Tag color="blue">{acc.currency_code}</Tag>
          </Space>
        ) : (
          <span style={{ fontFamily: 'monospace', color: '#8c8c8c', fontSize: 12 }}>{v}</span>
        )
      },
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
      title: 'Сумма',
      dataIndex: 'amount',
      key: 'amount',
      align: 'right',
      render: formatAmount,
    },
    {
      title: 'Направление',
      dataIndex: 'direction',
      key: 'direction',
      width: 110,
      align: 'center',
      render: (v) =>
        v === 'IN' ? (
          <Tag color="success">IN ↓</Tag>
        ) : (
          <Tag color="error">OUT ↑</Tag>
        ),
    },
    {
      title: 'Сделка FX',
      dataIndex: 'fx_deal_id',
      key: 'fx_deal_id',
      render: (v) =>
        v ? (
          <Button
            type="link"
            size="small"
            icon={<LinkOutlined />}
            style={{ fontFamily: 'monospace', fontSize: 11, padding: 0 }}
            onClick={(e) => { e.stopPropagation(); openDeal(v) }}
          >
            {String(v).slice(0, 8)}…
          </Button>
        ) : (
          <Text type="secondary">—</Text>
        ),
    },
  ]

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Title level={4} style={{ margin: 0 }}>
        Платежи
      </Title>

      <Card
        extra={
          <Space>
            <Select
              placeholder="Все счета"
              allowClear
              style={{ width: 220 }}
              onChange={setFilterAccount}
              options={accounts.map((a) => ({
                value: a.id,
                label: `${a.account_number} (${a.currency_code})`,
              }))}
              showSearch
              filterOption={(input, opt) =>
                opt.label.toLowerCase().includes(input.toLowerCase())
              }
            />
            <DatePicker
              placeholder="Дата валютирования"
              onChange={setFilterDate}
              format="DD.MM.YYYY"
              allowClear
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={() => {
                form.resetFields()
                form.setFieldValue('value_date', dayjs())
                setModalOpen(true)
              }}
            >
              Симулировать платёж (FX)
            </Button>
          </Space>
        }
      >
        <Table
          rowKey="id"
          dataSource={data}
          columns={columns as any}
          loading={loading}
          pagination={{ pageSize: 20 }}
          bordered
          size="middle"
        />
      </Card>

      {/* Детали сделки FX */}
      <Modal
        title="Сделка FX"
        open={dealModalOpen}
        onCancel={() => { setDealModalOpen(false); setDealData(null) }}
        footer={null}
        width={560}
      >
        {dealLoading ? (
          <div style={{ textAlign: 'center', padding: 32 }}><Spin /></div>
        ) : dealData ? (
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            <Descriptions bordered size="small" column={2}>
              <Descriptions.Item label="Тип">
                <Tag>{dealData.type}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Статус">
                <Tag color="success">{dealData.status}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Валюта покупки">
                <Tag color="blue">{dealData.buy_currency}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Валюта продажи">
                <Tag color="orange">{dealData.sell_currency}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Сумма">
                {dealData.amount != null ? formatAmount(dealData.amount) : '—'}
              </Descriptions.Item>
              <Descriptions.Item label="Курс">
                {dealData.rate ?? '—'}
              </Descriptions.Item>
              <Descriptions.Item label="Дата сделки">
                {dealData.trade_date ? formatDate(dealData.trade_date) : '—'}
              </Descriptions.Item>
              <Descriptions.Item label="Дата валютирования">
                {dealData.value_date ? formatDate(dealData.value_date) : '—'}
              </Descriptions.Item>
              <Descriptions.Item label="Трейдер" span={2}>
                <Text code>{dealData.trader ?? '—'}</Text>
              </Descriptions.Item>
              {dealData.counterparty && (
                <Descriptions.Item label="Контрагент" span={2}>
                  {dealData.counterparty}
                </Descriptions.Item>
              )}
              {dealData.comment && (
                <Descriptions.Item label="Комментарий" span={2}>
                  {dealData.comment}
                </Descriptions.Item>
              )}
            </Descriptions>
            <Divider style={{ margin: '4px 0' }} />
            <Text type="secondary" style={{ fontSize: 11, fontFamily: 'monospace' }}>
              ID: {dealData.id}
            </Text>
          </Space>
        ) : null}
      </Modal>

      <Modal
        title="Симулировать входящий платёж от FX-АСУБАНК"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={saving}
        okText="Отправить платёж"
        cancelText="Отмена"
        width={480}
      >
        <Form form={form} onFinish={onSend} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item
            name="account_id"
            label="Счёт ностро"
            rules={[{ required: true, message: 'Выберите счёт' }]}
          >
            <Select
              placeholder="Выберите счёт"
              showSearch
              options={accounts.map((a) => ({
                value: a.id,
                label: `${a.account_number} — ${a.name} (${a.currency_code})`,
              }))}
              filterOption={(input, opt) =>
                opt.label.toLowerCase().includes(input.toLowerCase())
              }
            />
          </Form.Item>
          <Form.Item
            name="currency_code"
            label="Валюта"
            rules={[{ required: true, message: 'Выберите валюту' }]}
          >
            <Select
              placeholder="Выберите валюту"
              options={currencies.map((c) => ({
                value: c.code,
                label: `${c.code} — ${c.name}`,
              }))}
            />
          </Form.Item>
          <Form.Item
            name="direction"
            label="Направление"
            rules={[{ required: true, message: 'Выберите направление' }]}
          >
            <Select
              options={[
                { value: 'IN', label: 'IN — поступление на счёт' },
                { value: 'OUT', label: 'OUT — списание со счёта' },
              ]}
            />
          </Form.Item>
          <Form.Item
            name="amount"
            label="Сумма"
            rules={[{ required: true, message: 'Введите сумму' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              precision={2}
              min={0.01}
              formatter={(v) => (v ? `${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ' ') : '')}
              placeholder="0.00"
            />
          </Form.Item>
          <Form.Item
            name="value_date"
            label="Дата валютирования"
            rules={[{ required: true, message: 'Укажите дату' }]}
          >
            <DatePicker style={{ width: '100%' }} format="DD.MM.YYYY" />
          </Form.Item>
        </Form>
      </Modal>
    </Space>
  )
}
