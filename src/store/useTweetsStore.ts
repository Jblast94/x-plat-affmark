import { create } from 'zustand';
import { tweetsAPI, Tweet, TweetPerformance } from '../services/api';
import { toast } from 'sonner';

interface TweetsState {
  tweets: Tweet[];
  currentTweet: Tweet | null;
  tweetPerformance: TweetPerformance | null;
  isLoading: boolean;
  error: string | null;
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
  
  // Actions
  fetchTweets: (params?: {
    page?: number;
    per_page?: number;
    status?: string;
    campaign_id?: number;
  }) => Promise<void>;
  fetchTweetById: (id: number) => Promise<void>;
  createTweet: (data: {
    content: string;
    campaign_id: number;
    affiliate_link_id?: number;
    scheduled_time?: string;
  }) => Promise<boolean>;
  updateTweet: (id: number, data: Partial<Tweet>) => Promise<boolean>;
  deleteTweet: (id: number) => Promise<boolean>;
  postTweet: (id: number) => Promise<boolean>;
  scheduleTweet: (id: number, scheduled_time: string) => Promise<boolean>;
  cancelTweet: (id: number) => Promise<boolean>;
  fetchTweetPerformance: (id: number, refresh?: boolean) => Promise<void>;
  bulkScheduleTweets: (data: {
    tweets: Array<{
      content: string;
      campaign_id: number;
      affiliate_link_id?: number;
      scheduled_time: string;
    }>;
  }) => Promise<{ success: number; failed: number }>;
  clearError: () => void;
  setCurrentTweet: (tweet: Tweet | null) => void;
}

export const useTweetsStore = create<TweetsState>((set) => ({
  tweets: [],
  currentTweet: null,
  tweetPerformance: null,
  isLoading: false,
  error: null,
  pagination: {
    page: 1,
    per_page: 10,
    total: 0,
    pages: 0,
  },

  fetchTweets: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response = await tweetsAPI.getAll(params);
      const { tweets, pagination } = response.data;
      
      set({ 
        tweets, 
        pagination,
        isLoading: false,
        error: null 
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to fetch tweets';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
    }
  },

  fetchTweetById: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const response = await tweetsAPI.getById(id);
      const tweet = response.data;
      
      set({ 
        currentTweet: tweet,
        isLoading: false,
        error: null 
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to fetch tweet';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
    }
  },

  createTweet: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await tweetsAPI.create(data);
      const newTweet = response.data;
      
      set((state) => ({ 
        tweets: [newTweet, ...state.tweets],
        isLoading: false,
        error: null 
      }));
      
      toast.success('Tweet created successfully!');
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to create tweet';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      return false;
    }
  },

  updateTweet: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await tweetsAPI.update(id, data);
      const updatedTweet = response.data;
      
      set((state) => ({ 
        tweets: state.tweets.map(tweet => 
          tweet.id === id ? updatedTweet : tweet
        ),
        currentTweet: state.currentTweet?.id === id ? updatedTweet : state.currentTweet,
        isLoading: false,
        error: null 
      }));
      
      toast.success('Tweet updated successfully!');
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to update tweet';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      return false;
    }
  },

  deleteTweet: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await tweetsAPI.delete(id);
      
      set((state) => ({ 
        tweets: state.tweets.filter(tweet => tweet.id !== id),
        currentTweet: state.currentTweet?.id === id ? null : state.currentTweet,
        isLoading: false,
        error: null 
      }));
      
      toast.success('Tweet deleted successfully!');
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to delete tweet';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      return false;
    }
  },

  postTweet: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const response = await tweetsAPI.post(id);
      const updatedTweet = response.data;
      
      set((state) => ({ 
        tweets: state.tweets.map(tweet => 
          tweet.id === id ? updatedTweet : tweet
        ),
        currentTweet: state.currentTweet?.id === id ? updatedTweet : state.currentTweet,
        isLoading: false,
        error: null 
      }));
      
      toast.success('Tweet posted successfully!');
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to post tweet';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      return false;
    }
  },

  scheduleTweet: async (id, scheduled_time) => {
    set({ isLoading: true, error: null });
    try {
      const response = await tweetsAPI.schedule(id, scheduled_time);
      const updatedTweet = response.data;
      
      set((state) => ({ 
        tweets: state.tweets.map(tweet => 
          tweet.id === id ? updatedTweet : tweet
        ),
        currentTweet: state.currentTweet?.id === id ? updatedTweet : state.currentTweet,
        isLoading: false,
        error: null 
      }));
      
      toast.success('Tweet scheduled successfully!');
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to schedule tweet';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      return false;
    }
  },

  cancelTweet: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const response = await tweetsAPI.cancel(id);
      const updatedTweet = response.data;
      
      set((state) => ({ 
        tweets: state.tweets.map(tweet => 
          tweet.id === id ? updatedTweet : tweet
        ),
        currentTweet: state.currentTweet?.id === id ? updatedTweet : state.currentTweet,
        isLoading: false,
        error: null 
      }));
      
      toast.success('Tweet cancelled successfully!');
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to cancel tweet';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      return false;
    }
  },

  fetchTweetPerformance: async (id, refresh = false) => {
    set({ isLoading: true, error: null });
    try {
      const response = await tweetsAPI.getPerformance(id, refresh);
      const performance = response.data;
      
      set({ 
        tweetPerformance: performance,
        isLoading: false,
        error: null 
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to fetch tweet performance';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
    }
  },

  bulkScheduleTweets: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await tweetsAPI.bulkSchedule(data);
      const { success, failed, results } = response.data;
      
      // Add successfully created tweets to the store
      const successfulTweets = results.filter((result: any) => result.success).map((result: any) => result.tweet);
      
      set((state) => ({ 
        tweets: [...successfulTweets, ...state.tweets],
        isLoading: false,
        error: null 
      }));
      
      if (success > 0) {
        toast.success(`${success} tweets scheduled successfully!`);
      }
      if (failed > 0) {
        toast.error(`${failed} tweets failed to schedule`);
      }
      
      return { success, failed };
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to bulk schedule tweets';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      return { success: 0, failed: data.tweets.length };
    }
  },

  clearError: () => {
    set({ error: null });
  },

  setCurrentTweet: (tweet) => {
    set({ currentTweet: tweet });
  },
}));