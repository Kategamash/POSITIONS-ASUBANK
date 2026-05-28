import React, { useState, useEffect } from 'react'
import { Table, Space, Typography, Tag, message, Card, Avatar, Alert } from 'antd'
import { UserOutlined } from '@ant-design/icons'
import { getUsers } from '../api/admin'
import { formatDateTime } from '../utils/format'

const { Title, Text } = Typography

const ROLES = [
  { value: 'TRADER', label: 'Трейдер', color: 'green' },
  { value: 'POSITIONER', label: 'Позиционер', color: 'blue' },
  { value: 'AUDITOR', label: 'Аудитор', color: 'gold' },
  { value: 'ADMIN', label: 'Администратор', color: 'red' },
]
const roleMap = Object.fromEntries(ROLES.map((r) => [r.value, r]))

export default function UsersPage() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)

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
      width: 160,
      render: (v) => {
        const meta = roleMap[v]
        return meta ? <Tag color={meta.color}>{meta.label}</Tag> : <Tag>{v}</Tag>
      },
    },
    {
      title: 'Статус',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 110,
      align: 'center',
      render: (v) =>
        v ? <Tag color="success">Активен</Tag> : <Tag color="default">Отключён</Tag>,
    },
    {
      title: 'Создан',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: formatDateTime,
    },
  ]

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Title level={4} style={{ margin: 0 }}>
        Пользователи системы
      </Title>

      <Alert
        type="info"
        showIcon
        message="Источник правды — Identity Provider"
        description={
          <Text>
            Управление пользователями (создание, изменение ролей, деактивация) выполняется в
            Identity Provider. На этой странице — только зеркало пользователей, которые уже
            заходили в ПОЗИЦИИ-АСУБАНК.
          </Text>
        }
      />

      <Card>
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
    </Space>
  )
}
