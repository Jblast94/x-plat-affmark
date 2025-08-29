import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      } else {
        // No refresh token, redirect to login
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// API Types
export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  created_at: string;
}

export interface Campaign {
  id: number;
  name: string;
  niche: string;
  status: string;
  posts_per_day: number;
  created_at: string;
  user_id: number;
  description?: string;
  targetAudience?: string;
  postingSchedule?: string;
  isActive?: boolean;
}

export interface Tweet {
  id: number;
  content: string;
  tweet_id?: string;
  status: 'draft' | 'scheduled' | 'posted' | 'failed';
  scheduled_time?: string;
  posted_time?: string;
  scheduledFor?: string;
  impressions: number;
  clicks: number;
  retweets: number;
  likes: number;
  campaign_id: number;
  affiliate_link_id?: number;
  campaign?: Campaign;
  affiliate_link?: AffiliateLink;
}

export interface AffiliateLink {
  id: number;
  brand: string;
  product_name: string;
  category: string;
  original_url: string;
  tracked_url: string;
  url?: string;
  title?: string;
  commission_rate: number;
  commission_type: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  clicks?: number;
  revenue?: number;
}

export interface TweetPerformance {
  id: number;
  tweet_id: number;
  impressions: number;
  clicks: number;
  retweets: number;
  likes: number;
  replies: number;
  engagement_rate: number;
  updated_at: string;
}

export interface Analytics {
  total_tweets: number;
  total_clicks: number;
  total_revenue: number;
  conversion_rate: number;
  conversionGrowth?: number;
  engagement_trends: Array<{
    date: string;
    impressions: number;
    clicks: number;
    engagement_rate: number;
  }>;
}

// Auth API
export const authAPI = {
  login: (credentials: { email: string; password: string }) =>
    api.post('/auth/login', credentials),
  
  register: (userData: { username: string; email: string; password: string }) =>
    api.post('/auth/register', userData),
  
  refresh: () => api.post('/auth/refresh'),
  
  logout: () => api.post('/auth/logout'),
  
  getProfile: () => api.get('/auth/profile'),
  
  updateProfile: (data: Partial<User>) => api.put('/auth/profile', data),
  
  changePassword: (data: { current_password: string; new_password: string }) =>
    api.post('/auth/change-password', data),
  
  testXAPI: (credentials: {
    api_key: string;
    api_secret: string;
    access_token: string;
    access_token_secret: string;
    bearer_token: string;
  }) => api.post('/auth/test-x-api', credentials),
};

// Campaigns API
export const campaignsAPI = {
  getAll: (params?: { page?: number; per_page?: number }) =>
    api.get('/campaigns', { params }),
  
  getById: (id: number) => api.get(`/campaigns/${id}`),
  
  create: (data: Omit<Campaign, 'id' | 'created_at' | 'user_id'>) =>
    api.post('/campaigns', data),
  
  update: (id: number, data: Partial<Campaign>) =>
    api.put(`/campaigns/${id}`, data),
  
  delete: (id: number) => api.delete(`/campaigns/${id}`),
  
  getTweets: (id: number, params?: { page?: number; per_page?: number }) =>
    api.get(`/campaigns/${id}/tweets`, { params }),
  
  getPerformance: (id: number, days?: number) =>
    api.get(`/campaigns/${id}/performance`, { params: { days } }),
  
  activate: (id: number) => api.post(`/campaigns/${id}/activate`),
  
  pause: (id: number) => api.post(`/campaigns/${id}/pause`),
};

