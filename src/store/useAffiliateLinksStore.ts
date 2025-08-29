import { create } from 'zustand';
import { affiliateLinksAPI, AffiliateLink } from '../services/api';
import { toast } from 'sonner';

interface AffiliateLinksState {
  affiliateLinks: AffiliateLink[];
  currentAffiliateLink: AffiliateLink | null;
  categories: string[];
  isLoading: boolean;
  error: string | null;
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
  
  // Actions
  fetchAffiliateLinks: (params?: {
    page?: number;
    per_page?: number;
    category?: string;
    active?: boolean;
    search?: string;
  }) => Promise<void>;
  fetchAffiliateLinkById: (id: number) => Promise<void>;
  createAffiliateLink: (data: Omit<AffiliateLink, 'id' | 'created_at'>) => Promise<boolean>;
  updateAffiliateLink: (id: number, data: Partial<AffiliateLink>) => Promise<boolean>;
  deleteAffiliateLink: (id: number) => Promise<boolean>;
  toggleAffiliateLinkStatus: (id: number) => Promise<boolean>;
  fetchAffiliateLinkPerformance: (id: number, days?: number) => Promise<any>;
  fetchCategories: () => Promise<void>;
  searchAffiliateLinks: (params: {
    query?: string;
    category?: string;
    min_commission?: number;
    max_commission?: number;
    brand?: string;
    active?: boolean;
  }) => Promise<void>;
  bulkImportAffiliateLinks: (data: {
    links: Array<Omit<AffiliateLink, 'id' | 'created_at'>>;
  }) => Promise<{ created: number; failed: number }>;
  clearError: () => void;
  setCurrentAffiliateLink: (link: AffiliateLink | null) => void;
}

export const useAffiliateLinksStore = create<AffiliateLinksState>((set) => ({
  affiliateLinks: [],
  currentAffiliateLink: null,
  categories: [],
  isLoading: false,
  error: null,
  pagination: {
    page: 1,
    per_page: 10,
    total: 0,
    pages: 0,
  },

  fetchAffiliateLinks: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response = await affiliateLinksAPI.getAll(params);
      const { affiliate_links, pagination } = response.data;
      
      set({ 
        affiliateLinks: affiliate_links,
        pagination,
        isLoading: false,
        error: null 
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to fetch affiliate links';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
    }
  },

  fetchAffiliateLinkById: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const response = await affiliateLinksAPI.getById(id);
      const affiliateLink = response.data;
      
      set({ 
        currentAffiliateLink: affiliateLink,
        isLoading: false,
        error: null 
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to fetch affiliate link';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
    }
  },

  createAffiliateLink: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await affiliateLinksAPI.create(data);
      const newAffiliateLink = response.data;
      
      set((state) => ({ 
        affiliateLinks: [newAffiliateLink, ...state.affiliateLinks],
        isLoading: false,
        error: null 
      }));
      
      toast.success('Affiliate link created successfully!');
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to create affiliate link';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      return false;
    }
  },

  updateAffiliateLink: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await affiliateLinksAPI.update(id, data);
      const updatedAffiliateLink = response.data;
      
      set((state) => ({ 
        affiliateLinks: state.affiliateLinks.map(link => 
          link.id === id ? updatedAffiliateLink : link
        ),
        currentAffiliateLink: state.currentAffiliateLink?.id === id ? updatedAffiliateLink : state.currentAffiliateLink,
        isLoading: false,
        error: null 
      }));
      
      toast.success('Affiliate link updated successfully!');
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to update affiliate link';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      return false;
    }
  },

  deleteAffiliateLink: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await affiliateLinksAPI.delete(id);
      
      set((state) => ({ 
        affiliateLinks: state.affiliateLinks.filter(link => link.id !== id),
        currentAffiliateLink: state.currentAffiliateLink?.id === id ? null : state.currentAffiliateLink,
        isLoading: false,
        error: null 
      }));
      
      toast.success('Affiliate link deleted successfully!');
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to delete affiliate link';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      return false;
    }
  },

  toggleAffiliateLinkStatus: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const response = await affiliateLinksAPI.toggleActive(id);
      const updatedAffiliateLink = response.data;
      
      set((state) => ({ 
        affiliateLinks: state.affiliateLinks.map(link => 
          link.id === id ? updatedAffiliateLink : link
        ),
        currentAffiliateLink: state.currentAffiliateLink?.id === id ? updatedAffiliateLink : state.currentAffiliateLink,
        isLoading: false,
        error: null 
      }));
      
      const status = updatedAffiliateLink.is_active ? 'activated' : 'deactivated';
      toast.success(`Affiliate link ${status} successfully!`);
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to toggle affiliate link status';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      return false;
    }
  },

  fetchAffiliateLinkPerformance: async (id, days = 30) => {
    set({ isLoading: true, error: null });
    try {
      const response = await affiliateLinksAPI.getPerformance(id, days);
      const performance = response.data;
      
      set({ 
        isLoading: false,
        error: null 
      });
      
      return performance;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to fetch affiliate link performance';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      throw error;
    }
  },

  fetchCategories: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await affiliateLinksAPI.getCategories();
      const categories = response.data;
      
      set({ 
        categories,
        isLoading: false,
        error: null 
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to fetch categories';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
    }
  },

  searchAffiliateLinks: async (params) => {
    set({ isLoading: true, error: null });
    try {
      const response = await affiliateLinksAPI.search(params);
      const { affiliate_links, pagination } = response.data;
      
      set({ 
        affiliateLinks: affiliate_links,
        pagination,
        isLoading: false,
        error: null 
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to search affiliate links';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
    }
  },

  bulkImportAffiliateLinks: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await affiliateLinksAPI.bulkImport(data);
      const { created, failed, results } = response.data;
      
      // Add successfully created affiliate links to the store
      const successfulLinks = results.filter((result: any) => result.success).map((result: any) => result.affiliate_link);
      
      set((state) => ({ 
        affiliateLinks: [...successfulLinks, ...state.affiliateLinks],
        isLoading: false,
        error: null 
      }));
      
      if (created > 0) {
        toast.success(`${created} affiliate links imported successfully!`);
      }
      if (failed > 0) {
        toast.error(`${failed} affiliate links failed to import`);
      }
      
      return { created, failed };
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to bulk import affiliate links';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      return { created: 0, failed: data.links.length };
    }
  },

  clearError: () => {
    set({ error: null });
  },

  setCurrentAffiliateLink: (link) => {
    set({ currentAffiliateLink: link });
  },
}));