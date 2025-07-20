import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { Calendar, MapPin, Link as LinkIcon, Users, MessageCircle, BarChart3, TrendingUp, Sparkles } from 'lucide-react';

const UserProfile = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { currentUser, tweets, posts } = useSelector((state) => state.user);

  const handleAnalyzeProfile = () => {
    navigate('/analysis');
  };

  if (!currentUser) return null;

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  return (
    <div className="card overflow-hidden w-full max-w-4xl mx-auto">
      {/* Cover Photo */}
      <div className="relative h-48 bg-gradient-to-r from-slate-400 via-slate-500 to-slate-600">
        {currentUser.banner_image_url && (
          <img
            src={currentUser.banner_image_url}
            alt="Banner"
            className="absolute inset-0 w-full h-full object-cover"
            style={{ zIndex: 1 }}
          />
        )}
        <div className="absolute inset-0 bg-black/20" style={{ zIndex: 2 }}></div>
        
        {/* Profile image positioned over banner */}
        <div className="absolute left-8 -bottom-16 z-30">
          <div className="relative">
            <img
              src={currentUser.profile_image_url || '/default-avatar.png'}
              alt={currentUser.name}
              className="w-32 h-32 rounded-full border-4 border-white shadow-2xl"
            />
            <div className="absolute -top-2 -right-2 p-2 bg-gradient-to-r from-slate-500 to-slate-600 rounded-full">
              <Sparkles className="h-4 w-4 text-white" />
            </div>
          </div>
        </div>
      </div>

      {/* Profile Info */}
      <div className="px-8 pb-8 pt-20">
        <div className="flex items-start justify-between">
          <div className="flex items-end space-x-4">
            <div className="pb-2">
              <h2 className="text-2xl font-bold gradient-text">{currentUser.name}</h2>
              <p className="text-slate-600 text-lg">@{currentUser.username}</p>
            </div>
          </div>
          {/* Action Buttons */}
          <div className="flex space-x-3 mt-4">
            <button
              onClick={handleAnalyzeProfile}
              className="btn-primary flex items-center space-x-2 px-6 py-3"
            >
              <TrendingUp className="h-5 w-5" />
              <span>Analyze Profile</span>
            </button>
          </div>
        </div>

        {/* Bio */}
        {currentUser.description && (
          <div className="mt-6 p-4 bg-slate-50 rounded-xl">
            <p className="text-slate-700 leading-relaxed">{currentUser.description}</p>
          </div>
        )}

        {/* Profile Details */}
        <div className="mt-6 flex flex-wrap items-center gap-6 text-sm text-slate-600">
          {currentUser.location && (
            <div className="flex items-center space-x-2 p-2 bg-slate-50 rounded-lg">
              <MapPin className="h-4 w-4 text-slate-500" />
              <span>{currentUser.location}</span>
            </div>
          )}

          {currentUser.url && (
            <div className="flex items-center space-x-2 p-2 bg-slate-50 rounded-lg">
              <LinkIcon className="h-4 w-4 text-slate-500" />
              <a
                href={currentUser.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-600 hover:underline"
              >
                {currentUser.url}
              </a>
            </div>
          )}

          {currentUser.created_at && (
            <div className="flex items-center space-x-2 p-2 bg-slate-50 rounded-lg">
              <Calendar className="h-4 w-4 text-slate-500" />
              <span>Joined {formatDate(currentUser.joined_date)}</span>
            </div>
          )}
        </div>

        {/* Stats */}
        <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="text-center p-4 bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl border border-slate-200">
            <div className="text-2xl font-bold gradient-text">
              {formatNumber(currentUser.followers_count || 0)}
            </div>
            <div className="text-sm text-slate-600 font-medium">Followers</div>
          </div>

          <div className="text-center p-4 bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl border border-slate-200">
            <div className="text-2xl font-bold text-slate-600">
              {formatNumber(currentUser.following_count || 0)}
            </div>
            <div className="text-sm text-slate-600 font-medium">Following</div>
          </div>

          <div className="text-center p-4 bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl border border-slate-200">
            <div className="text-2xl font-bold text-slate-600">
              {tweets.length}
            </div>
            <div className="text-sm text-slate-600 font-medium">Tweets</div>
          </div>

          <div className="text-center p-4 bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl border border-slate-200">
            <div className="text-2xl font-bold text-slate-600">
              {posts.length}
            </div>
            <div className="text-sm text-slate-600 font-medium">Posts</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;