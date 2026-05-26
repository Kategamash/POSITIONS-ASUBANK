import React, { useState, useEffect } from 'react'
import {
  Table, Button, Modal, Form, Input, Select, Switch,
  Space, Typography, Tag, message, Card, Popconfirm, Avatar,
} from 'antd'
import { PlusOutlined, EditOutlined, StopOutlined, UserOutlined } from '@ant-design/icons'
import { getUsers, createUser, updateUser, deactivateUser } from '../api/admin'
import { useAuth } from '../context/AuthContext'
import { formatDateTime } from '../utils/format'

const { Title } = Typography

const ROLES = [
  { value: 'TRADER', label: 'Трейдер', color: 'green' },
  { value: 'POSITIONER', label: 'Позиционер', color: 'blue' },
  { value: 'ADMIN', label: 'Администратор', color: 'red' },
]
const roleMap = Object.fromEntries(ROLES.map((r) => [r.value, r]))

export default function UsersPage() {
  const { user: me } = useAuth()
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editRecord, setEditRecord] = useState(null)
  const [saving, setSaving] = useState(false)
  const [form] = Form.useForm<any>()

  const load = async () => {
    setLoading(true)
    try {
      setData(await getUsers())
    } catch {
      message.error('Ошибка загрузки пользователей')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const openCreate = () => {
    setEditRecord(null)
    form.resetFields()
    setModalOpen(true)
  }

  const openEdit = (record) => {
    setEditRecord(record)
    form.setFieldsValue({
      full_name: record.full_name,
      role: record.role,
      is_active: record.is_active,
    })
    setModalOpen(true)
  }

  const onSave = async (values) => {
    setSaving(true)
    try {
      if (editRecord) {
        const payload: Record<string, any> = {}
        if (values.full_name !== editRecord.full_name) payload.full_name = values.full_name
        if (values.role !== editRecord.role) payload.role = values.role
        if (values.is_active !== editRecord.is_active) payload.is_active = values.is_active
        if (values.password) payload.password = values.password
        await updateUser(editRecord.id, payload)
        message.success('Пользователь обновлён')
      } else {
        await createUser({
          login: values.login,
          password: values.password,
          full_name: values.full_name,
          role: values.role,
        })
        message.success('Пользователь создан')
      }
      setModalOpen(false)
      load()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Ошибка сохранения')
    } finally {
      setSaving(false)
    }
  }

  const onDeactivate = async (id) => {
    try {
      await deactivateUser(id)
      message.success('Пользователь деактивирован')
      load()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Ошибка')
    }
  }

  const columns = [
    {
      title: 'Пользователь',
      key: 'user',
      render: (_, r) => (
        <Space>
          <Avatar
            size="small"
            icon={<UserOutlined />}
            style={{ background: roleMap[r.role]?.color === 'red' ? '#f5222d' : '#1677ff' }}
          />
          <div>
            <div style={{ fontWeight: 500 }}>{r.full_name}</div>
            <div style={{ fontSize: 12, color: '#8c8c8c', fontFamily: 'monospace' }}>{r.login}</div>
          </div>
        </Space>
      ),
    },
    {
      title: 'Роль',
      dataIndex: 'role',
      key: 'role',
      width: 150,
      render: (v) => {
        const meta = roleMap[v]
        return meta ? (
          <Tag color={meta.color}>{meta.label}</Tag>
        ) : (
          <Tag>{v}</Tag>
        )
      },
    },
    {
      title: 'Статус',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      align: 'center',
      render: (v) =>
        v ? (
          <Tag color="success">Активен</Tag>
        ) : (
          <Tag color="default">Отключён</Tag>
        ),
    },
    {
      title: 'Создан',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 160,
      render: formatDateTime,
    },
    {
      title: 'Действия',
      key: 'actions',
      width: 110,
      align: 'center',
      render: (_, record) => (
        <Space>
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => openEdit(record)}
            size="small"
          />
          {record.is_active && record.id !== me?.id && (
            <Popconfirm
              title="Деактивировать пользователя?"
              onConfirm={() => onDeactivate(record.id)}
              okText="Деактивировать"
              cancelText="Отмена"
              okButtonProps={{ danger: true }}
            >
              <Button
                type="text"
                danger
                icon={<StopOutlined />}
                size="small"
              />
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ]

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Title level={4} style={{ margin: 0 }}>
        Управление пользователями
      </Title>

      <Card
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            Создать пользователя
          </Button>
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

      <Modal
        title={editRecord ? 'Редактировать пользователя' : 'Создать пользователя'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={saving}
        okText="Сохранить"
        cancelText="Отмена"
        width={460}
      >
        <Form form={form} onFinish={onSave} layout="vertical" style={{ marginTop: 16 }}>
          {!editRecord && (
            <Form.Item
              name="login"
              label="Логин"
              rules={[{ required: true, message: 'Введите логин' }]}
            >
              <Input placeholder="trader01" autoComplete="off" />
            </Form.Item>
          )}
          <Form.Item
            name="full_name"
            label="Полное имя"
            rules={[{ required: true, message: 'Введите имя' }]}
          >
            <Input placeholder="Иванов Иван Иванович" />
          </Form.Item>
          <Form.Item
            name="role"
            label="Роль"
            rules={[{ required: true, message: 'Выберите роль' }]}
          >
            <Select
              options={ROLES.map((r) => ({ value: r.value, label: r.label }))}
            />
          </Form.Item>
          {editRecord && (
            <Form.Item name="is_active" label="Статус" valuePropName="checked">
              <Switch checkedChildren="Активен" unCheckedChildren="Отключён" />
            </Form.Item>
          )}
          <Form.Item
            name="password"
            label={editRecord ? 'Новый пароль (оставьте пустым, чтобы не менять)' : 'Пароль'}
            rules={
              !editRecord ? [{ required: true, message: 'Введите пароль' }] : []
            }
          >
            <Input.Password
              placeholder={editRecord ? 'Новый пароль' : 'Придумайте пароль'}
              autoComplete="new-password"
            />
          </Form.Item>
        </Form>
      </Modal>
    </Space>
  )
}
