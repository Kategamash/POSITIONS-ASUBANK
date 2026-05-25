import React, { createContext, useContext, useState, useCallback } from 'react'
import { login as apiLogin, logout as apiLogout } from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const u = localStorage.getItem('user')
      return u ? JSON.parse(u) : null
    } catch {
      return null
    }
  })

  const login = useCallback(async (логин, пароль) => {
    const data = await apiLogin(логин, пароль)
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.пользователь))
    setUser(data.пользователь)
    return data.пользователь
  }, [])

  const logout = useCallback(async () => {
    try {
      await apiLogout()
    } catch {}
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
  }, [])

  const isAdmin = user?.роль === 'ADMIN'
  const isPositionerOrAdmin = user?.роль === 'POSITIONER' || user?.роль === 'ADMIN'

  return (
    <AuthContext.Provider value={{ user, login, logout, isAdmin, isPositionerOrAdmin }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
