import React, { useState, useEffect } from 'react'
import {
  Table, Button, Modal, Form, Input, InputNumber,
  Space, Typography, Tag, message, Card, Popconfirm,
} from 'antd'
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons'
import { getCurrencies, createCurrency, deleteCurrency } from '../api/currencies'
import { useAuth } from '../context/AuthContext'

const { Title } = Typography

export default function CurrenciesPage() {
  const { isAdmin } = useAuth()
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [saving, setSaving] = useState(false)
  const [form] = Form.useForm<any>()

  const load = async () => {
    setLoading(true)
    try {
      setData(await getCurrencies())
    } catch {
      message.error('Ошибка загрузки валют')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const onSave = async (values) => {
    setSaving(true)
    try {
      await createCurrency({
        code: values.code.toUpperCase(),
        name: values.name,
        decimal_places: values.decimal_places ?? 2,
      })
      message.success('Валюта добавлена')
      setModalOpen(false)
      form.resetFields()
      load()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Ошибка сохранения')
    } finally {
      setSaving(false)
    }
  }

  const onDelete = async (code) => {
    try {
      await deleteCurrency(code)
      message.success(`Валюта ${code} удалена`)
      load()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Ошибка удаления')
    }
  }

  const columns = [
    {
      title: 'Код',
      dataIndex: 'code',
      key: 'code',
      width: 100,
      render: (v) => <Tag color="blue" style={{ fontSize: 14, padding: '2px 10px' }}>{v}</Tag>,
    },
    {
      title: 'Наименование',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Знаков после запятой',
      dataIndex: 'decimal_places',
      key: 'decimal_places',
      width: 180,
      align: 'center',
    },
    ...(isAdmin
      ? [
          {
            title: 'Действия',
            key: 'actions',
            width: 100,
            align: 'center',
            render: (_, record) => (
              <Popconfirm
                title={`Удалить валюту ${record.code}?`}
                onConfirm={() => onDelete(record.code)}
                okText="Удалить"
                cancelText="Отмена"
                okButtonProps={{ danger: true }}
              >
                <Button type="text" danger icon={<DeleteOutlined />} size="small" />
              </Popconfirm>
            ),
          },
        ]
      : []),
  ]

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Title level={4} style={{ margin: 0 }}>
        Справочник валют
      </Title>

      <Card
        extra={
          isAdmin && (
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => {
                form.resetFields()
                setModalOpen(true)
              }}
            >
              Добавить валюту
            </Button>
          )
        }
      >
        <Table
          rowKey="code"
          dataSource={data}
          columns={columns as any}
          loading={loading}
          pagination={false}
          bordered
          size="middle"
        />
      </Card>

      <Modal
        title="Добавить валюту"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={saving}
        okText="Добавить"
        cancelText="Отмена"
        width={400}
      >
        <Form form={form} onFinish={onSave} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item
            name="code"
            label="Код валюты (ISO 4217)"
            rules={[
              { required: true, message: 'Укажите код' },
              { len: 3, message: 'Код должен состоять из 3 символов' },
            ]}
          >
            <Input placeholder="USD" maxLength={3} style={{ textTransform: 'uppercase' }} />
          </Form.Item>
          <Form.Item
            name="name"
            label="Наименование"
            rules={[{ required: true, message: 'Укажите наименование' }]}
          >
            <Input placeholder="Доллар США" />
          </Form.Item>
          <Form.Item
            name="decimal_places"
            label="Знаков после запятой"
            initialValue={2}
          >
            <InputNumber min={0} max={8} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </Space>
  )
}
