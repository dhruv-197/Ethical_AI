import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import Layout from '../components/common/Layout';
import { apiService } from '../services/api';
import { setCurrentUser, setTweets, setPosts } from '../store/userSlice'; // Import actions
import { Trash2 } from 'lucide-react';
import { 
  Users as UsersIcon, 
  Search, 
  Filter, 
  Calendar, 
  UserCheck, 
  Eye, 
  MessageCircle, 
  Image,
  ChevronLeft,
  ChevronRight,
  SortAsc,
  SortDesc
} from 'lucide-react';
import toast from 'react-hot-toast';

const Users = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingProfile, setLoadingProfile] = useState(null); // Track which profile is loading
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 10,
    total: 0,
    pages: 0,
    has_next: false,
    has_prev: false
  });
  
  const [filters, setFilters] = useState({
    search: '',
    sort_by: 'created_at',
    sort_order: 'desc'
  });

  // Fetch users from API (only user info)
  const fetchUsers = async (page = 1) => {
    try {
      setLoading(true);
      const response = await apiService.getUserProfiles({
        page,
        per_page: pagination.per_page,
        search: filters.search,
        sort_by: filters.sort_by,
        sort_order: filters.sort_order
      });
      
      if (response.data.success) {
        setUsers(response.data.users);
        setPagination(response.data.pagination);
      }
    } catch (error) {
      toast.error('Failed to fetch users');
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchUsers(1);
  }, [filters]);

  const handleDeleteUser = async (username) => {
  if (!window.confirm(`Are you sure you want to delete @${username}? This action cannot be undone.`)) {
    return;
  }

  try {
    await apiService.deleteUserProfile(username);
    
    toast.success(`User @${username} deleted successfully`);
    
    // Refresh users
    fetchUsers(pagination.page);
  } catch (error) {
    toast.error(`Failed to delete @${username}`);
    console.error('Error deleting user:', error);
  }
};

  // Handle user click - fetch profile with tweets and navigate
  const handleUserClick = async (username) => {
    try {
      setLoadingProfile(username);
      const loadingToast = toast.loading('Loading user profile...');
      
      // Call the new API endpoint to get user profile with tweets
      const response = await apiService.getUserProfile(username);
      
      if (response.data.success) {
        // Update Redux store with user data and tweets
        dispatch(setCurrentUser(response.data));
        dispatch(setTweets(response.data.tweets || []));
        dispatch(setPosts(response.data.posts || []));
        
        toast.success('Profile loaded!', { id: loadingToast });
        navigate('/profile');
      } else {
        throw new Error('Failed to load profile');
      }
    } catch (error) {
      toast.error('Failed to load profile');
      console.error('Error loading profile:', error);
    } finally {
      setLoadingProfile(null);
    }
  };

  // Handle search
  const handleSearch = (e) => {
    e.preventDefault();
    fetchUsers(1);
  };

  // Handle sort change
  const handleSortChange = (sortBy) => {
    setFilters(prev => ({
      ...prev,
      sort_by: sortBy,
      sort_order: prev.sort_by === sortBy && prev.sort_order === 'desc' ? 'asc' : 'desc'
    }));
  };

  // Handle pagination
  const handlePageChange = (newPage) => {
    fetchUsers(newPage);
  };

  // Format numbers
  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num?.toString() || '0';
  };

  // Format date
  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
    } catch {
      return 'N/A';
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <UsersIcon className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">All Users</h1>
                <p className="text-sm text-gray-500">
                  {pagination.total} users found
                </p>
              </div>
            </div>
          </div>

          {/* Search and Filters - same as before */}
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <form onSubmit={(e) => { e.preventDefault(); fetchUsers(1); }} className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <input
                  type="text"
                  placeholder="Search users by name or username..."
                  value={filters.search}
                  onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </form>

            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-gray-400" />
              <select
                value={filters.sort_by}
                onChange={(e) => setFilters(prev => ({ ...prev, sort_by: e.target.value }))}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="created_at">Date Added</option>
                <option value="followers_count">Followers</option>
                <option value="following_count">Following</option>
                <option value="tweets_count">Tweets</option>
                <option value="last_scraped">Last Scraped</option>
              </select>
              
              <button
                onClick={() => setFilters(prev => ({ 
                  ...prev, 
                  sort_order: prev.sort_order === 'desc' ? 'asc' : 'desc' 
                }))}
                className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                {filters.sort_order === 'desc' ? 
                  <SortDesc className="h-4 w-4" /> : 
                  <SortAsc className="h-4 w-4" />
                }
              </button>
            </div>
          </div>
        </div>

        {/* Users Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, index) => (
              <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 animate-pulse">
                <div className="flex items-center space-x-4 mb-4">
                  <div className="w-16 h-16 bg-gray-300 rounded-full"></div>
                  <div className="flex-1">
                    <div className="h-4 bg-gray-300 rounded mb-2"></div>
                    <div className="h-3 bg-gray-300 rounded w-3/4"></div>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="h-3 bg-gray-300 rounded"></div>
                  <div className="h-3 bg-gray-300 rounded w-2/3"></div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {users.map((user) => (
              <div
                key={user.id}
                onClick={() => handleUserClick(user.username)}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md hover:border-blue-200 transition-all cursor-pointer group relative"
              >
                {/* Loading overlay */}
                {loadingProfile === user.username && (
                  <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center rounded-lg">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  </div>
                )}

                {/* User Header */}
                <div className="flex items-center space-x-4 mb-4">
                  <img
                    src={user.profile_image_url || '/default-avatar.png'}
                    alt={user.name}
                    className="w-16 h-16 rounded-full border-2 border-gray-100 group-hover:border-blue-200 transition-colors"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-semibold text-gray-900 truncate">
                        {user.name || user.username}
                      </h3>
                      {user.verified && (
                        <UserCheck className="h-4 w-4 text-blue-500" />
                      )}
                    </div>
                    <p className="text-sm text-gray-500">@{user.username}</p>
                  </div>
                </div>

                {/* Bio */}
                {user.bio && (
                  <p className="text-sm text-gray-700 mb-4 line-clamp-2">
                    {user.bio}
                  </p>
                )}

                {/* Location */}
                {user.location && (
                  <p className="text-sm text-gray-500 mb-4">📍 {user.location}</p>
                )}

                {/* Stats */}
                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="text-center">
                    <p className="text-lg font-semibold text-gray-900">
                      {formatNumber(user.followers_count)}
                    </p>
                    <p className="text-xs text-gray-500">Followers</p>
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-semibold text-gray-900">
                      {formatNumber(user.following_count)}
                    </p>
                    <p className="text-xs text-gray-500">Following</p>
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-semibold text-gray-900">
                      {formatNumber(user.tweets_count)}
                    </p>
                    <p className="text-xs text-gray-500">Tweets</p>
                  </div>
                </div>

                {/* Scraped Tweets Count */}
                <div className="flex items-center justify-between mb-4 p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <MessageCircle className="h-4 w-4 text-blue-500" />
                    <span className="text-sm text-gray-700">
                      {user.scraped_tweets_count || 0} tweets scraped
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Image className="h-4 w-4 text-green-500" />
                    <span className="text-sm text-gray-700">
                      {user.scraped_media_count || 0} with media
                    </span>
                  </div>
                </div>
               
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteUser(user.username);
                }}
                className="flex items-center space-x-1 text-red-500 text-xs hover:underline"
              >
                <Trash2 className="h-3 w-3" />
                <span>Delete</span>
              </button>

                {/* Footer */}
                <div className="flex items-center justify-between text-xs text-gray-500 pt-4 border-t border-gray-100">
                  <div className="flex items-center space-x-1">
                    <Calendar className="h-3 w-3" />
                    <span>Added {formatDate(user.created_at)}</span>
                  </div>
                  <div className="flex items-center space-x-1 text-blue-600 group-hover:text-blue-700">
                    <Eye className="h-3 w-3" />
                    <span>View Profile</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination and Empty State remain the same */}
        {/* ... rest of the component ... */}
      </div>
    </Layout>
  );
};

export default Users;