import React, { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Button, Avatar, Grid, Typography, Tag, Drawer } from 'antd'
import {
  BarChartOutlined,
  BankOutlined,
  SwapOutlined,
  FileTextOutlined,
  DollarOutlined,
  AuditOutlined,
  TeamOutlined,
  ApiOutlined,
  LogoutOutlined,
  UserOutlined,
  CalendarOutlined,
  MenuOutlined,
} from '@ant-design/icons'
import { useAuth } from '../context/AuthContext'

const { Sider, Header, Content } = Layout
const { Text } = Typography
const { useBreakpoint } = Grid

const ROLE_META = {
  ADMIN: { label: 'Администратор', color: 'red' },
  POSITIONER: { label: 'Позиционер', color: 'blue' },
  TRADER: { label: 'Трейдер', color: 'green' },
}

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const screens = useBreakpoint()
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout, isAdmin } = useAuth()
  const isCompact = !screens.md

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const menuItems = [
    {
      key: '/positions',
      icon: <BarChartOutlined />,
      label: 'Позиции',
    },
    {
      key: '/accounts',
      icon: <BankOutlined />,
      label: 'Счета ностро',
    },
    {
      key: '/opening-balances',
      icon: <CalendarOutlined />,
      label: 'Вх. остатки',
    },
    {
      key: '/corrections',
      icon: <SwapOutlined />,
      label: 'Корректировки',
    },
    {
      key: '/payments',
      icon: <DollarOutlined />,
      label: 'Платежи',
    },
    {
      key: '/currencies',
      icon: <FileTextOutlined />,
      label: 'Валюты',
    },
    {
      key: '/integration',
      icon: <ApiOutlined />,
      label: 'Интеграция',
    },
    ...(isAdmin
      ? [
          { type: 'divider' },
          {
            key: 'admin-group',
            icon: <TeamOutlined />,
            label: 'Администрирование',
            children: [
              { key: '/admin/users', label: 'Пользователи', icon: <TeamOutlined /> },
              { key: '/admin/audit', label: 'Журнал аудита', icon: <AuditOutlined /> },
            ],
          },
        ]
      : []),
  ]

  const role = user?.role
  const roleMeta = ROLE_META[role] || { label: role, color: 'default' }

  const handleMenuClick = ({ key }) => {
    if (!key.startsWith('admin-group')) {
      navigate(key)
      setMenuOpen(false)
    }
  }

  const menu = (
    <Menu
      theme="dark"
      mode="inline"
      selectedKeys={[location.pathname]}
      defaultOpenKeys={['admin-group']}
      items={menuItems as any}
      onClick={handleMenuClick}
      style={{ marginTop: 8 }}
    />
  )

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {!isCompact && (
        <Sider
          collapsible
          collapsed={collapsed}
          onCollapse={setCollapsed}
          theme="dark"
          width={220}
          collapsedWidth={80}
        >
          <div
            style={{
              height: 64,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontWeight: 700,
              fontSize: collapsed ? 11 : 13,
              padding: '0 12px',
              borderBottom: '1px solid rgba(255,255,255,0.08)',
              textAlign: 'center',
              letterSpacing: '0.5px',
            }}
          >
            {collapsed ? 'ПА' : 'ПОЗИЦИИ-АСУБАНК'}
          </div>
          {menu}
        </Sider>
      )}
      <Drawer
        title="ПОЗИЦИИ-АСУБАНК"
        placement="left"
        open={menuOpen}
        onClose={() => setMenuOpen(false)}
        width={280}
        styles={{
          body: { padding: 0, background: '#001529' },
          header: { background: '#001529', color: '#fff', borderBottom: '1px solid rgba(255,255,255,0.08)' },
        }}
      >
        {menu}
      </Drawer>
      <Layout style={{ minWidth: 0 }}>
        <Header
          style={{
            background: '#fff',
            padding: isCompact ? '0 12px' : '0 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: isCompact ? 'space-between' : 'flex-end',
            boxShadow: '0 1px 4px rgba(0,21,41,.08)',
            gap: isCompact ? 8 : 12,
            minWidth: 0,
          }}
        >
          {isCompact && (
            <Button
              type="text"
              icon={<MenuOutlined />}
              onClick={() => setMenuOpen(true)}
            />
          )}
          <Avatar
            size="small"
            icon={<UserOutlined />}
            style={{ background: '#1677ff' }}
          />
          <Text
            strong
            ellipsis
            style={{
              fontSize: 14,
              maxWidth: isCompact ? 110 : 260,
            }}
          >
            {user?.full_name}
          </Text>
          <Tag color={roleMeta.color} style={{ margin: 0 }}>
            {roleMeta.label}
          </Tag>
          <Button type="text" icon={<LogoutOutlined />} onClick={handleLogout} size="small">
            {isCompact ? null : 'Выйти'}
          </Button>
        </Header>
        <Content
          style={{
            margin: isCompact ? 12 : 24,
            minHeight: 280,
            minWidth: 0,
            overflow: 'hidden',
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
