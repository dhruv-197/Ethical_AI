import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import { MessageCircle, Repeat, Heart, ExternalLink, Calendar, Filter, Image, Play, Sparkles } from 'lucide-react';

const TweetList = () => {
  const { tweets, posts, currentUser } = useSelector((state) => state.user);
  const [filter, setFilter] = useState('all'); // 'all', 'tweets', 'media'

  if (!currentUser) {
    return (
      <div className="card p-8">
        <div className="text-center">
          <Sparkles className="h-16 w-16 mx-auto mb-4 text-slate-300" />
          <p className="text-slate-500 text-lg">No user data available.</p>
        </div>
      </div>
    );
  }

  // Combine and filter tweets
  const getAllContent = () => {
    let content = [];
    
    if (filter === 'all') {
      content = [...tweets];
    } else if (filter === 'tweets') {
      content = tweets.filter(tweet => !tweet.media_urls || tweet.media_urls.length === 0);
    } else if (filter === 'media') {
      content = tweets.filter(tweet => tweet.media_urls && tweet.media_urls.length > 0);
    }
    
    // Sort by date (newest first)
    content.sort((a, b) => new Date(b.posted_at) - new Date(a.posted_at));
    
    return content;
  };

  const content = getAllContent();

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'N/A';
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num?.toString() || '0';
  };

 const renderMediaGrid = (mediaUrls) => {
  const mediaCount = mediaUrls.length;
  const imageBaseClass = "w-full object-cover rounded-lg bg-white";
  const errorHandler = (e) => (e.target.style.display = "none");

  if (mediaCount === 1) {
    return (
      <div className="mt-3 rounded-xl overflow-hidden border border-slate-200">
        <img
          src={mediaUrls[0]}
          alt="media"
          className="w-full h-auto object-contain rounded-xl"
          onError={errorHandler}
        />
      </div>
    );
  }

  if (mediaCount === 2) {
    return (
      <div className="mt-3 grid grid-cols-2 gap-2 rounded-xl overflow-hidden">
        {mediaUrls.map((url, index) => (
          <img
            key={index}
            src={url}
            alt={`media-${index}`}
            className={`${imageBaseClass} aspect-[4/5]`}
            onError={errorHandler}
          />
        ))}
      </div>
    );
  }

 if (mediaCount === 3) {
  return (
    <div className="mt-3 grid grid-cols-2 gap-2 rounded-xl overflow-hidden h-[400px]">
      <div className="grid grid-rows-2 gap-2">
        {mediaUrls.slice(0, 2).map((url, index) => (
          <img
            key={index}
            src={url}
            alt={`media-${index}`}
            className={`${imageBaseClass} w-full h-full object-cover`}
            onError={errorHandler}
          />
        ))}
      </div>
      <img
        src={mediaUrls[2]}
        alt="media-2"
        className={`${imageBaseClass} w-full h-full object-cover`}
        onError={errorHandler}
      />
    </div>
  );
}

  return (
    <div className="mt-3 grid grid-cols-2 gap-2 rounded-xl overflow-hidden">
      {mediaUrls.slice(0, 4).map((url, index) => (
        <div key={index} className="relative">
          <img
            src={url}
            alt={`media-${index}`}
            className={`${imageBaseClass} aspect-square`}
            onError={errorHandler}
          />
          {index === 3 && mediaCount > 4 && (
            <div className="absolute inset-0 bg-black bg-opacity-60 flex items-center justify-center rounded-lg">
              <span className="text-white text-lg font-semibold">+{mediaCount - 4}</span>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

  return (
    <div className="card w-full max-w-4xl mx-auto">
      {/* Header */}
      <div className="p-8 border-b border-slate-100">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-gradient-to-r from-slate-500 to-slate-600 rounded-xl">
              <MessageCircle className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold gradient-text">
                {currentUser.name}'s Posts
              </h2>
              <p className="text-slate-600 text-sm">
                {content.length} {filter === 'media' ? 'media posts' : 'posts'} found
              </p>
            </div>
          </div>
        </div>
        
        {/* Filters */}
        <div className="flex flex-wrap gap-3">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="input-modern px-6 py-3 text-sm font-medium focus:ring-2 focus:ring-slate-500 focus:border-transparent"
          >
            <option value="all">All Posts</option>
            <option value="tweets">Text Only</option>
            <option value="media">With Media</option>
          </select>
        </div>
      </div>

      {/* Content List */}
      <div className="max-h-[600px] overflow-y-auto">
        {content.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            <MessageCircle className="h-16 w-16 mx-auto mb-4 text-slate-300" />
            <p className="text-lg font-medium">No {filter === 'media' ? 'media posts' : 'posts'} found</p>
            <p className="text-sm mt-1">Try adjusting your filter or check back later</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {content.map((item, index) => (
              <div key={item.tweet_id || index} className="p-6 hover:bg-slate-50/50 transition-all duration-300">
                {/* Tweet Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-4">
                    <img
                      src={currentUser.profile_image_url || '/default-avatar.png'}
                      alt={currentUser.name}
                      className="w-12 h-12 rounded-full border-2 border-slate-100 shadow-md"
                    />
                    <div>
                      <div className="flex items-center space-x-2">
                        <p className="font-bold text-slate-900">{currentUser.name}</p>
                        {currentUser.verified && (
                          <div className="w-5 h-5 bg-slate-500 rounded-full flex items-center justify-center">
                            <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          </div>
                        )}
                      </div>
                      <p className="text-sm text-slate-500">@{currentUser.username}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-slate-500 bg-slate-50 px-3 py-1 rounded-full">
                    <Calendar className="h-4 w-4" />
                    <span>{formatDate(item.posted_at)}</span>
                  </div>
                </div>

                {/* Tweet Content */}
                <div className="mb-4 ml-16">
                  <p className="text-slate-900 leading-relaxed text-[15px] mb-4">{item.text}</p>
                  
                  {/* Media */}
                  {item.media_urls && item.media_urls.length > 0 && (
                     <div className="max-w-full">
                      {renderMediaGrid(item.media_urls)}
                    </div>
                  )}
                  
                  {/* Hashtags */}
                  {item.hashtags && (
                    <div className="mt-4 flex flex-wrap gap-2">
                      {(Array.isArray(item.hashtags) ? item.hashtags : 
                        typeof item.hashtags === 'string' ? 
                          (item.hashtags.startsWith('[') ? JSON.parse(item.hashtags) : []) : 
                          []
                      ).map((hashtag, hashIndex) => (
                        <span
                          key={hashIndex}
                          className="text-slate-600 text-sm hover:underline cursor-pointer font-medium bg-slate-50 px-3 py-1 rounded-full"
                        >
                          {hashtag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Engagement Stats */}
                <div className="flex items-center justify-between ml-16">
                  <div className="flex items-center space-x-8 text-sm text-slate-500">
                    <button className="flex items-center space-x-2 hover:text-slate-700 transition-colors group">
                      <div className="p-2 rounded-full group-hover:bg-slate-50 transition-colors">
                        <MessageCircle className="h-4 w-4" />
                      </div>
                      <span className="font-medium">{formatNumber(item.reply_count || 0)}</span>
                    </button>
                    <button className="flex items-center space-x-2 hover:text-slate-700 transition-colors group">
                      <div className="p-2 rounded-full group-hover:bg-slate-50 transition-colors">
                        <Repeat className="h-4 w-4" />
                      </div>
                      <span className="font-medium">{formatNumber(item.retweet_count || 0)}</span>
                    </button>
                    <button className="flex items-center space-x-2 hover:text-slate-700 transition-colors group">
                      <div className="p-2 rounded-full group-hover:bg-slate-50 transition-colors">
                        <Heart className="h-4 w-4" />
                      </div>
                      <span className="font-medium">{formatNumber(item.like_count || 0)}</span>
                    </button>
                  </div>
                  
                  <a
                    href={`https://twitter.com/${currentUser.username}/status/${item.tweet_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center space-x-2 text-slate-400 hover:text-slate-600 transition-colors"
                  >
                    <ExternalLink className="h-4 w-4" />
                    <span className="text-sm">View on X</span>
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TweetList;