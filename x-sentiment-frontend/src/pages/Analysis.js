import React, { useEffect, useState } from 'react';
import Select from 'react-select';
import { useDispatch, useSelector } from 'react-redux';
import Layout from '../components/common/Layout';
import AnalysisResults from '../components/analysis/AnalysisResults';
import BiasDetection from '../components/analysis/BiasDetection';
import SocialImpactTracker from '../components/analysis/SocialImpactTracker';
import CommunityOutreach from '../components/analysis/CommunityOutreach';
import { MessageCircle, Image, GitMerge, Sliders, Info as InfoIcon, Shield, Heart, BookOpen } from 'lucide-react';
import {
  analyzeUserProfile,
  refreshUserData,
  clearAnalysis,
  clearError
} from '../store/slices/analysisSlice';
import { BarChart3, TrendingUp, AlertCircle, Loader2, RefreshCw } from 'lucide-react';

// Helper functions for descriptions
const getTechniqueDescription = (technique) => {
  switch (technique) {
    case 'weighted_average': return 'Simple & Fast';
    case 'attention': return 'Adaptive';
    case 'feature_fusion': return 'Deep Features';
    case 'stacking': return 'Meta-learning';
    case 'learned_weights': return 'Optimized';
    default: return '';
  }
};

const getFusionTechniqueFullDescription = (technique) => {
  switch (technique) {
    case 'weighted_average':
      return 'Uses a fixed weight to combine text and image predictions. Simple and interpretable.';
    case 'attention':
      return 'Dynamically weighs modalities based on content reliability - adapts to each input.';
    case 'feature_fusion':
      return 'Combines raw features from text and image models before classification for deeper interactions.';
    case 'stacking':
      return 'Treats predictions from base models as features for a meta-classifier to learn complex relationships.';
    case 'learned_weights':
      return 'Uses data-trained weights to optimally combine predictions from different modalities.';
    default:
      return '';
  }
};

const IMAGE_MODELS = [
  { value: 'clip', label: 'CLIP' },
  { value: 'vgg16', label: 'VGG16' }
];
const TEXT_MODELS = [
  { value: 'xlnet', label: 'XLNet' },
  { value: 'bert', label: 'BERT' }
];

const FUSION_TECHNIQUES = [
  { value: 'weighted_average', label: 'Weighted Average' },
  { value: 'attention', label: 'Attention-Based Fusion' },
  { value: 'feature_fusion', label: 'Feature-Level Fusion' },
  { value: 'stacking', label: 'Model Stacking' },
  { value: 'learned_weights', label: 'Learned Weights' }
];

