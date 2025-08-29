import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'sonner'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Campaigns from './pages/Campaigns'
import Content from './pages/Content'
import Analytics from './pages/Analytics'
import Settings from './pages/Settings'
import Login from './pages/Login'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-dark-900">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="campaigns" element={<Campaigns />} />
            <Route path="content" element={<Content />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
        <Toaster 
          theme="dark" 
          position="top-right"
          toastOptions={{
            style: {
              background: '#1f2937',
              border: '1px solid #374151',
              color: '#f9fafb',
            },
          }}
        />
      </div>
    </Router>
  )
}

export default App