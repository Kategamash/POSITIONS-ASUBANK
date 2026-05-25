import React, { useState, useEffect } from 'react'
import {
  Table, Button, Modal, Form, Select, DatePicker, InputNumber,
  Space, Typography, Tag, message, Card, Row, Col,
} from 'antd'
import { PlusOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { getOpeningBalances, createOpeningBalance } from '../api/positions'
import { getAccounts } from '../api/accounts'
import { useAuth } from '../context/AuthContext'
import { formatAmount, formatDate } from '../utils/format'

const { Title } = Typography

export default function OpeningBalancesPage() {
  const { isPositionerOrAdmin } = useAuth()
  const [data, setData] = useState([])
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [saving, setSaving] = useState(false)
  const [filterDate, setFilterDate] = useState(null)
  const [filterAccount, setFilterAccount] = useState(null)
  const [form] = Form.useForm()

  const load = async () => {
    setLoading(true)
    try {
      const params = {}
      if (filterDate) params.дата = filterDate.format('YYYY-MM-DD')
      if (filterAccount) params.id_счета = filterAccount
      setData(await getOpeningBalances(params))
    } catch {
      message.error('Ошибка загрузки входящих остатков')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    getAccounts().then(setAccounts).catch(() => {})
  }, [])

  useEffect(() => {
    load()
  }, [filterDate, filterAccount])

  const onSave = async (values) => {
    setSaving(true)
    try {
      await createOpeningBalance({
        id_счета: values.id_счета,
        дата: values.дата.format('YYYY-MM-DD'),
        сумма: values.сумма,
      })
      message.success('Входящий остаток установлен')
      setModalOpen(false)
      form.resetFields()
      load()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Ошибка сохранения')
    } finally {
      setSaving(false)
    }
  }

  const accountMap = Object.fromEntries(accounts.map((a) => [a.id, a]))

  const columns = [
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
          <span style={{ fontFamily: 'monospace', color: '#8c8c8c' }}>{v}</span>
        )
      },
    },
    {
      title: 'Дата',
      dataIndex: 'дата',
      key: 'дата',
      width: 120,
      render: formatDate,
    },
    {
      title: 'Сумма',
      dataIndex: 'сумма',
      key: 'сумма',
      align: 'right',
      render: formatAmount,
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
      title: 'Скорректирован',
      dataIndex: 'скорректирован',
      key: 'скорректирован',
      align: 'center',
      width: 130,
      render: (v) =>
        v ? (
          <Tag icon={<CheckOutlined />} color="success">
            Да
          </Tag>
        ) : (
          <Tag icon={<CloseOutlined />} color="default">
            Нет
          </Tag>
        ),
    },
  ]

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Title level={4} style={{ margin: 0 }}>
        Входящие остатки
      </Title>

      <Card
        extra={
          <Space>
            <DatePicker
              placeholder="Фильтр по дате"
              onChange={setFilterDate}
              format="DD.MM.YYYY"
              allowClear
            />
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
            {isPositionerOrAdmin && (
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => {
                  form.resetFields()
                  setModalOpen(true)
                }}
              >
                Установить остаток
              </Button>
            )}
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
        title="Установить входящий остаток"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={saving}
        okText="Сохранить"
        cancelText="Отмена"
        width={480}
      >
        <Form form={form} onFinish={onSave} layout="vertical" style={{ marginTop: 16 }}>
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
            name="дата"
            label="Дата"
            rules={[{ required: true, message: 'Укажите дату' }]}
          >
            <DatePicker style={{ width: '100%' }} format="DD.MM.YYYY" />
          </Form.Item>
          <Form.Item
            name="сумма"
            label="Сумма входящего остатка"
            rules={[{ required: true, message: 'Укажите сумму' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              precision={2}
              formatter={(v) => (v ? `${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ' ') : '')}
              placeholder="0.00"
            />
          </Form.Item>
        </Form>
      </Modal>
    </Space>
  )
}
