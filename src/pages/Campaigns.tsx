import React, { useEffect, useState } from 'react'
import { PlusIcon, PlayIcon, PauseIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline'
import { useCampaignsStore } from '../store/useCampaignsStore'
import { Campaign } from '../services/api'

export default function Campaigns() {
  const { campaigns, isLoading, fetchCampaigns, createCampaign, updateCampaign, deleteCampaign, activateCampaign, pauseCampaign } = useCampaignsStore()
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingCampaign, setEditingCampaign] = useState<Campaign | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    niche: '',
    targetAudience: '',
    postingSchedule: 'daily',
    isActive: true,
    status: 'active',
    posts_per_day: 1
  })

  useEffect(() => {
    fetchCampaigns()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (editingCampaign) {
      await updateCampaign(editingCampaign.id, formData)
      setEditingCampaign(null)
    } else {
      await createCampaign(formData)
    }
    setShowCreateModal(false)
    resetForm()
  }

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      niche: '',
      targetAudience: '',
      postingSchedule: 'daily',
      isActive: true,
      status: 'active',
      posts_per_day: 1
    })
  }

  const handleEdit = (campaign: Campaign) => {
    setEditingCampaign(campaign)
    setFormData({
      name: campaign.name,
      description: campaign.description || '',
      niche: campaign.niche || '',
      targetAudience: campaign.targetAudience || '',
      postingSchedule: campaign.postingSchedule || 'daily',
      isActive: campaign.isActive || false,
      status: campaign.status || 'active',
      posts_per_day: campaign.posts_per_day || 1
    })
    setShowCreateModal(true)
  }

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this campaign?')) {
      await deleteCampaign(id)
    }
  }

  const handleToggleStatus = async (campaign: Campaign) => {
    if (campaign.isActive) {
      await pauseCampaign(campaign.id)
    } else {
      await activateCampaign(campaign.id)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-white">Campaigns</h1>
            <p className="text-gray-400 mt-1">Manage your affiliate marketing campaigns</p>
          </div>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-400">Loading campaigns...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white">Campaigns</h1>
          <p className="text-gray-400 mt-1">Manage your affiliate marketing campaigns</p>
        </div>
        <button 
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          New Campaign
        </button>
      </div>

      {campaigns.length === 0 ? (
        <div className="card p-6">
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-300 mb-2">No campaigns yet</h3>
            <p className="text-gray-500 mb-6">Create your first campaign to start automated posting</p>
            <button 
              onClick={() => setShowCreateModal(true)}
              className="btn-primary"
            >
              Create Campaign
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {campaigns.map((campaign) => (
            <div key={campaign.id} className="card p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-white">{campaign.name}</h3>
                  <p className="text-sm text-gray-400">{campaign.niche}</p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleToggleStatus(campaign)}
                    className={`p-2 rounded-lg ${
                      campaign.isActive 
                        ? 'bg-red-600 hover:bg-red-700 text-white' 
                        : 'bg-green-600 hover:bg-green-700 text-white'
                    }`}
                  >
                    {campaign.isActive ? (
                      <PauseIcon className="h-4 w-4" />
                    ) : (
                      <PlayIcon className="h-4 w-4" />
                    )}
                  </button>
                  <button
                    onClick={() => handleEdit(campaign)}
                    className="p-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(campaign.id)}
                    className="p-2 bg-red-600 hover:bg-red-700 text-white rounded-lg"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
              
              <p className="text-gray-300 text-sm mb-4">{campaign.description}</p>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Target Audience:</span>
                  <span className="text-gray-300">{campaign.targetAudience}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Schedule:</span>
                  <span className="text-gray-300">{campaign.postingSchedule}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Status:</span>
                  <span className={`font-medium ${
                    campaign.isActive ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {campaign.isActive ? 'Active' : 'Paused'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-white mb-4">
              {editingCampaign ? 'Edit Campaign' : 'Create New Campaign'}
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Campaign Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
                  rows={3}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Niche
                </label>
                <input
                  type="text"
                  value={formData.niche}
                  onChange={(e) => setFormData({ ...formData, niche: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Target Audience
                </label>
                <input
                  type="text"
                  value={formData.targetAudience}
                  onChange={(e) => setFormData({ ...formData, targetAudience: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Posting Schedule
                </label>
                <select
                  value={formData.postingSchedule}
                  onChange={(e) => setFormData({ ...formData, postingSchedule: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
                >
                  <option value="hourly">Hourly</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                </select>
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="isActive"
                  checked={formData.isActive}
                  onChange={(e) => setFormData({ ...formData, isActive: e.target.checked })}
                  className="mr-2"
                />
                <label htmlFor="isActive" className="text-sm text-gray-300">
                  Activate campaign immediately
                </label>
              </div>
              
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateModal(false)
                    setEditingCampaign(null)
                    resetForm()
                  }}
                  className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg"
                >
                  {editingCampaign ? 'Update' : 'Create'} Campaign
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}