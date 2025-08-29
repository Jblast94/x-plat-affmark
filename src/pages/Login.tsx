import React, { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../store/useAuthStore'
import { toast } from 'sonner'

export default function Login() {
  const [isLogin, setIsLogin] = useState(true)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: '',
    confirmPassword: ''
  })
  const [isLoading, setIsLoading] = useState(false)
  
  const { login, register, isAuthenticated } = useAuthStore()
  
  // Redirect if already authenticated
  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    try {
      if (isLogin) {
        const success = await login({ email: formData.email, password: formData.password })
        if (success) {
          toast.success('Login successful!')
        }
      } else {
        if (formData.password !== formData.confirmPassword) {
          toast.error('Passwords do not match')
          setIsLoading(false)
          return
        }
        
        const success = await register({
          username: formData.username,
          email: formData.email,
          password: formData.password
        })
        
        if (success) {
          toast.success('Registration successful! Please login.')
          setIsLogin(true)
          setFormData({ email: formData.email, password: '', username: '', confirmPassword: '' })
        }
      }
    } catch (error) {
      // Error handling is done in the store
    } finally {
      setIsLoading(false)
    }
  }
  
  const toggleMode = () => {
    setIsLogin(!isLogin)
    setFormData({ email: '', password: '', username: '', confirmPassword: '' })
  }
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-900">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary-400 to-secondary-400 bg-clip-text text-transparent">
            X Affiliate Pro
          </h1>
          <h2 className="mt-6 text-2xl font-bold text-white">
            {isLogin ? 'Sign in to your account' : 'Create your account'}
          </h2>
          <p className="mt-2 text-gray-400">
            {isLogin ? 'Access your affiliate marketing dashboard' : 'Start your affiliate marketing journey'}
          </p>
        </div>
        
        <div className="card p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {!isLogin && (
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-300 mb-2">
                  Username
                </label>
                <input
                  id="username"
                  name="username"
                  type="text"
                  autoComplete="username"
                  required={!isLogin}
                  value={formData.username}
                  onChange={handleInputChange}
                  className="input-field w-full"
                  placeholder="Enter your username"
                />
              </div>
            )}
            
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={formData.email}
                onChange={handleInputChange}
                className="input-field w-full"
                placeholder="Enter your email"
              />
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete={isLogin ? 'current-password' : 'new-password'}
                required
                value={formData.password}
                onChange={handleInputChange}
                className="input-field w-full"
                placeholder="Enter your password"
              />
            </div>
            
            {!isLogin && (
              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-300 mb-2">
                  Confirm Password
                </label>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  autoComplete="new-password"
                  required={!isLogin}
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className="input-field w-full"
                  placeholder="Confirm your password"
                />
              </div>
            )}
            
            {isLogin && (
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    id="remember-me"
                    name="remember-me"
                    type="checkbox"
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-dark-600 rounded bg-dark-700"
                  />
                  <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-300">
                    Remember me
                  </label>
                </div>
                
                <div className="text-sm">
                  <a href="#" className="text-primary-400 hover:text-primary-300">
                    Forgot your password?
                  </a>
                </div>
              </div>
            )}
            
            <button 
              type="submit" 
              disabled={isLoading}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Please wait...' : (isLogin ? 'Sign in' : 'Create account')}
            </button>
          </form>
          
          <div className="mt-6 text-center">
            <p className="text-gray-400">
              {isLogin ? "Don't have an account?" : "Already have an account?"}
              {' '}
              <button
                type="button"
                onClick={toggleMode}
                className="text-primary-400 hover:text-primary-300 font-medium"
              >
                {isLogin ? 'Sign up' : 'Sign in'}
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}