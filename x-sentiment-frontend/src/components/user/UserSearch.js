import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Search, X, Clock, User, Sparkles, TrendingUp } from 'lucide-react';
import { fetchUserData, clearUserData, clearError } from '../../store/userSlice';
import toast from 'react-hot-toast';

const UserSearch = () => {
  const dispatch = useDispatch();
  const { loading, error, searchHistory = [] } = useSelector((state) => state.user);
  const [username, setUsername] = useState('');
  const [maxTweets, setMaxTweets] = useState(50);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!username.trim()) {
      toast.error('Please enter a username');
      return;
    }

    if (maxTweets < 10) {
      toast.error('Minimum tweets count is 10');
      return;
    }

    // Clear previous error
    dispatch(clearError());

    const cleanUsername = username.trim().replace('@', '');

    // Show loading toast
    const loadingToast = toast.loading('Fetching user data... This may take a moment');

    try {
      const result = await dispatch(fetchUserData({
        username: cleanUsername,
        maxTweets: parseInt(maxTweets)
      }));

      if (result.type === 'user/fetchUserData/fulfilled') {
        toast.success('User data fetched successfully!', { id: loadingToast });
        setUsername('');
      } else {
        toast.error(result.payload || 'Failed to fetch user data', { id: loadingToast });
      }
    } catch (err) {
      toast.error('An unexpected error occurred', { id: loadingToast });
    }
  };

  const handleClear = () => {
    dispatch(clearUserData());
    setUsername('');
  };

  const handleHistoryClick = (historicalUsername) => {
    setUsername(historicalUsername);
  };

  return (
    <div className="card p-8 animate-float">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-gradient-to-r from-slate-500 to-slate-600 rounded-xl">
            <Search className="h-6 w-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold gradient-text">Search X/Twitter User</h2>
            <p className="text-slate-600 text-sm">Analyze sentiment and political classification</p>
          </div>
        </div>
        <button
          onClick={handleClear}
          className="p-3 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-xl transition-all duration-300 hover:scale-110"
          title="Clear data"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl backdrop-blur-sm">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-slate-700 mb-2">
              Search Keyword/Username:
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <User className="h-5 w-5 text-slate-400" />
              </div>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="e.g., #AI, @elonmusk, or a topic"
                className="input-modern w-full pl-12 pr-4"
                disabled={loading}
              />
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Enter a keyword or a Twitter username (e.g., #reactjs, @narendramodi).
            </p>
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-semibold text-slate-700 mb-2">
              Number of Tweets to Analyze:
            </label>
            <div className="relative">
              <input
                type="number"
                value={maxTweets}
                onChange={(e) => setMaxTweets(e.target.value)}
                min="10"
                max="200"
                className="input-modern w-full pr-12"
                disabled={loading}
              />
              <div className="absolute right-4 top-1/2 transform -translate-y-1/2 text-xs text-slate-500 font-medium">
                tweets
              </div>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Analyze between 1 and 200 recent tweets.
            </p>
          </div>
        </div>

        <div className="flex justify-center pt-4">
          <button
            type="submit"
            disabled={loading || !username.trim()}
            className="btn-primary flex items-center space-x-2 px-8 py-4 text-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <TrendingUp className="h-5 w-5" />
                <span>Analyze Sentiment</span>
              </>
            )}
          </button>
        </div>
      </form>

      {loading && (
        <div className="mt-6 p-6 bg-gradient-to-r from-slate-50 to-slate-100 border border-slate-200 rounded-xl">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-slate-600"></div>
            <div>
              <p className="text-slate-700 font-medium">Scraping user data...</p>
              <p className="text-slate-600 text-sm">
                This may take 30-60 seconds depending on the user's activity.
              </p>
            </div>
          </div>
        </div>
      )}

      {searchHistory.length > 0 && (
        <div className="mt-6 p-4 bg-slate-50 rounded-xl">
          <div className="flex items-center space-x-2 mb-3">
            <Clock className="h-4 w-4 text-slate-500" />
            <h3 className="text-sm font-semibold text-slate-700">Recent Searches</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {searchHistory.slice(0, 5).map((historicalUsername, index) => (
              <button
                key={index}
                onClick={() => handleHistoryClick(historicalUsername)}
                className="px-3 py-1 bg-white border border-slate-200 rounded-full text-xs text-slate-600 hover:bg-slate-50 transition-colors"
              >
                {historicalUsername}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default UserSearch;