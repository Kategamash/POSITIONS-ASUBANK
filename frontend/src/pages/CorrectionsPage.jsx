import React, { useState, useEffect } from 'react'
import {
  Table, Button, Modal, Form, Select, DatePicker, InputNumber, Input,
  Space, Typography, Tag, message, Card, Alert, Descriptions, Spin,
} from 'antd'
import { PlusOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { getCorrections, createCorrection } from '../api/corrections'
import { getOpeningBalances } from '../api/positions'
import { getAccounts } from '../api/accounts'
import { useAuth } from '../context/AuthContext'
import { formatAmount, formatDateTime } from '../utils/format'

const { Title, Text } = Typography

export default function CorrectionsPage() {
  const { isPositionerOrAdmin } = useAuth()
  const [data, setData] = useState([])
  const [accounts, setAccounts] = useState([])
  const [openingBalances, setOpeningBalances] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [saving, setSaving] = useState(false)
  const [form] = Form.useForm()

  // For the create correction flow
  const [selectedAccount, setSelectedAccount] = useState(null)
  const [selectedDate, setSelectedDate] = useState(null)
  const [openingBalance, setOpeningBalance] = useState(null)
  const [loadingOB, setLoadingOB] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      setData(await getCorrections())
    } catch {
      message.error('Ошибка загрузки корректировок')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    getAccounts().then(setAccounts).catch(() => {})
    getOpeningBalances().then(setOpeningBalances).catch(() => {})
    load()
  }, [])

  useEffect(() => {
    if (selectedAccount && selectedDate) {
      setLoadingOB(true)
      setOpeningBalance(null)
      getOpeningBalances({
        account_id: selectedAccount,
        date: selectedDate.format('YYYY-MM-DD'),
      })
        .then((list) => setOpeningBalance(list[0] || null))
        .catch(() => setOpeningBalance(null))
        .finally(() => setLoadingOB(false))
    } else {
      setOpeningBalance(null)
    }
  }, [selectedAccount, selectedDate])

  const onSave = async (values) => {
    if (!openingBalance) {
      message.error('Входящий остаток для выбранного счёта и даты не найден')
      return
    }
    setSaving(true)
    try {
      await createCorrection({
        opening_balance_id: openingBalance.id,
        amount: values.amount,
        comment: values.comment || null,
      })
      message.success('Корректировка создана')
      setModalOpen(false)
      resetModalState()
      load()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Ошибка создания корректировки')
    } finally {
      setSaving(false)
    }
  }

  const resetModalState = () => {
    form.resetFields()
    setSelectedAccount(null)
    setSelectedDate(null)
    setOpeningBalance(null)
  }

  const accountMap = Object.fromEntries(accounts.map((a) => [a.id, a]))
  const openingBalanceMap = Object.fromEntries(openingBalances.map((ob) => [ob.id, ob]))

  const columns = [
    {
      title: 'Дата/время',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 170,
      render: formatDateTime,
    },
    {
      title: 'Счёт',
      dataIndex: 'opening_balance_id',
      key: 'account',
      render: (openingBalanceId) => {
        const ob = openingBalanceMap[openingBalanceId]
        const acc = ob ? accountMap[ob.account_id] : null
        return acc ? (
          <Space>
            <span style={{ fontFamily: 'monospace', fontWeight: 500 }}>{acc.account_number}</span>
            <Tag color="blue">{acc.currency_code}</Tag>
          </Space>
        ) : (
          <span style={{ fontFamily: 'monospace', color: '#8c8c8c', fontSize: 12 }}>
            {openingBalanceId}
          </span>
        )
      },
    },
    {
      title: 'Сумма корректировки',
      dataIndex: 'amount',
      key: 'amount',
      align: 'right',
      render: (v) => {
        const n = Number(v)
        if (n > 0) return <span style={{ color: '#3f8600', fontWeight: 600 }}>+{formatAmount(v)}</span>
        return <span style={{ color: '#cf1322', fontWeight: 600 }}>{formatAmount(v)}</span>
      },
    },
    {
      title: 'Комментарий',
      dataIndex: 'comment',
      key: 'comment',
      ellipsis: true,
      render: (v) => v || <Text type="secondary">—</Text>,
    },
  ]

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Title level={4} style={{ margin: 0 }}>
        Корректировки остатков
      </Title>

      <Card
        extra={
          isPositionerOrAdmin && (
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => {
                resetModalState()
                setModalOpen(true)
              }}
            >
              Новая корректировка
            </Button>
          )
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
        title="Создать корректировку входящего остатка"
        open={modalOpen}
        onCancel={() => {
          setModalOpen(false)
          resetModalState()
        }}
        onOk={() => form.submit()}
        confirmLoading={saving}
        okText="Создать"
        cancelText="Отмена"
        okButtonProps={{ disabled: !openingBalance }}
        width={520}
      >
        <Space direction="vertical" style={{ width: '100%', marginTop: 16 }} size="middle">
          <Form layout="vertical">
            <Form.Item label="Счёт ностро" required>
              <Select
                placeholder="Выберите счёт"
                showSearch
                value={selectedAccount}
                onChange={setSelectedAccount}
                options={accounts.map((a) => ({
                  value: a.id,
                  label: `${a.account_number} — ${a.name} (${a.currency_code})`,
                }))}
                filterOption={(input, opt) =>
                  opt.label.toLowerCase().includes(input.toLowerCase())
                }
              />
            </Form.Item>
            <Form.Item label="Дата входящего остатка" required>
              <DatePicker
                style={{ width: '100%' }}
                format="DD.MM.YYYY"
                value={selectedDate}
                onChange={setSelectedDate}
              />
            </Form.Item>
          </Form>

          {loadingOB && (
            <div style={{ textAlign: 'center', padding: 8 }}>
              <Spin size="small" /> Поиск входящего остатка...
            </div>
          )}

          {!loadingOB && selectedAccount && selectedDate && !openingBalance && (
            <Alert
              type="warning"
              message="Входящий остаток не найден"
              description="Для выбранного счёта и даты не установлен входящий остаток. Создайте его в разделе «Входящие остатки»."
              showIcon
            />
          )}

          {openingBalance && (
            <>
              <Alert
                type="success"
                message="Входящий остаток найден"
                showIcon
              />
              <Descriptions bordered size="small" column={1}>
                <Descriptions.Item label="Текущий остаток">
                  {formatAmount(openingBalance.amount)}
                </Descriptions.Item>
                <Descriptions.Item label="Накопленные корректировки">
                  {formatAmount(openingBalance.corrections_amount)}
                </Descriptions.Item>
              </Descriptions>

              <Form form={form} onFinish={onSave} layout="vertical">
                <Form.Item
                  name="amount"
                  label="Сумма корректировки (отрицательная — уменьшение)"
                  rules={[
                    { required: true, message: 'Введите сумму' },
                    {
                      validator: (_, v) =>
                        v !== 0 ? Promise.resolve() : Promise.reject('Сумма не может быть 0'),
                    },
                  ]}
                >
                  <InputNumber
                    style={{ width: '100%' }}
                    precision={2}
                    placeholder="Например: 50000 или -25000"
                    formatter={(v) => (v ? `${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ' ') : '')}
                  />
                </Form.Item>
                <Form.Item name="comment" label="Комментарий">
                  <Input.TextArea rows={2} placeholder="Причина корректировки" />
                </Form.Item>
              </Form>
            </>
          )}
        </Space>
      </Modal>
    </Space>
  )
}
