import { useEffect } from 'react'
import {
  ChartBarIcon,
  CursorArrowRaysIcon,
  BanknotesIcon,
  EyeIcon,
} from '@heroicons/react/24/outline'
import { useAnalyticsStore } from '../store/useAnalyticsStore'
import { useTweetsStore } from '../store/useTweetsStore'
import { useAffiliateLinksStore } from '../store/useAffiliateLinksStore'



function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}

export default function Dashboard() {
  const { dashboardStats, fetchDashboardStats, isLoading } = useAnalyticsStore()
  const { tweets, fetchTweets } = useTweetsStore()
  const { affiliateLinks, fetchAffiliateLinks } = useAffiliateLinksStore()

  useEffect(() => {
    fetchDashboardStats()
    // fetchTopTweets() // Not used in current implementation
    fetchTweets()
    fetchAffiliateLinks()
  }, [])

  const stats = [
    {
      name: 'Total Tweets',
      value: dashboardStats?.total_tweets?.toString() || '0',
      change: '0%', // Growth data not available in current API
      changeType: 'positive' as const,
      icon: CursorArrowRaysIcon,
    },
    {
      name: 'Engagement Rate',
      value: dashboardStats?.avg_engagement_rate ? `${dashboardStats.avg_engagement_rate.toFixed(1)}%` : '0%',
      change: '0%', // Growth data not available in current API
      changeType: 'positive' as const,
      icon: EyeIcon,
    },
    {
      name: 'Estimated Revenue',
      value: dashboardStats?.estimated_revenue ? `$${dashboardStats.estimated_revenue.toFixed(2)}` : '$0',
      change: '0%', // Growth data not available in current API
      changeType: 'positive' as const,
      icon: BanknotesIcon,
    },
    {
      name: 'Active Campaigns',
      value: dashboardStats?.active_campaigns?.toString() || '0',
      change: '0%', // Growth data not available in current API
      changeType: 'positive' as const,
      icon: ChartBarIcon,
    },
  ]

  const recentTweets = tweets.slice(0, 3)
  const topPerformingLinks = affiliateLinks
    .sort((a, b) => (b.clicks || 0) - (a.clicks || 0))
    .slice(0, 3)

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-400 mt-1">Overview of your affiliate marketing performance</p>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-400">Loading dashboard data...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-gray-400 mt-1">Overview of your affiliate marketing performance</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <stat.icon className="h-8 w-8 text-primary-400" aria-hidden="true" />
              </div>
              <div className="ml-4 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-400 truncate">{stat.name}</dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-white">{stat.value}</div>
                    <div
                      className={classNames(
                        stat.changeType === 'positive' ? 'text-green-400' : 'text-red-400',
                        'ml-2 flex items-baseline text-sm font-semibold'
                      )}
                    >
                      {stat.change}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h3 className="text-lg font-medium text-white mb-4">Recent Tweets</h3>
          <div className="space-y-4">
            {recentTweets.length > 0 ? (
              recentTweets.map((tweet) => (
                <div key={tweet.id} className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-2 h-2 bg-primary-500 rounded-full mt-2"></div>
                  <div className="flex-1">
                    <p className="text-sm text-gray-300 truncate">
                      {tweet.content}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {tweet.scheduledFor ? new Date(tweet.scheduledFor).toLocaleDateString() : 'Draft'}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-gray-500">No recent tweets</p>
            )}
          </div>
        </div>

        <div className="card p-6">
          <h3 className="text-lg font-medium text-white mb-4">Top Performing Links</h3>
          <div className="space-y-4">
            {topPerformingLinks.length > 0 ? (
              topPerformingLinks.map((link) => (
                <div key={link.id} className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm text-gray-300 truncate">
                      {link.title || link.url}
                    </p>
                    <p className="text-xs text-gray-500">{link.clicks || 0} clicks</p>
                  </div>
                  <div className="text-sm text-green-400 font-medium">
                    ${(link.revenue || 0).toFixed(2)}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-gray-500">No affiliate links yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}