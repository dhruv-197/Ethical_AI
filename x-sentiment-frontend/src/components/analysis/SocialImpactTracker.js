import React, { useState } from 'react';
import { Heart, Users, TrendingUp, Target, Award, Globe } from 'lucide-react';
import useApi from '../../hooks/useApi';

const SocialImpactTracker = ({ analysisData }) => {
  const [activeTab, setActiveTab] = useState('overview');
  
  // Use the useApi hook correctly
  const { data: impactData, loading, error } = useApi('http://localhost:8000/api/social-impact');

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

  if (loading) {
    return (
      <div className="card p-6">
        <div className="flex items-center justify-center space-x-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-600"></div>
          <div className="text-center">
            <h3 className="text-lg font-medium text-slate-800 mb-2">Loading Social Impact</h3>
            <p className="text-slate-600">Analyzing community impact...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card p-6">
        <div className="text-center">
          <Heart className="h-12 w-12 mx-auto mb-4 text-red-500" />
          <h3 className="text-lg font-medium text-slate-800 mb-2">Error Loading Data</h3>
          <p className="text-slate-600 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="card p-6">
      <div className="flex items-center space-x-3 mb-6">
        <div className="p-3 bg-gradient-to-r from-pink-500 to-rose-500 rounded-xl">
          <Heart className="h-6 w-6 text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-bold gradient-text">Social Justice Impact</h2>
          <p className="text-slate-600 text-sm">Community impact and social justice metrics</p>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-2 mb-6">
        {['overview', 'protected-groups', 'social-justice', 'community-impact'].map((tab) => (
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
                {(impactMetrics.social_justice_score.overall * 100).toFixed(0)}%
              </div>
              <p className="text-pink-700 text-sm">
                Strong commitment to social justice principles
              </p>
            </div>

            <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
              <div className="flex items-center space-x-2 mb-3">
                <Users className="h-5 w-5 text-blue-600" />
                <h3 className="font-semibold text-blue-800">Protected Users</h3>
              </div>
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {impactMetrics.marginalized_groups.protected_users}
              </div>
              <p className="text-blue-700 text-sm">
                Users from marginalized groups supported
              </p>
            </div>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl">
            <h3 className="font-semibold text-slate-800 mb-3">Key Achievements</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{impactMetrics.community_impact.positive_interventions}</div>
                <div className="text-sm text-slate-600">Positive Interventions</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{(impactMetrics.community_impact.bias_reduction * 100).toFixed(0)}%</div>
                <div className="text-sm text-slate-600">Bias Reduction</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{impactMetrics.community_impact.social_justice_initiatives}</div>
                <div className="text-sm text-slate-600">Initiatives Launched</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'protected-groups' && (
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

      {activeTab === 'social-justice' && (
        <div className="space-y-4">
          {Object.entries(impactMetrics.social_justice_score).map(([key, value]) => (
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

      {activeTab === 'community-impact' && (
        <div className="space-y-4">
          <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-200">
            <div className="flex items-center space-x-2 mb-3">
              <Target className="h-5 w-5 text-green-600" />
              <h3 className="font-semibold text-green-800">Impact Metrics</h3>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {impactMetrics.community_impact.positive_interventions}
                </div>
                <div className="text-sm text-green-700">Positive Interventions</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {impactMetrics.community_impact.protected_groups_supported}
                </div>
                <div className="text-sm text-green-700">Protected Groups</div>
              </div>
            </div>
          </div>

          <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
            <div className="flex items-center space-x-2 mb-3">
              <Award className="h-5 w-5 text-blue-600" />
              <h3 className="font-semibold text-blue-800">Achievements</h3>
            </div>
            <ul className="space-y-2 text-blue-700">
              <li className="flex items-center space-x-2">
                <TrendingUp className="h-4 w-4" />
                <span>{(impactMetrics.community_impact.bias_reduction * 100).toFixed(0)}% bias reduction achieved</span>
              </li>
              <li className="flex items-center space-x-2">
                <Globe className="h-4 w-4" />
                <span>{impactMetrics.community_impact.social_justice_initiatives} initiatives launched</span>
              </li>
              <li className="flex items-center space-x-2">
                <Users className="h-4 w-4" />
                <span>{impactMetrics.marginalized_groups.interventions_applied} interventions applied</span>
              </li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default SocialImpactTracker; 