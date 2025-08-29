import React, { useEffect, useState } from 'react'
import { PlusIcon, CalendarIcon, PencilIcon, TrashIcon, ClockIcon } from '@heroicons/react/24/outline'
import { useTweetsStore } from '../store/useTweetsStore'
import { useCampaignsStore } from '../store/useCampaignsStore'
import { Tweet } from '../services/api'

export default function Content() {
  const { tweets, isLoading, fetchTweets, createTweet, updateTweet, deleteTweet, scheduleTweet, postTweet } = useTweetsStore()
  const { campaigns, fetchCampaigns } = useCampaignsStore()
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingTweet, setEditingTweet] = useState<Tweet | null>(null)
  const [activeTab, setActiveTab] = useState<'all' | 'drafts' | 'scheduled' | 'posted'>('all')
  const [formData, setFormData] = useState({
    content: '',
    campaignId: '',
    scheduledFor: '',
    mediaUrls: [] as string[]
  })

  useEffect(() => {
    fetchTweets()
    fetchCampaigns()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (editingTweet) {
      const updateData = {
        content: formData.content,
        campaign_id: formData.campaignId ? parseInt(formData.campaignId) : undefined,
        scheduledFor: formData.scheduledFor ? new Date(formData.scheduledFor).toISOString() : undefined
      }
      await updateTweet(editingTweet.id, updateData)
      setEditingTweet(null)
    } else {
      const createData = {
        content: formData.content,
        campaign_id: parseInt(formData.campaignId),
        scheduled_time: formData.scheduledFor ? new Date(formData.scheduledFor).toISOString() : undefined
      }
      await createTweet(createData)
    }
    setShowCreateModal(false)
    resetForm()
  }

  const resetForm = () => {
    setFormData({
      content: '',
      campaignId: '',
      scheduledFor: '',
      mediaUrls: []
    })
  }

  const handleEdit = (tweet: Tweet) => {
    setEditingTweet(tweet)
    setFormData({
      content: tweet.content,
      campaignId: tweet.campaign_id?.toString() || '',
      scheduledFor: tweet.scheduledFor ? new Date(tweet.scheduledFor).toISOString().slice(0, 16) : '',
      mediaUrls: [] // mediaUrls not available in current Tweet interface
    })
    setShowCreateModal(true)
  }

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this tweet?')) {
      await deleteTweet(id)
    }
  }

  const handleSchedule = async (tweet: Tweet) => {
    const scheduledFor = prompt('Enter schedule time (YYYY-MM-DD HH:MM):')
    if (scheduledFor) {
      await scheduleTweet(tweet.id, new Date(scheduledFor).toISOString())
    }
  }

  const handlePostNow = async (tweet: Tweet) => {
    if (confirm('Post this tweet now?')) {
      await postTweet(tweet.id)
    }
  }

  const filteredTweets = tweets.filter(tweet => {
    switch (activeTab) {
      case 'drafts':
        return tweet.status === 'draft'
      case 'scheduled':
        return tweet.status === 'scheduled'
      case 'posted':
        return tweet.status === 'posted'
      default:
        return true
    }
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'posted': return 'text-green-400'
      case 'scheduled': return 'text-blue-400'
      case 'failed': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-white">Content Management</h1>
            <p className="text-gray-400 mt-1">Manage your tweet templates and content</p>
          </div>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-400">Loading content...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white">Content Management</h1>
          <p className="text-gray-400 mt-1">Manage your tweet templates and content</p>
        </div>
        <button 
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          New Tweet
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {[
            { key: 'all', label: 'All Tweets' },
            { key: 'drafts', label: 'Drafts' },
            { key: 'scheduled', label: 'Scheduled' },
            { key: 'posted', label: 'Posted' }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.key
                  ? 'border-primary-500 text-primary-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tweets List */}
      {filteredTweets.length === 0 ? (
        <div className="card p-6">
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-300 mb-2">No tweets yet</h3>
            <p className="text-gray-500 mb-6">Create your first tweet to get started</p>
            <button 
              onClick={() => setShowCreateModal(true)}
              className="btn-primary"
            >
              Create Tweet
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredTweets.map((tweet) => (
            <div key={tweet.id} className="card p-6">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <p className="text-white mb-2">{tweet.content}</p>
                  <div className="flex items-center space-x-4 text-sm text-gray-400">
                    <span className={`font-medium ${getStatusColor(tweet.status)}`}>
                      {tweet.status.charAt(0).toUpperCase() + tweet.status.slice(1)}
                    </span>
                    {tweet.campaign_id && (
                      <span>
                        Campaign: {campaigns.find(c => c.id === tweet.campaign_id)?.name || 'Unknown'}
                      </span>
                    )}
                    {tweet.scheduledFor && (
                      <span className="flex items-center">
                        <ClockIcon className="h-4 w-4 mr-1" />
                        {new Date(tweet.scheduledFor).toLocaleString()}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex space-x-2 ml-4">
                  {tweet.status === 'draft' && (
                    <>
                      <button
                        onClick={() => handleSchedule(tweet)}
                        className="p-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
                        title="Schedule"
                      >
                        <CalendarIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handlePostNow(tweet)}
                        className="p-2 bg-green-600 hover:bg-green-700 text-white rounded-lg"
                        title="Post Now"
                      >
                        <PlusIcon className="h-4 w-4" />
                      </button>
                    </>
                  )}
                  <button
                    onClick={() => handleEdit(tweet)}
                    className="p-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg"
                    title="Edit"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(tweet.id)}
                    className="p-2 bg-red-600 hover:bg-red-700 text-white rounded-lg"
                    title="Delete"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-lg">
            <h2 className="text-xl font-bold text-white mb-4">
              {editingTweet ? 'Edit Tweet' : 'Create New Tweet'}
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Tweet Content
                </label>
                <textarea
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
                  rows={4}
                  maxLength={280}
                  placeholder="What's happening?"
                  required
                />
                <div className="text-right text-sm text-gray-400 mt-1">
                  {formData.content.length}/280
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Campaign (Optional)
                </label>
                <select
                  value={formData.campaignId}
                  onChange={(e) => setFormData({ ...formData, campaignId: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
                >
                  <option value="">No campaign</option>
                  {campaigns.map((campaign) => (
                    <option key={campaign.id} value={campaign.id}>
                      {campaign.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Schedule For (Optional)
                </label>
                <input
                  type="datetime-local"
                  value={formData.scheduledFor}
                  onChange={(e) => setFormData({ ...formData, scheduledFor: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
                  min={new Date().toISOString().slice(0, 16)}
                />
              </div>
              
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateModal(false)
                    setEditingTweet(null)
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
                  {editingTweet ? 'Update' : 'Create'} Tweet
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}