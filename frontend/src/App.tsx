import { useEffect, useState } from 'react'

function App() {
  const [apiStatus, setApiStatus] = useState('checking…')

  useEffect(() => {
    fetch('/api/health')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((data) => setApiStatus(data.status))
      .catch(() => setApiStatus('unreachable'))
  }, [])

  return (
    <main>
      <h1>BB Bloom 🍼</h1>
      <p>A baby tracker for sleeps, feeds, diapers, symptoms and medication.</p>
      <p>API: {apiStatus}</p>
    </main>
  )
}

export default App
