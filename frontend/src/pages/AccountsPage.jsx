import React, { useState, useEffect } from 'react'
import {
  Table, Button, Modal, Form, Input, Select, InputNumber, Switch,
  Space, Typography, Tag, message, Tooltip, Card, Row, Col,
} from 'antd'
import { PlusOutlined, EditOutlined } from '@ant-design/icons'
import { getAccounts, createAccount, updateAccount } from '../api/accounts'
import { getCurrencies } from '../api/currencies'
import { useAuth } from '../context/AuthContext'
import { formatAmount } from '../utils/format'

const { Title } = Typography

export default function AccountsPage() {
  const { isAdmin } = useAuth()
  const [data, setData] = useState([])
  const [currencies, setCurrencies] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editRecord, setEditRecord] = useState(null)
  const [saving, setSaving] = useState(false)
  const [filterActive, setFilterActive] = useState(null)
  const [filterCurrency, setFilterCurrency] = useState(null)
  const [form] = Form.useForm()

  const load = async () => {
    setLoading(true)
    try {
      const params = {}
      if (filterActive !== null) params.активен = filterActive
      if (filterCurrency) params.код_валюты = filterCurrency
      setData(await getAccounts(params))
    } catch {
      message.error('Ошибка загрузки счетов')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    getCurrencies().then(setCurrencies).catch(() => {})
  }, [])

  useEffect(() => {
    load()
  }, [filterActive, filterCurrency])

  const openCreate = () => {
    setEditRecord(null)
    form.resetFields()
    setModalOpen(true)
  }

  const openEdit = (record) => {
    setEditRecord(record)
    form.setFieldsValue({
      наименование: record.наименование,
      банк_корреспондент: record.банк_корреспондент,
      лимит: record.лимит != null ? Number(record.лимит) : null,
      активен: record.активен,
    })
    setModalOpen(true)
  }

  const onSave = async (values) => {
    setSaving(true)
    try {
      if (editRecord) {
        await updateAccount(editRecord.id, {
          наименование: values.наименование,
          банк_корреспондент: values.банк_корреспондент,
          лимит: values.лимит ?? null,
          активен: values.активен,
        })
        message.success('Счёт обновлён')
      } else {
        await createAccount({
          номер_счета: values.номер_счета,
          наименование: values.наименование,
          код_валюты: values.код_валюты,
          банк_корреспондент: values.банк_корреспондент,
          лимит: values.лимит ?? null,
          активен: true,
        })
        message.success('Счёт создан')
      }
      setModalOpen(false)
      load()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Ошибка сохранения')
    } finally {
      setSaving(false)
    }
  }

  const columns = [
    {
      title: 'Номер счёта',
      dataIndex: 'номер_счета',
      key: 'номер_счета',
      render: (v) => <span style={{ fontFamily: 'monospace', fontWeight: 500 }}>{v}</span>,
    },
    {
      title: 'Наименование',
      dataIndex: 'наименование',
      key: 'наименование',
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
      title: 'Банк-корреспондент',
      dataIndex: 'банк_корреспондент',
      key: 'банк_корреспондент',
      ellipsis: true,
    },
    {
      title: 'Лимит',
      dataIndex: 'лимит',
      key: 'лимит',
      align: 'right',
      render: (v) => (v != null ? formatAmount(v) : <Tag>Без лимита</Tag>),
    },
    {
      title: 'Статус',
      dataIndex: 'активен',
      key: 'активен',
      width: 100,
      align: 'center',
      render: (v) =>
        v ? <Tag color="success">Активен</Tag> : <Tag color="default">Закрыт</Tag>,
    },
    ...(isAdmin
      ? [
          {
            title: '',
            key: 'actions',
            width: 60,
            align: 'center',
            render: (_, record) => (
              <Tooltip title="Редактировать">
                <Button
                  type="text"
                  icon={<EditOutlined />}
                  onClick={() => openEdit(record)}
                  size="small"
                />
              </Tooltip>
            ),
          },
        ]
      : []),
  ]

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Row justify="space-between" align="middle">
        <Col>
          <Title level={4} style={{ margin: 0 }}>
            Счета ностро
          </Title>
        </Col>
      </Row>

      <Card
        extra={
          <Space>
            <Select
              placeholder="Все валюты"
              allowClear
              style={{ width: 120 }}
              onChange={setFilterCurrency}
              options={currencies.map((c) => ({ value: c.код, label: c.код }))}
            />
            <Select
              placeholder="Все статусы"
              allowClear
              style={{ width: 140 }}
              onChange={(v) => setFilterActive(v ?? null)}
              options={[
                { value: true, label: 'Активные' },
                { value: false, label: 'Закрытые' },
              ]}
            />
            {isAdmin && (
              <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
                Создать счёт
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
        title={editRecord ? 'Редактировать счёт' : 'Создать счёт ностро'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={saving}
        okText="Сохранить"
        cancelText="Отмена"
        width={520}
      >
        <Form form={form} onFinish={onSave} layout="vertical" style={{ marginTop: 16 }}>
          {!editRecord && (
            <>
              <Form.Item
                name="номер_счета"
                label="Номер счёта"
                rules={[{ required: true, message: 'Укажите номер счёта' }]}
              >
                <Input placeholder="NOSTRO.USD.001" />
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
            </>
          )}
          <Form.Item
            name="наименование"
            label="Наименование"
            rules={[{ required: true, message: 'Укажите наименование' }]}
          >
            <Input placeholder="Счёт ностро USD (Citibank)" />
          </Form.Item>
          <Form.Item
            name="банк_корреспондент"
            label="Банк-корреспондент"
            rules={[{ required: true, message: 'Укажите банк' }]}
          >
            <Input placeholder="Citibank N.A., New York" />
          </Form.Item>
          <Form.Item name="лимит" label="Лимит (минимальная позиция)">
            <InputNumber
              style={{ width: '100%' }}
              placeholder="Не задан"
              precision={2}
              formatter={(v) => (v ? `${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ' ') : '')}
            />
          </Form.Item>
          {editRecord && (
            <Form.Item name="активен" label="Статус" valuePropName="checked">
              <Switch checkedChildren="Активен" unCheckedChildren="Закрыт" />
            </Form.Item>
          )}
        </Form>
      </Modal>
    </Space>
  )
}
