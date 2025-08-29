import { Outlet, Link, useLocation, Navigate } from 'react-router-dom'
import {
  Home,
  Megaphone,
  FileText,
  BarChart3,
  Settings,
  User,
  LogOut,
} from 'lucide-react'
import { useAuthStore } from '../store/useAuthStore'

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Campaigns', href: '/campaigns', icon: Megaphone },
  { name: 'Content', href: '/content', icon: FileText },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
]

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}

export default function Layout() {
  const location = useLocation()
  const { user, logout, isAuthenticated } = useAuthStore()

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  const handleLogout = () => {
    logout()
  }

  return (
    <div className="flex h-screen bg-dark-900">
      {/* Sidebar */}
      <div className="flex flex-col w-64 bg-dark-800 border-r border-dark-700">
        <div className="flex items-center h-16 px-4 border-b border-dark-700">
          <h1 className="text-xl font-bold bg-gradient-to-r from-primary-400 to-secondary-400 bg-clip-text text-transparent">
            X Affiliate Pro
          </h1>
        </div>
        <nav className="flex-1 px-4 py-6 space-y-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={classNames(
                  isActive
                    ? 'bg-gradient-to-r from-primary-600 to-secondary-600 text-white'
                    : 'text-gray-300 hover:bg-dark-700 hover:text-white',
                  'group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200'
                )}
              >
                <item.icon
                  className={classNames(
                    isActive ? 'text-white' : 'text-gray-400 group-hover:text-white',
                    'mr-3 h-5 w-5 transition-colors duration-200'
                  )}
                  aria-hidden="true"
                />
                {item.name}
              </Link>
            )
          })}
        </nav>
        
        {/* User Profile Section */}
        <div className="px-4 py-4 border-t border-dark-700">
          <div className="flex items-center space-x-3 mb-3">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">
                {user?.username || 'User'}
              </p>
              <p className="text-xs text-gray-400 truncate">
                {user?.email || ''}
              </p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center px-3 py-2 text-sm font-medium text-gray-300 hover:bg-dark-700 hover:text-white rounded-lg transition-all duration-200"
          >
            <LogOut className="mr-3 h-5 w-5" />
            Logout
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