const Analysis = () => {
  const [imageModels, setImageModels] = useState([IMAGE_MODELS[0]]);
  const [textModels, setTextModels] = useState([TEXT_MODELS[0]]);
  const [fusionTechnique, setFusionTechnique] = useState(FUSION_TECHNIQUES[0]);
  const [alpha, setAlpha] = useState(0.5);
  const [activeTab, setActiveTab] = useState('sentiment');
  
  const dispatch = useDispatch();
  const { currentUser, tweets } = useSelector((state) => state.user);
  const { 
    currentAnalysis, 
    loading, 
    error, 
    refreshing, 
    refreshError 
  } = useSelector((state) => state.analysis);

  useEffect(() => {
    // Clear previous analysis when component mounts
    return () => {
      dispatch(clearAnalysis());
    };
  }, [dispatch]);

  const handleAnalyzeProfile = () => {
    if (currentUser) {
      dispatch(analyzeUserProfile({
        username: currentUser.username,
        image_model: imageModels.map(m => m.value),
        text_model: textModels.map(m => m.value),
        fusion_technique: fusionTechnique.value,
        alpha: alpha
      }));
    }
  };

  const handleRefreshData = () => {
    if (currentUser) {
      dispatch(refreshUserData(currentUser.username));
    }
  };

  const handleClearError = () => {
    dispatch(clearError());
  };

  const tabs = [
    { id: 'sentiment', name: 'Sentiment Analysis', icon: TrendingUp },
    { id: 'bias', name: 'Ethical AI Monitoring', icon: Shield },
    { id: 'social-impact', name: 'Social Justice Impact', icon: Heart },
    { id: 'community', name: 'Community Outreach', icon: BookOpen }
  ];

  if (!currentUser) {
    return (
      <Layout>
        <div className="text-center py-12">
          <Shield className="h-16 w-16 mx-auto mb-4 text-slate-300" />
          <h2 className="text-2xl font-bold text-slate-800 mb-2">No Analysis Available</h2>
          <p className="text-slate-600">Please analyze a user profile first to view results.</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-4">
            PostPatrol Analysis Dashboard
          </h1>
          <p className="text-lg text-slate-600 max-w-3xl mx-auto">
            Comprehensive sentiment analysis with ethical AI monitoring, social justice impact tracking, 
            and community outreach initiatives to promote responsible AI practices.
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap justify-center gap-2 mb-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-6 py-3 rounded-xl text-sm font-medium transition-all duration-300 ${
                  activeTab === tab.id
                    ? 'bg-slate-200 text-slate-800 shadow-lg'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-800'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span>{tab.name}</span>
              </button>
            );
          })}
        </div>

        {/* Content based on active tab */}
        {activeTab === 'sentiment' && (
          <div className="space-y-6">
            {/* Header with Analysis Button */}
            <div className="card p-6">
              <div className="flex items-center justify-between mb-6">
                <h1 className="text-2xl font-bold gradient-text">
                  Analysis for @{currentUser.username}
                </h1>
              </div>
              
              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-blue-800">Total Tweets</h3>
                    <MessageCircle className="h-5 w-5 text-blue-600" />
                  </div>
                  <p className="text-2xl font-bold text-blue-600">{tweets.length}</p>
                </div>
                
                <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-200">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-green-800">With Media</h3>
                    <TrendingUp className="h-5 w-5 text-green-600" />
                  </div>
                  <p className="text-2xl font-bold text-green-600">
                    {tweets.filter(t => t.media_urls && t.media_urls.length > 0).length}
                  </p>
                </div>
                
                <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-200">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-purple-800">Status</h3>
                    <BarChart3 className="h-5 w-5 text-purple-600" />
                  </div>
                  <p className="text-sm text-purple-600">
                    {currentAnalysis ? 'Analyzed' : 'Ready to Analyze'}
                  </p>
                </div>
              </div>
              
              {tweets.length === 0 && (
                <div className="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                  <div className="flex items-center space-x-2">
                    <AlertCircle className="h-5 w-5 text-yellow-600" />
                    <p className="text-yellow-700">
                      No tweets available for analysis. Please fetch user data first.
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Analysis Configuration */}
            <div className="card p-6">
              <h2 className="text-xl font-bold mb-5 text-slate-800 border-b pb-3">Analysis Configuration</h2>

              <div className="space-y-6">
                {/* Model Selection */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
                    <label className="block text-slate-800 font-medium mb-2">
                      <div className="flex items-center mb-1">
                        <MessageCircle className="h-4 w-4 mr-2" />
                        Text Models
                      </div>
                    </label>
                    <Select
                      isMulti
                      options={TEXT_MODELS}
                      value={textModels}
                      onChange={setTextModels}
                      className="basic-multi-select"
                      classNamePrefix="select"
                      placeholder="Select text models..."
                    />
                    <p className="text-xs text-slate-500 mt-2">
                      Models used for analyzing tweet text content
                    </p>
                  </div>

                  <div className="p-4 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl border border-indigo-200">
                    <label className="block text-slate-800 font-medium mb-2">
                      <div className="flex items-center mb-1">
                        <Image className="h-4 w-4 mr-2" />
                        Image Models
                      </div>
                    </label>
                    <Select
                      isMulti
                      options={IMAGE_MODELS}
                      value={imageModels}
                      onChange={setImageModels}
                      className="basic-multi-select"
                      classNamePrefix="select"
                      placeholder="Select image models..."
                    />
                    <p className="text-xs text-slate-500 mt-2">
                      Models used for analyzing media content
                    </p>
                  </div>
                </div>

                {/* Fusion Technique */}
                <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-200">
                  <label className="block text-slate-800 font-medium mb-3">
                    <div className="flex items-center">
                      <GitMerge className="h-4 w-4 mr-2" />
                      Fusion Technique
                    </div>
                  </label>

                  <div className="grid grid-cols-1 md:grid-cols-5 gap-2">
                    {FUSION_TECHNIQUES.map((technique) => (
                      <div
                        key={technique.value}
                        onClick={() => setFusionTechnique(technique)}
                        className={`
                          cursor-pointer rounded-lg border p-3 transition-all
                          ${fusionTechnique.value === technique.value
                            ? 'border-purple-500 bg-purple-100 shadow-sm'
                            : 'border-slate-200 hover:border-purple-300 hover:bg-purple-50'
                          }
                        `}
                      >
                        <div className="text-center">
                          <div className="font-medium mb-1">{technique.label}</div>
                          <div className="text-xs text-slate-500">
                            {getTechniqueDescription(technique.value)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <p className="text-sm text-slate-600 mt-3">
                    {getFusionTechniqueFullDescription(fusionTechnique.value)}
                  </p>
                </div>

                {/* Alpha slider (only for weighted average) */}
                {fusionTechnique.value === 'weighted_average' && (
                  <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-200">
                    <label className="block text-slate-800 font-medium mb-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <Sliders className="h-4 w-4 mr-2" />
                          Text-Image Weight (Alpha)
                        </div>
                        <span className="text-lg font-semibold text-green-700">{alpha.toFixed(2)}</span>
                      </div>
                    </label>

                    <div className="px-2">
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.05"
                        value={alpha}
                        onChange={(e) => setAlpha(parseFloat(e.target.value))}
                        className="w-full accent-green-600"
                      />
                      <div className="flex justify-between text-xs text-slate-500 mt-1">
                        <span className="font-medium text-blue-600">Images Only</span>
                        <span className="font-medium">Equal Weight</span>
                        <span className="font-medium text-green-600">Text Only</span>
                      </div>
                    </div>

                    <div className="flex items-center mt-3 p-2 bg-white rounded border border-green-200">
                      <InfoIcon className="h-4 w-4 text-green-600 mr-2 flex-shrink-0" />
                      <p className="text-xs text-slate-600">
                        Alpha controls the balance between text and image models.
                        Higher values give more weight to text analysis.
                      </p>
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={handleAnalyzeProfile}
                  disabled={loading || textModels.length === 0 || imageModels.length === 0}
                  className="flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
                >
                  {loading ?
                    <Loader2 className="h-5 w-5 animate-spin" /> :
                    <BarChart3 className="h-5 w-5" />
                  }
                  <span className="font-medium">{loading ? 'Analyzing...' : 'Analyze Profile'}</span>
                </button>
              </div>
            </div>

            {/* Error Display */}
            {(error || refreshError) && (
              <div className="card p-4 bg-red-50 border border-red-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <AlertCircle className="h-5 w-5 text-red-600" />
                    <p className="text-red-700">{error || refreshError}</p>
                  </div>
                  <button
                    onClick={handleClearError}
                    className="text-red-600 hover:text-red-800 font-medium"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            )}

            {/* Loading State */}
            {loading && (
              <div className="card p-6">
                <div className="flex items-center justify-center space-x-4">
                  <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                  <div className="space-y-2">
                    <p className="text-lg font-medium text-slate-900">
                      Analyzing Profile...
                    </p>
                    <p className="text-sm text-slate-600">
                      Processing {tweets.length} tweets and media content with ethical AI practices
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Analysis Results */}
            {currentAnalysis && currentAnalysis.success && (
              <AnalysisResults analysis={currentAnalysis.analysis} />
            )}
          </div>
        )}

        {activeTab === 'bias' && (
          <BiasDetection analysisData={currentAnalysis} />
        )}

        {activeTab === 'social-impact' && (
          <SocialImpactTracker analysisData={currentAnalysis} />
        )}

        {activeTab === 'community' && (
          <CommunityOutreach />
        )}
      </div>
    </Layout>
  );
};

export default Analysis;