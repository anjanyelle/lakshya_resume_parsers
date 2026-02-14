import MainLayout from './components/layout/MainLayout'
import { useRoutes } from 'react-router-dom'
import { appRoutes } from './routes'

function App() {
  const routes = useRoutes(appRoutes)

  return (
    <MainLayout>
      {routes}
    </MainLayout>
  )
}

export default App
