import { configureStore } from '@reduxjs/toolkit';
import userReducer from './userSlice';
import analysisReducer from './slices/analysisSlice';

export const store = configureStore({
  reducer: {
    user: userReducer,
    analysis: analysisReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

export default store;