// Tweets API
export const tweetsAPI = {
  getAll: (params?: {
    page?: number;
    per_page?: number;
    status?: string;
    campaign_id?: number;
  }) => api.get('/tweets', { params }),
  
  getById: (id: number) => api.get(`/tweets/${id}`),
  
  create: (data: {
    content: string;
    campaign_id: number;
    affiliate_link_id?: number;
    scheduled_time?: string;
  }) => api.post('/tweets', data),
  
  update: (id: number, data: Partial<Tweet>) => api.put(`/tweets/${id}`, data),
  
  delete: (id: number) => api.delete(`/tweets/${id}`),
  
  post: (id: number) => api.post(`/tweets/${id}/post`),
  
  schedule: (id: number, scheduled_time: string) =>
    api.post(`/tweets/${id}/schedule`, { scheduled_time }),
  
  cancel: (id: number) => api.post(`/tweets/${id}/cancel`),
  
  getPerformance: (id: number, refresh?: boolean) =>
    api.get(`/tweets/${id}/performance`, { params: { refresh } }),
  
  bulkSchedule: (data: {
    tweets: Array<{
      content: string;
      campaign_id: number;
      affiliate_link_id?: number;
      scheduled_time: string;
    }>;
  }) => api.post('/tweets/bulk-schedule', data),
};

// Analytics API
export const analyticsAPI = {
  getDashboard: () => api.get('/analytics/dashboard'),
  
  getEngagementTrends: (params: {
    start_date: string;
    end_date: string;
    granularity?: 'day' | 'week' | 'month';
  }) => api.get('/analytics/engagement-trends', { params }),
  
  getTopTweets: (params?: {
    metric?: 'likes' | 'retweets' | 'impressions' | 'engagement_rate';
    limit?: number;
    days?: number;
  }) => api.get('/analytics/top-tweets', { params }),
  
  getCampaignPerformance: (campaign_id?: number, days?: number) =>
    api.get('/analytics/campaign-performance', {
      params: { campaign_id, days },
    }),
  
  getAffiliatePerformance: (affiliate_id?: number, days?: number) =>
    api.get('/analytics/affiliate-performance', {
      params: { affiliate_id, days },
    }),
  
  generateReport: (params: {
    start_date: string;
    end_date: string;
    report_type: 'summary' | 'detailed' | 'campaign' | 'affiliate';
  }) => api.get('/analytics/reports', { params }),
  
  comparePerformance: (params: {
    period1_start: string;
    period1_end: string;
    period2_start: string;
    period2_end: string;
  }) => api.get('/analytics/compare', { params }),
  
  exportData: (params: {
    format: 'json' | 'csv';
    data_type: 'summary' | 'tweets' | 'campaign' | 'affiliate';
    start_date?: string;
    end_date?: string;
  }) => api.get('/analytics/export', { params }),
  
  refreshData: () => api.post('/analytics/refresh'),
  
  getMetricsSummary: () => api.get('/analytics/metrics/summary'),
};

// Affiliate Links API
export const affiliateLinksAPI = {
  getAll: (params?: {
    page?: number;
    per_page?: number;
    category?: string;
    active?: boolean;
    search?: string;
  }) => api.get('/affiliate-links', { params }),
  
  getById: (id: number) => api.get(`/affiliate-links/${id}`),
  
  create: (data: Omit<AffiliateLink, 'id' | 'created_at'>) =>
    api.post('/affiliate-links', data),
  
  update: (id: number, data: Partial<AffiliateLink>) =>
    api.put(`/affiliate-links/${id}`, data),
  
  delete: (id: number) => api.delete(`/affiliate-links/${id}`),
  
  toggleActive: (id: number) => api.post(`/affiliate-links/${id}/toggle`),
  
  getPerformance: (id: number, days?: number) =>
    api.get(`/affiliate-links/${id}/performance`, { params: { days } }),
  
  getCategories: () => api.get('/affiliate-links/categories'),
  
  search: (params: {
    query?: string;
    category?: string;
    min_commission?: number;
    max_commission?: number;
    brand?: string;
    active?: boolean;
  }) => api.get('/affiliate-links/search', { params }),
  
  bulkImport: (data: { links: Array<Omit<AffiliateLink, 'id' | 'created_at'>> }) =>
    api.post('/affiliate-links/bulk-import', data),
};

export default api;