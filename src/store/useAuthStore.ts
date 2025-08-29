import { create } from 'zustand';
import { authAPI, User } from '../services/api';
import { toast } from 'sonner';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (credentials: { email: string; password: string }) => Promise<boolean>;
  register: (userData: { username: string; email: string; password: string }) => Promise<boolean>;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
  getProfile: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<boolean>;
  changePassword: (data: { current_password: string; new_password: string }) => Promise<boolean>;
  testXAPI: (credentials: {
    api_key: string;
    api_secret: string;
    access_token: string;
    access_token_secret: string;
    bearer_token: string;
  }) => Promise<boolean>;
  clearError: () => void;
  checkAuthStatus: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (credentials) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authAPI.login(credentials);
      const { access_token, refresh_token, user } = response.data;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      set({ 
        user, 
        isAuthenticated: true, 
        isLoading: false,
        error: null 
      });
      
      toast.success('Login successful!');
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Login failed';
      set({ 
        error: errorMessage, 
        isLoading: false,
        isAuthenticated: false,
        user: null 
      });
      toast.error(errorMessage);
      return false;
    }
  },

  register: async (userData) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authAPI.register(userData);
      const { access_token, refresh_token, user } = response.data;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      set({ 
        user, 
        isAuthenticated: true, 
        isLoading: false,
        error: null 
      });
      
      toast.success('Registration successful!');
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Registration failed';
      set({ 
        error: errorMessage, 
        isLoading: false,
        isAuthenticated: false,
        user: null 
      });
      toast.error(errorMessage);
      return false;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    // Call logout API to blacklist token
    authAPI.logout().catch(() => {
      // Ignore errors on logout
    });
    
    set({ 
      user: null, 
      isAuthenticated: false, 
      error: null 
    });
    
    toast.success('Logged out successfully');
  },

  refreshToken: async () => {
    try {
      const response = await authAPI.refresh();
      const { access_token } = response.data;
      
      localStorage.setItem('access_token', access_token);
      return true;
    } catch (error) {
      // Refresh failed, logout user
      get().logout();
      return false;
    }
  },

  getProfile: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await authAPI.getProfile();
      const user = response.data;
      
      set({ 
        user, 
        isAuthenticated: true, 
        isLoading: false,
        error: null 
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to fetch profile';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      
      // If unauthorized, logout
      if (error.response?.status === 401) {
        get().logout();
      }
    }
  },

  updateProfile: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authAPI.updateProfile(data);
      const user = response.data;
      
      set({ 
        user, 
        isLoading: false,
        error: null 
      });
      
      toast.success('Profile updated successfully!');
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to update profile';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      return false;
    }
  },

  changePassword: async (data) => {
    set({ isLoading: true, error: null });
    try {
      await authAPI.changePassword(data);
      
      set({ 
        isLoading: false,
        error: null 
      });
      
      toast.success('Password changed successfully!');
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to change password';
      set({ 
        error: errorMessage, 
        isLoading: false 
      });
      toast.error(errorMessage);
      return false;
    }
  },

  testXAPI: async (credentials) => {
    set({ isLoading: true, error: null });
    try {
      await authAPI.testXAPI(credentials);
      
      set({ 
        isLoading: false,
        error: null 
      });
      
      toast.success('X API credentials are valid!');
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'X API test failed';
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

  checkAuthStatus: () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // Get user profile to verify token is still valid
      get().getProfile();
    } else {
      set({ isAuthenticated: false, user: null });
    }
  },
}));