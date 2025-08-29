import React, { useEffect, useState } from 'react'
import { UserIcon, BellIcon, ShieldCheckIcon, KeyIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'
import { useAuthStore } from '../store/useAuthStore'

export default function Settings() {
  const { user, updateProfile, changePassword, testXAPI, isLoading } = useAuthStore()
  const [activeTab, setActiveTab] = useState('profile')
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
    apiKey: false,
    apiSecret: false,
    accessToken: false,
    accessTokenSecret: false
  })
  
  const [profileData, setProfileData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    bio: ''
  })
  
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
  
  const [xApiData, setXApiData] = useState({
    apiKey: '',
    apiSecret: '',
    accessToken: '',
    accessTokenSecret: ''
  })
  
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    campaignUpdates: true,
    performanceReports: true
  })

  useEffect(() => {
    if (user) {
      setProfileData({
        firstName: '',
        lastName: '',
        email: user.email || '',
        bio: ''
      })
      setXApiData({
        apiKey: '',
        apiSecret: '',
        accessToken: '',
        accessTokenSecret: ''
      })
    }
  }, [user])

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await updateProfile(profileData)
  }

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      alert('New passwords do not match')
      return
    }
    await changePassword({ current_password: passwordData.currentPassword, new_password: passwordData.newPassword })
    setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' })
  }

  const handleXApiSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    // X API credentials would be handled separately
    // For now, just test the credentials
    await testXAPI({ 
      api_key: xApiData.apiKey,
      api_secret: xApiData.apiSecret,
      access_token: xApiData.accessToken,
      access_token_secret: xApiData.accessTokenSecret,
      bearer_token: ''
    })
  }

  const handleTestXCredentials = async () => {
    await testXAPI({ 
      api_key: xApiData.apiKey,
      api_secret: xApiData.apiSecret,
      access_token: xApiData.accessToken,
      access_token_secret: xApiData.accessTokenSecret,
      bearer_token: ''
    })
  }

  const togglePasswordVisibility = (field: string) => {
    setShowPasswords(prev => ({ ...prev, [field]: !prev[field as keyof typeof prev] }))
  }

  const tabs = [
    { id: 'profile', label: 'Profile', icon: UserIcon },
    { id: 'security', label: 'Security', icon: ShieldCheckIcon },
    { id: 'xapi', label: 'X API', icon: KeyIcon },
    { id: 'notifications', label: 'Notifications', icon: BellIcon }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-gray-400 mt-1">Manage your account and preferences</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-400'
                    : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4 mr-2" />
                {tab.label}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="card p-6">
          <h2 className="text-xl font-semibold text-white mb-6">Profile Information</h2>
          
          <form onSubmit={handleProfileSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  First Name
                </label>
                <input
                  type="text"
                  value={profileData.firstName}
                  onChange={(e) => setProfileData({ ...profileData, firstName: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
                  placeholder="Enter first name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Last Name
                </label>
                <input
                  type="text"
                  value={profileData.lastName}
                  onChange={(e) => setProfileData({ ...profileData, lastName: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
                  placeholder="Enter last name"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Email
              </label>
              <input
                type="email"
                value={profileData.email}
                onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
                placeholder="Enter email"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Bio
              </label>
              <textarea
                value={profileData.bio}
                onChange={(e) => setProfileData({ ...profileData, bio: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
                rows={3}
                placeholder="Tell us about yourself"
              />
            </div>
            
            <button 
              type="submit" 
              disabled={isLoading}
              className="btn-primary disabled:opacity-50"
            >
              {isLoading ? 'Saving...' : 'Save Changes'}
            </button>
          </form>
        </div>
      )}

      {/* Security Tab */}
      {activeTab === 'security' && (
        <div className="card p-6">
          <h2 className="text-xl font-semibold text-white mb-6">Change Password</h2>
          
          <form onSubmit={handlePasswordSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Current Password
              </label>
              <div className="relative">
                <input
                  type={showPasswords.current ? 'text' : 'password'}
                  value={passwordData.currentPassword}
                  onChange={(e) => setPasswordData({ ...passwordData, currentPassword: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500 pr-10"
                  placeholder="Enter current password"
                  required
                />
                <button
                  type="button"
                  onClick={() => togglePasswordVisibility('current')}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPasswords.current ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                New Password
              </label>
              <div className="relative">
                <input
                  type={showPasswords.new ? 'text' : 'password'}
                  value={passwordData.newPassword}
                  onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500 pr-10"
                  placeholder="Enter new password"
                  required
                  minLength={8}
                />
                <button
                  type="button"
                  onClick={() => togglePasswordVisibility('new')}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPasswords.new ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Confirm New Password
              </label>
              <div className="relative">
                <input
                  type={showPasswords.confirm ? 'text' : 'password'}
                  value={passwordData.confirmPassword}
                  onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500 pr-10"
                  placeholder="Confirm new password"
                  required
                  minLength={8}
                />
                <button
                  type="button"
                  onClick={() => togglePasswordVisibility('confirm')}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPasswords.confirm ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>
            
            <button 
              type="submit" 
              disabled={isLoading}
              className="btn-primary disabled:opacity-50"
            >
              {isLoading ? 'Updating...' : 'Update Password'}
            </button>
          </form>
        </div>
      )}

      {/* X API Tab */}
      {activeTab === 'xapi' && (
        <div className="card p-6">
          <h2 className="text-xl font-semibold text-white mb-6">X API Configuration</h2>
          <p className="text-gray-400 mb-6">Configure your X (Twitter) API credentials for automated posting</p>
          
          <form onSubmit={handleXApiSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                API Key
              </label>
              <div className="relative">
                <input
                  type={showPasswords.apiKey ? 'text' : 'password'}
                  value={xApiData.apiKey}
                  onChange={(e) => setXApiData({ ...xApiData, apiKey: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500 pr-10"
                  placeholder="Enter X API Key"
                />
                <button
                  type="button"
                  onClick={() => togglePasswordVisibility('apiKey')}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPasswords.apiKey ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                API Secret
              </label>
              <div className="relative">
                <input
                  type={showPasswords.apiSecret ? 'text' : 'password'}
                  value={xApiData.apiSecret}
                  onChange={(e) => setXApiData({ ...xApiData, apiSecret: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500 pr-10"
                  placeholder="Enter X API Secret"
                />
                <button
                  type="button"
                  onClick={() => togglePasswordVisibility('apiSecret')}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPasswords.apiSecret ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Access Token
              </label>
              <div className="relative">
                <input
                  type={showPasswords.accessToken ? 'text' : 'password'}
                  value={xApiData.accessToken}
                  onChange={(e) => setXApiData({ ...xApiData, accessToken: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500 pr-10"
                  placeholder="Enter Access Token"
                />
                <button
                  type="button"
                  onClick={() => togglePasswordVisibility('accessToken')}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPasswords.accessToken ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Access Token Secret
              </label>
              <div className="relative">
                <input
                  type={showPasswords.accessTokenSecret ? 'text' : 'password'}
                  value={xApiData.accessTokenSecret}
                  onChange={(e) => setXApiData({ ...xApiData, accessTokenSecret: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500 pr-10"
                  placeholder="Enter Access Token Secret"
                />
                <button
                  type="button"
                  onClick={() => togglePasswordVisibility('accessTokenSecret')}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPasswords.accessTokenSecret ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>
            
            <div className="flex space-x-3">
              <button 
                type="button" 
                onClick={handleTestXCredentials}
                disabled={isLoading}
                className="btn-secondary disabled:opacity-50"
              >
                {isLoading ? 'Testing...' : 'Test Connection'}
              </button>
              <button 
                type="submit" 
                disabled={isLoading}
                className="btn-primary disabled:opacity-50"
              >
                {isLoading ? 'Saving...' : 'Save API Settings'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Notifications Tab */}
      {activeTab === 'notifications' && (
        <div className="card p-6">
          <h2 className="text-xl font-semibold text-white mb-6">Notification Preferences</h2>
          
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white font-medium">Email Notifications</p>
                <p className="text-gray-400 text-sm">Receive updates via email</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={notifications.email}
                  onChange={(e) => setNotifications({ ...notifications, email: e.target.checked })}
                  className="sr-only peer" 
                />
                <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white font-medium">Push Notifications</p>
                <p className="text-gray-400 text-sm">Receive push notifications</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={notifications.push}
                  onChange={(e) => setNotifications({ ...notifications, push: e.target.checked })}
                  className="sr-only peer" 
                />
                <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white font-medium">Campaign Updates</p>
                <p className="text-gray-400 text-sm">Get notified about campaign status changes</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={notifications.campaignUpdates}
                  onChange={(e) => setNotifications({ ...notifications, campaignUpdates: e.target.checked })}
                  className="sr-only peer" 
                />
                <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white font-medium">Performance Reports</p>
                <p className="text-gray-400 text-sm">Weekly performance summaries</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={notifications.performanceReports}
                  onChange={(e) => setNotifications({ ...notifications, performanceReports: e.target.checked })}
                  className="sr-only peer" 
                />
                <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
            
            <button className="btn-primary">
              Save Notification Settings
            </button>
          </div>
        </div>
      )}
    </div>
  )
}