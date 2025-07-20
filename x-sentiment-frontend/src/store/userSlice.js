  import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
  import { apiService } from '../services/api';

  // Async thunk for fetching user data
  export const fetchUserData = createAsyncThunk(
    'user/fetchUserData',
    async ({ username, maxTweets = 50 },{ rejectWithValue }) => {
      try {
        const response = await apiService.getUserInfo(username,maxTweets);
        return response.data;
      } catch (error) {
        return rejectWithValue(
          error.response?.data?.error || 
          error.message || 
          'Failed to fetch user data'
        );
      }
    }
  );

  export const fetchUserProfile = createAsyncThunk(
    'user/fetchUserProfile',
    async (username, { rejectWithValue }) => {
      try {
        const response = await apiService.getUserProfile(username);
        return response.data;
      } catch (error) {
        return rejectWithValue(error.response?.data || error.message);
      }
    }
  );

  // Async thunk for fetching tweets only
  export const fetchUserTweets = createAsyncThunk(
    'user/fetchUserTweets',
    async ({ username, maxTweets = 50 }, { rejectWithValue }) => {
      try {
        const response = await apiService.getUserTweets(username, maxTweets);
        return response.data;
      } catch (error) {
        return rejectWithValue(
          error.response?.data?.error || 
          error.message || 
          'Failed to fetch tweets'
        );
      }
    }
  );

  // Async thunk for fetching posts only
  export const fetchUserPosts = createAsyncThunk(
    'user/fetchUserPosts',
    async ({ username, maxPosts = 20 }, { rejectWithValue }) => {
      try {
        const response = await apiService.getUserPosts(username, maxPosts);
        return response.data;
      } catch (error) {
        return rejectWithValue(
          error.response?.data?.error || 
          error.message || 
          'Failed to fetch posts'
        );
      }
    }
  );

  const initialState = {
    currentUser: null,
    tweets: [],
    posts: [],
    loading: false,
    error: null,
    searchHistory: [], // ADD THIS LINE
  };

  const userSlice = createSlice({
    name: 'user',
    initialState,
    reducers: {
      setCurrentUser: (state, action) => {
        state.currentUser = action.payload;
      },
      setTweets: (state, action) => {
        state.tweets = action.payload;
      },
      clearError: (state) => {
        state.error = null;
      },
      setPosts: (state, action) => {
        state.posts = action.payload;
      },
      clearUserData: (state) => {
        state.currentUser = null;
        state.tweets = [];
        state.posts = [];
        state.error = null;
      },
      // Add action to add to search history
      addToSearchHistory: (state, action) => {
        const username = action.payload;
        if (!state.searchHistory.includes(username)) {
          state.searchHistory.unshift(username);
          if (state.searchHistory.length > 10) {
            state.searchHistory.pop();
          }
        }
      },
      // Add action to clear search history
      clearSearchHistory: (state) => {
        state.searchHistory = [];
      },
    },
    extraReducers: (builder) => {
      builder
        // Fetch user data
        .addCase(fetchUserData.pending, (state) => {
          state.loading = true;
          state.error = null;
        })
        .addCase(fetchUserData.fulfilled, (state, action) => {
          state.loading = false;
          state.currentUser = action.payload.user;
          state.tweets = action.payload.tweets || [];
          state.posts = action.payload.posts || [];
          state.error = null;
          
          // Add to search history
          if (state.currentUser) {
            const username = state.currentUser.username;
            if (!state.searchHistory.includes(username)) {
              state.searchHistory.unshift(username);
              if (state.searchHistory.length > 10) {
                state.searchHistory.pop();
              }
            }
          }
        })
        .addCase(fetchUserData.rejected, (state, action) => {
          state.loading = false;
          state.error = action.payload;
        })
        
        // Fetch tweets
        .addCase(fetchUserTweets.pending, (state) => {
          state.loading = true;
          state.error = null;
        })
        .addCase(fetchUserTweets.fulfilled, (state, action) => {
          state.loading = false;
          state.tweets = action.payload.tweets || [];
          state.error = null;
        })
        .addCase(fetchUserTweets.rejected, (state, action) => {
          state.loading = false;
          state.error = action.payload;
        })
        
        // Fetch posts
        .addCase(fetchUserPosts.pending, (state) => {
          state.loading = true;
          state.error = null;
        })
        .addCase(fetchUserPosts.fulfilled, (state, action) => {
          state.loading = false;
          state.posts = action.payload.posts || [];
          state.error = null;
        })
        .addCase(fetchUserPosts.rejected, (state, action) => {
          state.loading = false;
          state.error = action.payload;
        })
        
        // Fetch user profile
        .addCase(fetchUserProfile.pending, (state) => {
          state.loading = true;
          state.error = null;
        })
        .addCase(fetchUserProfile.fulfilled, (state, action) => {
          state.loading = false;
          state.currentUser = action.payload;
          state.tweets = action.payload.tweets || [];
          state.posts = action.payload.posts || [];
          
          // Add to search history
          if (action.payload.username) {
            const username = action.payload.username;
            if (!state.searchHistory.includes(username)) {
              state.searchHistory.unshift(username);
              if (state.searchHistory.length > 10) {
                state.searchHistory.pop();
              }
            }
          }
        })
        .addCase(fetchUserProfile.rejected, (state, action) => {
          state.loading = false;
          state.error = action.payload;
        });
    },
  });

  export const { 
    setCurrentUser, 
    setTweets, 
    setPosts, 
    clearUserData, 
    clearError,
    addToSearchHistory,
    clearSearchHistory 
  } = userSlice.actions;

  export default userSlice.reducer;