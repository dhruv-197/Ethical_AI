import React, { useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, Users, TrendingUp, Play } from 'lucide-react';
import useApi from '../../hooks/useApi';

const BiasDetection = ({ analysisData }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [hasAnalyzed, setHasAnalyzed] = useState(false);
  
  // Get username from analysis data for dynamic analysis
  const username = analysisData?.analysis?.username || analysisData?.username;
  
  // Use the useApi hook with username parameter for dynamic analysis
  const apiUrl = username 
    ? `http://localhost:8000/api/bias-detection?username=${encodeURIComponent(username)}`
    : 'http://localhost:8000/api/bias-detection';
  
  const { data: biasData, loading, error, refetch } = useApi(apiUrl, {
    enabled: false // Don't fetch automatically
  });

  const biasMetrics = biasData?.bias_metrics || {
    gender_bias: {
      score: 0.15,
      status: 'low',
      description: 'Minimal gender bias detected in analysis'
    },
    racial_bias: {
      score: 0.08,
      status: 'very-low',
      description: 'Very low racial bias detected'
    },
    age_bias: {
      score: 0.22,
      status: 'moderate',
      description: 'Moderate age bias detected - requires attention'
    },
    socioeconomic_bias: {
      score: 0.12,
      status: 'low',
      description: 'Low socioeconomic bias detected'
    }
  };

  const fairnessMetrics = biasData?.fairness_metrics || {
    equalized_odds: 0.89,
    demographic_parity: 0.92,
    predictive_rate_parity: 0.88,
    overall_fairness: 0.90
  };

  const getBiasColor = (status) => {
    switch (status) {
      case 'very-low': return 'text-green-600 bg-green-50';
      case 'low': return 'text-blue-600 bg-blue-50';
      case 'moderate': return 'text-yellow-600 bg-yellow-50';
      case 'high': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getBiasIcon = (status) => {
    switch (status) {
      case 'very-low':
      case 'low':
        return <CheckCircle className="h-5 w-5" />;
      case 'moderate':
        return <AlertTriangle className="h-5 w-5" />;
      case 'high':
        return <AlertTriangle className="h-5 w-5 text-red-600" />;
      default:
        return <Shield className="h-5 w-5" />;
    }
  };

  const handleStartAnalysis = async () => {
    if (!username) {
      alert('Please search for a user first to enable AI analysis');
      return;
    }
    
    setIsAnalyzing(true);
    setHasAnalyzed(true);
    try {
      await refetch();
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Show start analysis button if no data or not analyzed yet
  if (!hasAnalyzed && !loading) {
    return (
      <div className="card p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-3 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl">
            <Shield className="h-6 w-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold gradient-text">Ethical AI Monitoring</h2>
            <p className="text-slate-600 text-sm">AI-powered bias detection</p>
          </div>
        </div>

        <div className="text-center py-12">
          <div className="mb-6">
            <Shield className="h-16 w-16 text-slate-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-800 mb-2">Start Bias Detection Analysis</h3>
            <p className="text-slate-600 mb-6">
              {username 
                ? `Analyze @${username}'s tweets for bias patterns using AI`
                : 'Search for a user first to enable AI analysis'
              }
            </p>
          </div>
          
          <button
            onClick={handleStartAnalysis}
            disabled={!username || isAnalyzing}
            className={`px-6 py-3 rounded-lg font-medium transition-all flex items-center space-x-2 mx-auto ${
              username && !isAnalyzing
                ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white hover:from-green-600 hover:to-emerald-600'
                : 'bg-slate-200 text-slate-400 cursor-not-allowed'
            }`}
          >
            {isAnalyzing ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                <span>Start AI Analysis</span>
              </>
            )}
          </button>
          
          {!username && (
            <p className="text-sm text-slate-500 mt-4">
              Go to the Sentiment Analysis tab and search for a user first
            </p>
          )}
        </div>
      </div>
    );
  }

  if (loading || isAnalyzing) {
    return (
      <div className="card p-6">
        <div className="flex items-center justify-center space-x-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-600"></div>
          <div className="text-center">
            <h3 className="text-lg font-medium text-slate-800 mb-2">
              {biasData?.analysis_type === 'dynamic' ? 'Analyzing with AI...' : 'Loading Bias Detection'}
            </h3>
            <p className="text-slate-600">
              {biasData?.analysis_type === 'dynamic' 
                ? 'Using Gemini AI to analyze tweets for bias patterns'
                : 'Fetching bias detection metrics...'
              }
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card p-6">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-red-800 mb-2">Analysis Failed</h3>
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={handleStartAnalysis}
            className="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors"
          >
            Retry Analysis
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl">
            <Shield className="h-6 w-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold gradient-text">Ethical AI Monitoring</h2>
            <p className="text-slate-600 text-sm">
              {biasData?.analysis_type === 'dynamic' 
                ? 'AI-powered bias detection'
                : 'Bias detection and fairness metrics'
              }
            </p>
            {biasData?.analysis_type === 'dynamic' && (
              <div className="mt-2">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  🤖 Dynamic AI Analysis
                </span>
              </div>
            )}
          </div>
        </div>
        
        {username && (
          <button
            onClick={handleStartAnalysis}
            disabled={isAnalyzing}
            className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors text-sm"
          >
            {isAnalyzing ? 'Analyzing...' : 'Refresh Analysis'}
          </button>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-2 mb-6">
        {['overview', 'bias-detection', 'fairness-metrics', 'recommendations'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === tab
                ? 'bg-slate-200 text-slate-800'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            {tab.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
          </button>
        ))}
      </div>

      {/* Content based on active tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-200">
              <div className="flex items-center space-x-2 mb-3">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <h3 className="font-semibold text-green-800">Overall Fairness Score</h3>
              </div>
              <div className="text-3xl font-bold text-green-600 mb-2">
                {(fairnessMetrics.overall_fairness * 100).toFixed(0)}%
              </div>
              <p className="text-green-700 text-sm">
                {biasData?.analysis_type === 'dynamic' 
                  ? 'AI-analyzed fairness across demographic groups'
                  : 'Your AI model demonstrates good fairness across demographic groups'
                }
              </p>
            </div>

            <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
              <div className="flex items-center space-x-2 mb-3">
                <Users className="h-5 w-5 text-blue-600" />
                <h3 className="font-semibold text-blue-800">Protected Groups</h3>
              </div>
              <div className="text-3xl font-bold text-blue-600 mb-2">4</div>
              <p className="text-blue-700 text-sm">
                Gender, Race, Age, and Socioeconomic status monitored
              </p>
            </div>
          </div>

          <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-200">
            <h3 className="font-semibold text-purple-800 mb-3">Key Insights</h3>
            <ul className="space-y-2 text-purple-700">
              <li className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4" />
                <span>Gender bias: {(biasMetrics.gender_bias.score * 100).toFixed(1)}% detected</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4" />
                <span>Racial bias: {(biasMetrics.racial_bias.score * 100).toFixed(1)}% detected</span>
              </li>
              <li className="flex items-center space-x-2">
                <AlertTriangle className="h-4 w-4" />
                <span>Age bias: {(biasMetrics.age_bias.score * 100).toFixed(1)}% detected - requires attention</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4" />
                <span>Socioeconomic bias: {(biasMetrics.socioeconomic_bias.score * 100).toFixed(1)}% detected</span>
              </li>
            </ul>
          </div>
        </div>
      )}

      {activeTab === 'bias-detection' && (
        <div className="space-y-4">
          {Object.entries(biasMetrics).map(([key, metric]) => (
            <div key={key} className="p-4 bg-white border border-slate-200 rounded-xl">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  {getBiasIcon(metric.status)}
                  <h3 className="font-semibold text-slate-800 capitalize">
                    {key.replace('_', ' ')} Bias
                  </h3>
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-medium ${getBiasColor(metric.status)}`}>
                  {metric.status.replace('-', ' ')}
                </div>
              </div>
              <div className="mb-3">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-600">Bias Score</span>
                  <span className="font-medium">{(metric.score * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all ${
                      metric.score < 0.1 ? 'bg-green-500' : 
                      metric.score < 0.2 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${metric.score * 100}%` }}
                  ></div>
                </div>
              </div>
              <p className="text-slate-600 text-sm">{metric.description}</p>
              {metric.examples && metric.examples.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-medium text-slate-500 mb-1">Examples:</p>
                  <ul className="text-xs text-slate-600 space-y-1">
                    {metric.examples.slice(0, 2).map((example, idx) => (
                      <li key={idx} className="flex items-start space-x-1">
                        <span className="text-slate-400">•</span>
                        <span>{example}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {activeTab === 'fairness-metrics' && (
        <div className="space-y-4">
          {Object.entries(fairnessMetrics).map(([key, value]) => (
            <div key={key} className="p-4 bg-white border border-slate-200 rounded-xl">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-slate-800 capitalize">
                  {key.replace(/_/g, ' ')}
                </h3>
                <div className="text-2xl font-bold text-slate-800">
                  {(value * 100).toFixed(0)}%
                </div>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-3">
                <div 
                  className="h-3 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full transition-all"
                  style={{ width: `${value * 100}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'recommendations' && (
        <div className="space-y-4">
          <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
            <h3 className="font-semibold text-blue-800 mb-3">Immediate Actions</h3>
            <ul className="space-y-2 text-blue-700">
              <li className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4" />
                <span>Review age bias detection - moderate level detected</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4" />
                <span>Implement demographic parity monitoring</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4" />
                <span>Add bias mitigation strategies</span>
              </li>
            </ul>
          </div>

          <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-200">
            <h3 className="font-semibold text-green-800 mb-3">Long-term Improvements</h3>
            <ul className="space-y-2 text-green-700">
              <li className="flex items-center space-x-2">
                <TrendingUp className="h-4 w-4" />
                <span>Expand training data diversity</span>
              </li>
              <li className="flex items-center space-x-2">
                <TrendingUp className="h-4 w-4" />
                <span>Implement fairness-aware algorithms</span>
              </li>
              <li className="flex items-center space-x-2">
                <TrendingUp className="h-4 w-4" />
                <span>Regular bias audits and reporting</span>
              </li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default BiasDetection; 