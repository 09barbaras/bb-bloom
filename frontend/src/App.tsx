import { Navigate, Route, Routes } from 'react-router'
import { useAuth } from './auth-context'
import { BabiesPage } from './pages/BabiesPage'
import { BabyPage } from './pages/BabyPage'
import { LoginPage } from './pages/LoginPage'

export default function App() {
  const { isLoggedIn } = useAuth()

  if (!isLoggedIn) return <LoginPage />

  return (
    <Routes>
      <Route path="/" element={<BabiesPage />} />
      <Route path="/babies/:babyId" element={<BabyPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
