import MainLayout from './components/layout/MainLayout'
import { LayoutProvider } from './contexts/LayoutContext'
import { useRoutes } from 'react-router-dom'
import { appRoutes } from './routes'

function App() {
  const routes = useRoutes(appRoutes)

  return (
    <LayoutProvider>
      <MainLayout>
        {routes}
      </MainLayout>
    </LayoutProvider>
  )
}

export default App
