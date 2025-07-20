import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import Layout from '../components/common/Layout';
import UserProfile from '../components/user/UserProfile';
import TweetList from '../components/user/TweetList';
import { fetchUserTweets, fetchUserPosts } from '../store/userSlice';
import { MessageCircle, Image, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';

const Profile = () => {
  const dispatch = useDispatch();
  const { currentUser, tweets, posts } = useSelector((state) => state.user);
  const [refreshing, setRefreshing] = useState(false);

  const handleRefreshTweets = async () => {
    if (!currentUser) return;
    
    setRefreshing(true);
    const loadingToast = toast.loading('Refreshing tweets...');
    
    try {
      await dispatch(fetchUserTweets({ 
        username: currentUser.username, 
        maxTweets: 50 
      })).unwrap();
      toast.success('Tweets refreshed!', { id: loadingToast });
    } catch (error) {
      toast.error('Failed to refresh tweets', { id: loadingToast });
    } finally {
      setRefreshing(false);
    }
  };

  const handleRefreshPosts = async () => {
    if (!currentUser) return;
    
    setRefreshing(true);
    const loadingToast = toast.loading('Refreshing posts...');
    
    try {
      await dispatch(fetchUserPosts({ 
        username: currentUser.username, 
        maxPosts: 20 
      })).unwrap();
      toast.success('Posts refreshed!', { id: loadingToast });
    } catch (error) {
      toast.error('Failed to refresh posts', { id: loadingToast });
    } finally {
      setRefreshing(false);
    }
  };

  if (!currentUser) {
    return (
      <Layout>
        <div className="bg-white rounded-lg shadow-md p-6">
          <p className="text-gray-500 text-center">
            No user profile loaded. Please search for a user from the{' '}
            <a href="/" className="text-blue-600 hover:underline">Home page</a>.
          </p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <UserProfile />
        
        {/* Action Buttons */}
        <div className="bg-white rounded-lg shadow-md p-6 w-[50%] mx-auto">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Content Actions</h3>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleRefreshTweets}
              disabled={refreshing}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh Tweets</span>
            </button>
            
            <button
              onClick={handleRefreshPosts}
              disabled={refreshing}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors"
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh Posts</span>
            </button>
          </div>
        </div>

        {/* Content Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-[50%] mx-auto">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Tweets</h3>
              <MessageCircle className="h-6 w-6 text-blue-500" />
            </div>
            <p className="text-3xl font-bold text-blue-600">{tweets.length}</p>
            <p className="text-sm text-gray-600">Total tweets scraped</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Media Posts</h3>
              <Image className="h-6 w-6 text-green-500" />
            </div>
            <p className="text-3xl font-bold text-green-600">{posts.length}</p>
            <p className="text-sm text-gray-600">Posts with media</p>
          </div>
        </div>

        {/* Tweet List */}
        {tweets.length > 0 && <TweetList />}
      </div>
    </Layout>
  );
};

export default Profile;