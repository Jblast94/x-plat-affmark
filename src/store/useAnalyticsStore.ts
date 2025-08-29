import { create } from 'zustand';
import { analyticsAPI } from '../services/api';
import { toast } from 'sonner';

interface AnalyticsState {
  dashboardStats: {
    total_campaigns: number;
    active_campaigns: number;
    total_tweets: number;
    posted_tweets: number;
    scheduled_tweets: number;
    total_likes: number;
    total_retweets: number;
    total_replies: number;
    total_impressions: number;
    avg_engagement_rate: number;
    total_affiliate_links: number;
    active_affiliate_links: number;
    estimated_revenue: number;
  } | null;
  engagementTrends: Array<{
    date: string;
    likes: number;
    retweets: number;
    replies: number;
    impressions: number;
    engagement_rate: number;
  }>;
  topTweets: Array<{
    id: number;
    content: string;
    likes: number;
    retweets: number;
    replies: number;
    impressions: number;
    engagement_rate: number;
    posted_at: string;
  }>;
  campaignPerformance: Array<{
    id: number;
    name: string;
    total_tweets: number;
    posted_tweets: number;
    total_likes: number;
    total_retweets: number;
    total_replies: number;
    total_impressions: number;
    avg_engagement_rate: number;
    estimated_revenue: number;
  }>;
  affiliatePerformance: Array<{
    id: number;
    name: string;
    url: string;
    total_tweets: number;
    posted_tweets: number;
    total_likes: number;
    total_retweets: number;
    total_replies: number;
    total_impressions: number;
    estimated_clicks: number;
    estimated_revenue: number;
  }>;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  fetchDashboardStats: () => Promise<void>;
  fetchEngagementTrends: (params?: {
    days?: number;
    granularity?: 'day' | 'week' | 'month';
  }) => Promise<void>;
  fetchTopTweets: (params?: {
    metric?: 'likes' | 'retweets' | 'impressions' | 'engagement_rate';
    limit?: number;
    days?: number;
  }) => Promise<void>;
  fetchCampaignPerformance: (campaign_id?: number) => Promise<void>;
  fetchAffiliatePerformance: (affiliate_id?: number) => Promise<void>;
  generateReport: (params: {
    start_date: string;
    end_date: string;
    report_type: 'summary' | 'detailed' | 'campaign' | 'affiliate';
  }) => Promise<any>;
  comparePerformance: (params: {
    period1_start: string;
    period1_end: string;
    period2_start: string;
    period2_end: string;
  }) => Promise<any>;
  exportData: (params: {
    data_type: 'summary' | 'tweets' | 'campaign' | 'affiliate';
    format: 'json' | 'csv';
    start_date?: string;
    end_date?: string;
  }) => Promise<any>;
  refreshAnalytics: () => Promise<void>;
  getMetricsSummary: () => Promise<void>;
  clearError: () => void;
}

export const useAnalyticsStore = create<AnalyticsState>((set, get) => ({
  dashboardStats: null,
  engagementTrends: [],
  topTweets: [],
  campaignPerformance: [],
  affiliatePerformance: [],
  isLoading: false,
  error: null,

  fetchDashboardStats: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await analyticsAPI.getDashboard();
      const stats = response.data;
      
      set({ 
        dashboardStats: stats,
        isLoading: false,
        error: null 
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to fetch dashboard stats';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
    }
  },

  fetchEngagementTrends: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      // Convert days to start_date and end_date if needed
      const apiParams = {
        start_date: new Date(Date.now() - (params.days || 30) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        end_date: new Date().toISOString().split('T')[0],
        granularity: params.granularity
      };
      
      const response = await analyticsAPI.getEngagementTrends(apiParams);
      const trends = response.data;
      
      set({ 
        engagementTrends: trends,
        isLoading: false,
        error: null 
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to fetch engagement trends';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
    }
  },

  fetchTopTweets: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response = await analyticsAPI.getTopTweets(params);
      const tweets = response.data;
      
      set({ 
        topTweets: tweets,
        isLoading: false,
        error: null 
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to fetch top tweets';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
    }
  },

  fetchCampaignPerformance: async (campaign_id) => {
    set({ isLoading: true, error: null });
    try {
      const response = await analyticsAPI.getCampaignPerformance(campaign_id);
      const performance = response.data;
      
      set({ 
        campaignPerformance: Array.isArray(performance) ? performance : [performance],
        isLoading: false,
        error: null 
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to fetch campaign performance';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
    }
  },

  fetchAffiliatePerformance: async (affiliate_id) => {
    set({ isLoading: true, error: null });
    try {
      const response = await analyticsAPI.getAffiliatePerformance(affiliate_id);
      const performance = response.data;
      
      set({ 
        affiliatePerformance: Array.isArray(performance) ? performance : [performance],
        isLoading: false,
        error: null 
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to fetch affiliate performance';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
    }
  },

  generateReport: async (params) => {
    set({ isLoading: true, error: null });
    try {
      const response = await analyticsAPI.generateReport(params);
      const report = response.data;
      
      set({ 
        isLoading: false,
        error: null 
      });
      
      toast.success('Report generated successfully!');
      return report;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to generate report';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      throw error;
    }
  },

  comparePerformance: async (params) => {
    set({ isLoading: true, error: null });
    try {
      const response = await analyticsAPI.comparePerformance(params);
      const comparison = response.data;
      
      set({ 
        isLoading: false,
        error: null 
      });
      
      return comparison;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to compare performance';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      throw error;
    }
  },

  exportData: async (params) => {
    set({ isLoading: true, error: null });
    try {
      const response = await analyticsAPI.exportData(params);
      const data = response.data;
      
      set({ 
        isLoading: false,
        error: null 
      });
      
      toast.success('Data exported successfully!');
      return data;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to export data';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      throw error;
    }
  },

  refreshAnalytics: async () => {
    set({ isLoading: true, error: null });
    try {
      await analyticsAPI.refreshData();
      
      // Refresh dashboard stats after analytics refresh
      await get().fetchDashboardStats();
      
      set({ 
        isLoading: false,
        error: null 
      });
      
      toast.success('Analytics data refreshed successfully!');
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to refresh analytics';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
    }
  },

  getMetricsSummary: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await analyticsAPI.getMetricsSummary();
      const summary = response.data;
      
      set({ 
        dashboardStats: {
          ...get().dashboardStats,
          ...summary
        },
        isLoading: false,
        error: null 
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to fetch metrics summary';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));