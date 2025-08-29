import { create } from 'zustand';
import { campaignsAPI, Campaign, Tweet } from '../services/api';
import { toast } from 'sonner';

interface CampaignsState {
  campaigns: Campaign[];
  currentCampaign: Campaign | null;
  campaignTweets: Tweet[];
  campaignPerformance: any;
  isLoading: boolean;
  error: string | null;
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
  
  // Actions
  fetchCampaigns: (params?: { page?: number; per_page?: number }) => Promise<void>;
  fetchCampaignById: (id: number) => Promise<void>;
  createCampaign: (data: Omit<Campaign, 'id' | 'created_at' | 'user_id'>) => Promise<boolean>;
  updateCampaign: (id: number, data: Partial<Campaign>) => Promise<boolean>;
  deleteCampaign: (id: number) => Promise<boolean>;
  fetchCampaignTweets: (id: number, params?: { page?: number; per_page?: number }) => Promise<void>;
  fetchCampaignPerformance: (id: number, days?: number) => Promise<void>;
  activateCampaign: (id: number) => Promise<boolean>;
  pauseCampaign: (id: number) => Promise<boolean>;
  clearError: () => void;
  setCurrentCampaign: (campaign: Campaign | null) => void;
}

export const useCampaignsStore = create<CampaignsState>((set) => ({
  campaigns: [],
  currentCampaign: null,
  campaignTweets: [],
  campaignPerformance: null,
  isLoading: false,
  error: null,
  pagination: {
    page: 1,
    per_page: 10,
    total: 0,
    pages: 0,
  },

  fetchCampaigns: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response = await campaignsAPI.getAll(params);
      const { campaigns, pagination } = response.data;
      
      set({ 
        campaigns, 
        pagination,
        isLoading: false,
        error: null 
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to fetch campaigns';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
    }
  },

  fetchCampaignById: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const response = await campaignsAPI.getById(id);
      const campaign = response.data;
      
      set({ 
        currentCampaign: campaign,
        isLoading: false,
        error: null 
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to fetch campaign';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
    }
  },

  createCampaign: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await campaignsAPI.create(data);
      const newCampaign = response.data;
      
      set((state) => ({ 
        campaigns: [newCampaign, ...state.campaigns],
        isLoading: false,
        error: null 
      }));
      
      toast.success('Campaign created successfully!');
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to create campaign';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      return false;
    }
  },

  updateCampaign: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await campaignsAPI.update(id, data);
      const updatedCampaign = response.data;
      
      set((state) => ({ 
        campaigns: state.campaigns.map(campaign => 
          campaign.id === id ? updatedCampaign : campaign
        ),
        currentCampaign: state.currentCampaign?.id === id ? updatedCampaign : state.currentCampaign,
        isLoading: false,
        error: null 
      }));
      
      toast.success('Campaign updated successfully!');
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to update campaign';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      return false;
    }
  },

  deleteCampaign: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await campaignsAPI.delete(id);
      
      set((state) => ({ 
        campaigns: state.campaigns.filter(campaign => campaign.id !== id),
        currentCampaign: state.currentCampaign?.id === id ? null : state.currentCampaign,
        isLoading: false,
        error: null 
      }));
      
      toast.success('Campaign deleted successfully!');
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to delete campaign';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      return false;
    }
  },

  fetchCampaignTweets: async (id, params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response = await campaignsAPI.getTweets(id, params);
      const { tweets } = response.data;
      
      set({ 
        campaignTweets: tweets,
        isLoading: false,
        error: null 
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to fetch campaign tweets';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
    }
  },

  fetchCampaignPerformance: async (id, days) => {
    set({ isLoading: true, error: null });
    try {
      const response = await campaignsAPI.getPerformance(id, days);
      const performance = response.data;
      
      set({ 
        campaignPerformance: performance,
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

  activateCampaign: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await campaignsAPI.activate(id);
      
      set((state) => ({ 
        campaigns: state.campaigns.map(campaign => 
          campaign.id === id ? { ...campaign, status: 'active' } : campaign
        ),
        currentCampaign: state.currentCampaign?.id === id 
          ? { ...state.currentCampaign, status: 'active' } 
          : state.currentCampaign,
        isLoading: false,
        error: null 
      }));
      
      toast.success('Campaign activated successfully!');
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to activate campaign';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      return false;
    }
  },

  pauseCampaign: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await campaignsAPI.pause(id);
      
      set((state) => ({ 
        campaigns: state.campaigns.map(campaign => 
          campaign.id === id ? { ...campaign, status: 'paused' } : campaign
        ),
        currentCampaign: state.currentCampaign?.id === id 
          ? { ...state.currentCampaign, status: 'paused' } 
          : state.currentCampaign,
        isLoading: false,
        error: null 
      }));
      
      toast.success('Campaign paused successfully!');
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to pause campaign';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      return false;
    }
  },

  clearError: () => {
    set({ error: null });
  },

  setCurrentCampaign: (campaign) => {
    set({ currentCampaign: campaign });
  },
}));