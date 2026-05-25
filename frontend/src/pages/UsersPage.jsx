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
  const [form] = Form.useForm()

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
      полное_имя: record.полное_имя,
      роль: record.роль,
      активен: record.активен,
    })
    setModalOpen(true)
  }

  const onSave = async (values) => {
    setSaving(true)
    try {
      if (editRecord) {
        const payload = {}
        if (values.полное_имя !== editRecord.полное_имя) payload.полное_имя = values.полное_имя
        if (values.роль !== editRecord.роль) payload.роль = values.роль
        if (values.активен !== editRecord.активен) payload.активен = values.активен
        if (values.пароль) payload.пароль = values.пароль
        await updateUser(editRecord.id, payload)
        message.success('Пользователь обновлён')
      } else {
        await createUser({
          логин: values.логин,
          пароль: values.пароль,
          полное_имя: values.полное_имя,
          роль: values.роль,
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
            style={{ background: roleMap[r.роль]?.color === 'red' ? '#f5222d' : '#1677ff' }}
          />
          <div>
            <div style={{ fontWeight: 500 }}>{r.полное_имя}</div>
            <div style={{ fontSize: 12, color: '#8c8c8c', fontFamily: 'monospace' }}>{r.логин}</div>
          </div>
        </Space>
      ),
    },
    {
      title: 'Роль',
      dataIndex: 'роль',
      key: 'роль',
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
      dataIndex: 'активен',
      key: 'активен',
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
      dataIndex: 'дата_создания',
      key: 'дата_создания',
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
          {record.активен && record.id !== me?.id && (
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
          columns={columns}
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
              name="логин"
              label="Логин"
              rules={[{ required: true, message: 'Введите логин' }]}
            >
              <Input placeholder="trader01" autoComplete="off" />
            </Form.Item>
          )}
          <Form.Item
            name="полное_имя"
            label="Полное имя"
            rules={[{ required: true, message: 'Введите имя' }]}
          >
            <Input placeholder="Иванов Иван Иванович" />
          </Form.Item>
          <Form.Item
            name="роль"
            label="Роль"
            rules={[{ required: true, message: 'Выберите роль' }]}
          >
            <Select
              options={ROLES.map((r) => ({ value: r.value, label: r.label }))}
            />
          </Form.Item>
          {editRecord && (
            <Form.Item name="активен" label="Статус" valuePropName="checked">
              <Switch checkedChildren="Активен" unCheckedChildren="Отключён" />
            </Form.Item>
          )}
          <Form.Item
            name="пароль"
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
