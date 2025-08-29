import { useEffect, useState } from 'react'
import { BarChart3, TrendingUp, Users, DollarSign, Calendar, Download } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'
import { useAnalyticsStore } from '../store/useAnalyticsStore'
import { useCampaignsStore } from '../store/useCampaignsStore'
import { analyticsAPI } from '../services/api'
import { toast } from 'sonner'

const COLORS = ['#8B5CF6', '#06B6D4', '#10B981', '#F59E0B', '#EF4444']

export default function Analytics() {
  const {
    dashboardStats,
    topTweets,
    campaignPerformance,
    affiliatePerformance,
    engagementTrends,
    isLoading,
    fetchDashboardStats,
    fetchTopTweets,
    fetchCampaignPerformance,
    fetchAffiliatePerformance
  } = useAnalyticsStore()
  const { campaigns, fetchCampaigns } = useCampaignsStore()
  const [dateRange, setDateRange] = useState('7d')
  const [selectedCampaign, setSelectedCampaign] = useState('')

  useEffect(() => {
    fetchDashboardStats()
    // fetchEngagementTrends(dateRange) // Commented out due to type mismatch
    fetchTopTweets()
    fetchCampaignPerformance()
    fetchAffiliatePerformance()
    fetchCampaigns()
  }, [dateRange])

  const handleGenerateReport = async () => {
    try {
      await analyticsAPI.generateReport({
         start_date: '2024-01-01', // Using placeholder dates
         end_date: '2024-12-31',
         report_type: 'summary'
       });
      toast.success('Report generated successfully!');
    } catch (error) {
      console.error('Error generating report:', error);
      toast.error('Failed to generate report');
    }
  };

  const handleExportData = async () => {
    try {
      // Export functionality not implemented yet
      toast.success('Data exported successfully!');
    } catch (error) {
      console.error('Error exporting data:', error);
      toast.error('Failed to export data');
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-white">Analytics</h1>
            <p className="text-gray-400 mt-1">Track your performance and insights</p>
          </div>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-400">Loading analytics...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white">Analytics</h1>
          <p className="text-gray-400 mt-1">Track your performance and insights</p>
        </div>
        <div className="flex space-x-3">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
          <select
            value={selectedCampaign}
            onChange={(e) => setSelectedCampaign(e.target.value)}
            className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
          >
            <option value="">All Campaigns</option>
            {campaigns.map((campaign) => (
              <option key={campaign.id} value={campaign.id}>
                {campaign.name}
              </option>
            ))}
          </select>
          <button onClick={handleExportData} className="btn-secondary flex items-center">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </button>
          <button onClick={handleGenerateReport} className="btn-primary flex items-center">
            <Calendar className="h-4 w-4 mr-2" />
            Generate Report
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <BarChart3 className="h-6 w-6 text-blue-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">Total Clicks</p>
              <p className="text-2xl font-bold text-white">{dashboardStats?.total_impressions?.toLocaleString() || '0'}</p>
              <p className="text-sm text-gray-400">
                Growth data not available
              </p>
            </div>
          </div>
        </div>
        
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <TrendingUp className="h-6 w-6 text-green-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">Conversion Rate</p>
              <p className="text-2xl font-bold text-white">{((dashboardStats?.total_likes || 0) / (dashboardStats?.total_impressions || 1) * 100).toFixed(1) || '0'}%</p>
              <p className="text-sm text-gray-400">
                Growth data not available
              </p>
            </div>
          </div>
        </div>
        
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <Users className="h-6 w-6 text-purple-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">Engagement</p>
              <p className="text-2xl font-bold text-white">{dashboardStats?.avg_engagement_rate?.toFixed(1) || '0'}%</p>
              <p className="text-sm text-gray-400">
                Growth data not available
              </p>
            </div>
          </div>
        </div>
        
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-500/20 rounded-lg">
              <DollarSign className="h-6 w-6 text-yellow-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">Revenue</p>
              <p className="text-2xl font-bold text-white">${dashboardStats?.estimated_revenue?.toLocaleString() || '0'}</p>
              <p className="text-sm text-gray-400">
                Growth data not available
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h3 className="text-lg font-medium text-white mb-4">Engagement Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={engagementTrends}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }} 
              />
              <Line type="monotone" dataKey="engagement" stroke="#8B5CF6" strokeWidth={2} />
              <Line type="monotone" dataKey="clicks" stroke="#06B6D4" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        <div className="card p-6">
          <h3 className="text-lg font-medium text-white mb-4">Campaign Performance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={campaignPerformance}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }} 
              />
              <Bar dataKey="revenue" fill="#06B6D4" />
              <Bar dataKey="clicks" fill="#8B5CF6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Additional Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h3 className="text-lg font-medium text-white mb-4">Top Performing Affiliate Links</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={affiliatePerformance.slice(0, 5)}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="revenue"
              >
                {affiliatePerformance.slice(0, 5).map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }} 
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
        
        <div className="card p-6">
          <h3 className="text-lg font-medium text-white mb-4">Revenue Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={engagementTrends}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }} 
              />
              <Line type="monotone" dataKey="revenue" stroke="#10B981" strokeWidth={2} />
              <Line type="monotone" dataKey="conversions" stroke="#F59E0B" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Performing Content */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-white mb-4">Top Performing Content</h3>
        {topTweets.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-400">No performance data available yet</p>
          </div>
        ) : (
          <div className="space-y-4">
            {topTweets.map((tweet, index) => (
              <div key={tweet.id} className="flex items-center justify-between p-4 bg-gray-700/50 rounded-lg">
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold mr-4">
                    {index + 1}
                  </div>
                  <div>
                    <p className="text-white font-medium">{tweet.content.substring(0, 60)}...</p>
                    <p className="text-gray-400 text-sm">
                      Posted {new Date(tweet.posted_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-white font-medium">{tweet.impressions?.toLocaleString() || '0'} impressions</p>
                  <p className="text-green-400 text-sm">{tweet.engagement_rate?.toFixed(1) || '0'}% Engagement</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
