import React, { useState } from 'react';
import { Heart, Users, TrendingUp, Target, Award, Globe, Play } from 'lucide-react';
import useApi from '../../hooks/useApi';

const SocialImpactTracker = ({ analysisData }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [hasAnalyzed, setHasAnalyzed] = useState(false);
  
  // Get username from analysis data for dynamic analysis
  const username = analysisData?.analysis?.username || analysisData?.username;
  
  // Use the useApi hook with username parameter for dynamic analysis
  const apiUrl = username 
    ? `http://localhost:8000/api/social-impact?username=${encodeURIComponent(username)}`
    : 'http://localhost:8000/api/social-impact';
  
  const { data: impactData, loading, error, refetch } = useApi(apiUrl, {
    enabled: false // Don't fetch automatically
  });

  const impactMetrics = impactData?.impact_metrics || {
    marginalized_groups: {
      total_analyzed: 1250,
      protected_users: 342,
      bias_detected: 23,
      interventions_applied: 15
    },
    social_justice_score: {
      overall: 0.87,
      representation: 0.82,
      fairness: 0.91,
      inclusivity: 0.85
    },
    community_impact: {
      positive_interventions: 89,
      bias_reduction: 0.23,
      protected_groups_supported: 4,
      social_justice_initiatives: 12
    }
  };

  const marginalizedGroups = impactData?.marginalized_groups || [
    { name: 'Women', count: 156, bias_score: 0.12, status: 'protected' },
    { name: 'People of Color', count: 203, bias_score: 0.08, status: 'protected' },
    { name: 'LGBTQ+', count: 89, bias_score: 0.15, status: 'protected' },
    { name: 'People with Disabilities', count: 67, bias_score: 0.18, status: 'protected' },
    { name: 'Religious Minorities', count: 134, bias_score: 0.11, status: 'protected' },
    { name: 'Economic Disadvantaged', count: 245, bias_score: 0.22, status: 'protected' }
  ];

  // Safe access to nested properties with fallbacks
  const socialJusticeScore = impactMetrics?.social_justice_score || { overall: 0.87, representation: 0.82, fairness: 0.91, inclusivity: 0.85 };
  const marginalizedGroupsData = impactMetrics?.marginalized_groups || { protected_users: 342, total_analyzed: 1250, bias_detected: 23, interventions_applied: 15 };
  const communityImpactData = impactMetrics?.community_impact || { positive_interventions: 89, bias_reduction: 0.23, protected_groups_supported: 4, social_justice_initiatives: 12 };

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
          <div className="p-3 bg-gradient-to-r from-pink-500 to-rose-500 rounded-xl">
            <Heart className="h-6 w-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold gradient-text">Social Justice Impact</h2>
            <p className="text-slate-600 text-sm">AI-powered social justice analysis</p>
          </div>
        </div>

        <div className="text-center py-12">
          <div className="mb-6">
            <Heart className="h-16 w-16 text-slate-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-800 mb-2">Start Social Impact Analysis</h3>
            <p className="text-slate-600 mb-6">
              {username 
                ? `Analyze @${username}'s social justice impact using AI`
                : 'Search for a user first to enable AI analysis'
              }
            </p>
          </div>
          
          <button
            onClick={handleStartAnalysis}
            disabled={!username || isAnalyzing}
            className={`px-6 py-3 rounded-lg font-medium transition-all flex items-center space-x-2 mx-auto ${
              username && !isAnalyzing
                ? 'bg-gradient-to-r from-pink-500 to-rose-500 text-white hover:from-pink-600 hover:to-rose-600'
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
              {impactData?.analysis_type === 'dynamic' ? 'Analyzing with AI...' : 'Loading Social Impact'}
            </h3>
            <p className="text-slate-600">
              {impactData?.analysis_type === 'dynamic' 
                ? 'Using Gemini AI to analyze social justice impact'
                : 'Fetching social impact metrics...'
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
          <Heart className="h-12 w-12 text-red-500 mx-auto mb-4" />
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
          <div className="p-3 bg-gradient-to-r from-pink-500 to-rose-500 rounded-xl">
            <Heart className="h-6 w-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold gradient-text">Social Justice Impact</h2>
            <p className="text-slate-600 text-sm">
              {impactData?.analysis_type === 'dynamic' 
                ? 'AI-powered social justice analysis'
                : 'Supporting marginalized communities and social justice'
              }
            </p>
            {impactData?.analysis_type === 'dynamic' && (
              <div className="mt-2">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-pink-100 text-pink-800">
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
        {['overview', 'marginalized-groups', 'social-justice-scores', 'achievements'].map((tab) => (
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
            <div className="p-4 bg-gradient-to-br from-pink-50 to-rose-50 rounded-xl border border-pink-200">
              <div className="flex items-center space-x-2 mb-3">
                <Heart className="h-5 w-5 text-pink-600" />
                <h3 className="font-semibold text-pink-800">Social Justice Score</h3>
              </div>
              <div className="text-3xl font-bold text-pink-600 mb-2">
                {(socialJusticeScore.overall * 100).toFixed(0)}%
              </div>
              <p className="text-pink-700 text-sm">
                {impactData?.analysis_type === 'dynamic' 
                  ? 'AI-analyzed social justice commitment'
                  : 'Strong commitment to social justice principles'
                }
              </p>
            </div>

            <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
              <div className="flex items-center space-x-2 mb-3">
                <Users className="h-5 w-5 text-blue-600" />
                <h3 className="font-semibold text-blue-800">Protected Users</h3>
              </div>
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {marginalizedGroupsData.protected_users}
              </div>
              <p className="text-blue-700 text-sm">
                Users from marginalized groups supported
              </p>
            </div>
          </div>

          <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-200">
            <h3 className="font-semibold text-green-800 mb-3">Key Achievements</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{communityImpactData.positive_interventions}</div>
                <div className="text-sm text-slate-600">Positive Interventions</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{(communityImpactData.bias_reduction * 100).toFixed(0)}%</div>
                <div className="text-sm text-slate-600">Bias Reduction</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{communityImpactData.social_justice_initiatives}</div>
                <div className="text-sm text-slate-600">Initiatives Launched</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'marginalized-groups' && (
        <div className="space-y-4">
          {marginalizedGroups.map((group, index) => (
            <div key={index} className="p-4 bg-white border border-slate-200 rounded-xl">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg">
                    <Users className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-800">{group.name}</h3>
                    <p className="text-sm text-slate-600">{group.count} users analyzed</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-slate-800">
                    {(group.bias_score * 100).toFixed(1)}%
                  </div>
                  <div className="text-xs text-slate-600">Bias Score</div>
                </div>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full transition-all ${
                    group.bias_score < 0.1 ? 'bg-green-500' : 
                    group.bias_score < 0.2 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${group.bias_score * 100}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'social-justice-scores' && (
        <div className="space-y-4">
          {Object.entries(socialJusticeScore).map(([key, value]) => (
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
                  className="h-3 bg-gradient-to-r from-pink-500 to-rose-500 rounded-full transition-all"
                  style={{ width: `${value * 100}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'achievements' && (
        <div className="space-y-4">
          <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
            <div className="flex items-center space-x-2 mb-3">
              <Award className="h-5 w-5 text-blue-600" />
              <h3 className="font-semibold text-blue-800">Achievements</h3>
            </div>
            <ul className="space-y-2 text-blue-700">
              <li className="flex items-center space-x-2">
                <TrendingUp className="h-4 w-4" />
                <span>{(communityImpactData.bias_reduction * 100).toFixed(0)}% bias reduction achieved</span>
              </li>
              <li className="flex items-center space-x-2">
                <Globe className="h-4 w-4" />
                <span>{communityImpactData.social_justice_initiatives} initiatives launched</span>
              </li>
              <li className="flex items-center space-x-2">
                <Users className="h-4 w-4" />
                <span>{marginalizedGroupsData.interventions_applied} interventions applied</span>
              </li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default SocialImpactTracker; 