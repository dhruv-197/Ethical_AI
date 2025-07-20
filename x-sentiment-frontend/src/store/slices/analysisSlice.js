import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { apiService } from '../../services/api';

// Async thunk for analyzing user profile
export const analyzeUserProfile = createAsyncThunk(
  'analysis/analyzeProfile',
  async ({ username, image_model, text_model,fusion_technique,alpha }, { rejectWithValue }) => {
    try {
      const response = await apiService.analyzeUserProfile(username, image_model, text_model,fusion_technique,alpha);
      return response.data;
    } catch (error) {
      return rejectWithValue(
        error.response?.data?.error || 'Failed to analyze profile'
      );
    }
  }
);

// Async thunk for refreshing user data
export const refreshUserData = createAsyncThunk(
  'analysis/refreshUserData',
  async (username, { rejectWithValue }) => {
    try {
      const response = await apiService.refreshUserData(username);
      return response.data;
    } catch (error) {
      return rejectWithValue(
        error.response?.data?.error || 'Failed to refresh user data'
      );
    }
  }
);

const analysisSlice = createSlice({
  name: 'analysis',
  initialState: {
    currentAnalysis: null,
    loading: false,
    error: null,
    analysisHistory: [],
    refreshing: false,
    refreshError: null
  },
  reducers: {
    clearAnalysis: (state) => {
      state.currentAnalysis = null;
      state.error = null;
    },
    clearError: (state) => {
      state.error = null;
      state.refreshError = null;
    },
    clearHistory: (state) => {
      state.analysisHistory = [];
    },
    removeAnalysisFromHistory: (state, action) => {
      state.analysisHistory = state.analysisHistory.filter(
        (analysis) => analysis.username !== action.payload
      );
    }
  },
  extraReducers: (builder) => {
    builder
      // Analyze user profile
      .addCase(analyzeUserProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(analyzeUserProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.currentAnalysis = action.payload;
        
        // Add to history if not already exists
        const existingIndex = state.analysisHistory.findIndex(
          item => item.username === action.payload.username
        );
        
        if (existingIndex >= 0) {
          state.analysisHistory[existingIndex] = action.payload;
        } else {
          state.analysisHistory.push(action.payload);
        }
        
        state.error = null;
      })
      .addCase(analyzeUserProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Refresh user data
      .addCase(refreshUserData.pending, (state) => {
        state.refreshing = true;
        state.refreshError = null;
      })
      .addCase(refreshUserData.fulfilled, (state, action) => {
        state.refreshing = false;
        state.refreshError = null;
        // Data refresh successful, can trigger new analysis
      })
      .addCase(refreshUserData.rejected, (state, action) => {
        state.refreshing = false;
        state.refreshError = action.payload;
      });
  }
});

export const { 
  clearAnalysis, 
  clearError, 
  clearHistory, 
  removeAnalysisFromHistory 
} = analysisSlice.actions;

export default analysisSlice.reducer;