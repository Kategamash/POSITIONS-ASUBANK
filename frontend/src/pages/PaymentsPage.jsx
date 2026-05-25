import React, { useState, useEffect } from 'react'
import {
  Table, Button, Modal, Form, Select, DatePicker, InputNumber,
  Space, Typography, Tag, message, Card,
} from 'antd'
import { SendOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { getPayments, sendIncomingPayment } from '../api/payments'
import { getAccounts } from '../api/accounts'
import { getCurrencies } from '../api/currencies'
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
  const [form] = Form.useForm()

  const load = async () => {
    setLoading(true)
    try {
      const params = {}
      if (filterAccount) params.id_счета = filterAccount
      if (filterDate) params.дата_валютирования = filterDate.format('YYYY-MM-DD')
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
        id_сделки: generateUUID(),
        код_валюты: values.код_валюты,
        сумма: values.сумма,
        дата_валютирования: values.дата_валютирования.format('YYYY-MM-DD'),
        id_счета: values.id_счета,
        направление: values.направление,
      })
      message.success(`Платёж принят. ID: ${result.платеж_id}`)
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
      dataIndex: 'дата_обработки',
      key: 'дата_обработки',
      width: 130,
      render: formatDate,
    },
    {
      title: 'Дата валютирования',
      dataIndex: 'дата_валютирования',
      key: 'дата_валютирования',
      width: 150,
      render: formatDate,
    },
    {
      title: 'Счёт',
      dataIndex: 'id_счета',
      key: 'id_счета',
      render: (v) => {
        const acc = accountMap[v]
        return acc ? (
          <Space>
            <span style={{ fontFamily: 'monospace', fontWeight: 500 }}>{acc.номер_счета}</span>
            <Tag color="blue">{acc.код_валюты}</Tag>
          </Space>
        ) : (
          <span style={{ fontFamily: 'monospace', color: '#8c8c8c', fontSize: 12 }}>{v}</span>
        )
      },
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
      title: 'Сумма',
      dataIndex: 'сумма',
      key: 'сумма',
      align: 'right',
      render: formatAmount,
    },
    {
      title: 'Направление',
      dataIndex: 'направление',
      key: 'направление',
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
      title: 'ID сделки FX',
      dataIndex: 'id_сделки_fx',
      key: 'id_сделки_fx',
      ellipsis: true,
      render: (v) =>
        v ? (
          <span style={{ fontFamily: 'monospace', fontSize: 11, color: '#595959' }}>{v}</span>
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
                label: `${a.номер_счета} (${a.код_валюты})`,
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
                form.setFieldValue('дата_валютирования', dayjs())
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
          columns={columns}
          loading={loading}
          pagination={{ pageSize: 20 }}
          bordered
          size="middle"
        />
      </Card>

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
            name="id_счета"
            label="Счёт ностро"
            rules={[{ required: true, message: 'Выберите счёт' }]}
          >
            <Select
              placeholder="Выберите счёт"
              showSearch
              options={accounts.map((a) => ({
                value: a.id,
                label: `${a.номер_счета} — ${a.наименование} (${a.код_валюты})`,
              }))}
              filterOption={(input, opt) =>
                opt.label.toLowerCase().includes(input.toLowerCase())
              }
            />
          </Form.Item>
          <Form.Item
            name="код_валюты"
            label="Валюта"
            rules={[{ required: true, message: 'Выберите валюту' }]}
          >
            <Select
              placeholder="Выберите валюту"
              options={currencies.map((c) => ({
                value: c.код,
                label: `${c.код} — ${c.наименование}`,
              }))}
            />
          </Form.Item>
          <Form.Item
            name="направление"
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
            name="сумма"
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
            name="дата_валютирования"
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
