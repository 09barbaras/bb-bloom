import { Link, Outlet } from 'react-router'

export function Layout() {
  return (
    <>
      <header>
        <Link to="/">BB Bloom 🍼</Link>
      </header>
      <main>
        <Outlet />
      </main>
    </>
  )
}
