import React, { useState, useEffect } from 'react'
import {
  Table, Input, Select, Space, Typography, Tag, Card, Button,
} from 'antd'
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons'
import { getAuditLog } from '../api/admin'
import { formatDateTime } from '../utils/format'

const { Title, Text } = Typography

const ACTION_COLORS = {
  LOGIN: 'blue',
  LOGOUT: 'default',
  LOGIN_FAILED: 'error',
  USER_CREATED: 'success',
  USER_UPDATED: 'warning',
  USER_DEACTIVATED: 'error',
  CORRECTION_CREATED: 'geekblue',
  BALANCE_SET: 'cyan',
}

const ACTIONS = [
  'LOGIN', 'LOGOUT', 'LOGIN_FAILED',
  'USER_CREATED', 'USER_UPDATED', 'USER_DEACTIVATED',
  'CORRECTION_CREATED', 'BALANCE_SET',
]

export default function AuditPage() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [filterLogin, setFilterLogin] = useState('')
  const [filterAction, setFilterAction] = useState(null)

  const load = async () => {
    setLoading(true)
    try {
      const params = {}
      if (filterLogin.trim()) params.login = filterLogin.trim()
      if (filterAction) params.action = filterAction
      setData(await getAuditLog(params))
    } catch {
      setData([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const columns = [
    {
      title: 'Дата / Время',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 170,
      render: formatDateTime,
    },
    {
      title: 'Логин',
      dataIndex: 'login',
      key: 'login',
      width: 130,
      render: (v) => <span style={{ fontFamily: 'monospace', fontWeight: 500 }}>{v || '—'}</span>,
    },
    {
      title: 'Действие',
      dataIndex: 'action',
      key: 'действие',
      width: 170,
      render: (v) => (
        <Tag color={ACTION_COLORS[v] || 'default'}>{v}</Tag>
      ),
    },
    {
      title: 'Сущность',
      dataIndex: 'entity',
      key: 'сущность',
      width: 150,
      render: (v) => v || <Text type="secondary">—</Text>,
    },
    {
      title: 'Детали',
      dataIndex: 'details',
      key: 'детали',
      ellipsis: true,
      render: (v) => {
        if (!v || Object.keys(v).length === 0) return <Text type="secondary">—</Text>
        return (
          <span style={{ fontFamily: 'monospace', fontSize: 11, color: '#595959' }}>
            {JSON.stringify(v)}
          </span>
        )
      },
    },
    {
      title: 'IP',
      dataIndex: 'ip_address',
      key: 'ip_адрес',
      width: 130,
      render: (v) =>
        v ? (
          <span style={{ fontFamily: 'monospace', fontSize: 12 }}>{v}</span>
        ) : (
          <Text type="secondary">—</Text>
        ),
    },
  ]

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Title level={4} style={{ margin: 0 }}>
        Журнал аудита
      </Title>

      <Card
        extra={
          <Space>
            <Input
              placeholder="Фильтр по логину"
              prefix={<SearchOutlined />}
              value={filterLogin}
              onChange={(e) => setFilterLogin(e.target.value)}
              style={{ width: 180 }}
              allowClear
            />
            <Select
              placeholder="Все действия"
              allowClear
              style={{ width: 180 }}
              onChange={setFilterAction}
              options={ACTIONS.map((a) => ({ value: a, label: a }))}
            />
            <Button icon={<ReloadOutlined />} onClick={load}>
              Обновить
            </Button>
          </Space>
        }
      >
        <Table
          rowKey="id"
          dataSource={data}
          columns={columns}
          loading={loading}
          pagination={{ pageSize: 25, showSizeChanger: true }}
          bordered
          size="small"
          scroll={{ x: 'max-content' }}
        />
      </Card>
    </Space>
  )
}
