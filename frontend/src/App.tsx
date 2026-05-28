import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import AppLayout from './components/AppLayout'
import LoginPage from './pages/LoginPage'
import PositionsPage from './pages/PositionsPage'
import AccountsPage from './pages/AccountsPage'
import CorrectionsPage from './pages/CorrectionsPage'
import PaymentsPage from './pages/PaymentsPage'
import OpeningBalancesPage from './pages/OpeningBalancesPage'
import CurrenciesPage from './pages/CurrenciesPage'
import UsersPage from './pages/UsersPage'
import AuditPage from './pages/AuditPage'
import IntegrationPage from './pages/IntegrationPage'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/positions" replace />} />
            <Route path="/positions" element={<PositionsPage />} />
            <Route path="/accounts" element={<AccountsPage />} />
            <Route path="/corrections" element={<CorrectionsPage />} />
            <Route path="/payments" element={<PaymentsPage />} />
            <Route path="/currencies" element={<CurrenciesPage />} />
            {/* Только позиционер и администратор */}
            <Route
              path="/opening-balances"
              element={
                <ProtectedRoute allowedRoles={['POSITIONER', 'ADMIN', 'AUDITOR']}>
                  <OpeningBalancesPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/integration"
              element={
                <ProtectedRoute allowedRoles={['POSITIONER', 'ADMIN', 'AUDITOR']}>
                  <IntegrationPage />
                </ProtectedRoute>
              }
            />
            {/* Только администратор */}
            <Route
              path="/admin/users"
              element={
                <ProtectedRoute allowedRoles={['ADMIN']}>
                  <UsersPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/audit"
              element={
                <ProtectedRoute allowedRoles={['ADMIN']}>
                  <AuditPage />
                </ProtectedRoute>
              }
            />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
