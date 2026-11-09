import { useHealth } from '../api/health'

export function HomePage() {
  const health = useHealth()

  let apiStatus = health.data?.status
  if (health.isPending) apiStatus = 'checking…'
  if (health.isError) apiStatus = 'unreachable'

  return (
    <>
      <h1>BB Bloom 🍼</h1>
      <p>A baby tracker for sleeps, feeds, diapers, symptoms and medication.</p>
      <p>API: {apiStatus}</p>
    </>
  )
}
