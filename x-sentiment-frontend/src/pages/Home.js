import React from 'react';
import Layout from '../components/common/Layout';
import UserSearch from '../components/user/UserSearch';
import UserProfile from '../components/user/UserProfile';
import TweetList from '../components/user/TweetList';
import { useSelector } from 'react-redux';
import { Shield, Heart, Users, Globe } from 'lucide-react';

const Home = () => {
  const { currentUser, loading, tweets, posts } = useSelector((state) => state.user);

  return (
    <Layout>
      <div className="space-y-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-4">
            PostPatrol - Ethical AI for Social Justice
          </h1>
          <p className="text-lg text-slate-600 max-w-3xl mx-auto mb-6">
            Analyze political sentiment and classify users as radical, non-radical, or politician 
            while promoting social justice, reducing biases, and supporting marginalized communities 
            through ethical AI practices.
          </p>
          
          {/* Social Justice Features */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-8">
            <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
              <div className="flex items-center justify-center mb-3">
                <Shield className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="font-semibold text-blue-800 text-sm">Bias Detection</h3>
              <p className="text-xs text-blue-700 mt-1">Monitor AI fairness</p>
            </div>
            
            <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-200">
              <div className="flex items-center justify-center mb-3">
                <Heart className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="font-semibold text-green-800 text-sm">Social Justice</h3>
              <p className="text-xs text-green-700 mt-1">Support marginalized groups</p>
            </div>
            
            <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-200">
              <div className="flex items-center justify-center mb-3">
                <Users className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="font-semibold text-purple-800 text-sm">Community Outreach</h3>
              <p className="text-xs text-purple-700 mt-1">Educational programs</p>
            </div>
            
            <div className="p-4 bg-gradient-to-br from-orange-50 to-red-50 rounded-xl border border-orange-200">
              <div className="flex items-center justify-center mb-3">
                <Globe className="h-8 w-8 text-orange-600" />
              </div>
              <h3 className="font-semibold text-orange-800 text-sm">Ethical AI</h3>
              <p className="text-xs text-orange-700 mt-1">Responsible practices</p>
            </div>
          </div>
        </div>
        
        <UserSearch />
        
        {loading && (
          <div className="card p-8">
            <div className="flex items-center justify-center space-x-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-600"></div>
              <div className="text-center">
                <h3 className="text-lg font-semibold text-slate-800 mb-2">Analyzing User Data</h3>
                <p className="text-slate-600">Please wait while we process the information with ethical AI practices...</p>
              </div>
            </div>
          </div>
        )}
        
        {currentUser && (
          <div className="space-y-6">
            <UserProfile />
            {(tweets.length > 0 || posts.length > 0) && <TweetList />}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Home;