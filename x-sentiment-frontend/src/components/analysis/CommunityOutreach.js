import React, { useState } from 'react';
import { BookOpen, Users, TrendingUp, Award, Globe, Target } from 'lucide-react';
import useApi from '../../hooks/useApi';

const CommunityOutreach = ({ analysisData }) => {
  const [activeTab, setActiveTab] = useState('overview');
  
  // Use the useApi hook correctly
  const { data: outreachData, loading, error } = useApi('http://localhost:8000/api/community-outreach');

  const educationalPrograms = outreachData?.educational_programs || [
    {
      name: 'AI Ethics Workshop',
      description: 'Interactive workshops on responsible AI development',
      participants: 156,
      impact: '85% reported improved understanding',
      status: 'ongoing',
      category: 'education'
    },
    {
      name: 'Bias Detection Training',
      description: 'Training sessions on identifying and mitigating AI bias',
      participants: 89,
      impact: '92% can now detect bias patterns',
      status: 'completed',
      category: 'training'
    },
    {
      name: 'Community AI Lab',
      description: 'Hands-on experience with ethical AI tools',
      participants: 234,
      impact: '67% implemented ethical practices',
      status: 'ongoing',
      category: 'hands-on'
    },
    {
      name: 'Youth AI Mentorship',
      description: 'Mentoring program for underrepresented youth in AI',
      participants: 45,
      impact: '78% pursued AI-related education',
      status: 'ongoing',
      category: 'mentorship'
    }
  ];

  const communityInitiatives = outreachData?.community_initiatives || [
    {
      name: 'Digital Literacy Program',
      description: 'Teaching basic digital skills to underserved communities',
      participants: 312,
      impact: 'Increased digital access by 40%',
      status: 'active'
    },
    {
      name: 'AI for Social Good',
      description: 'Projects using AI to solve community problems',
      participants: 89,
      impact: '5 community problems solved',
      status: 'active'
    },
    {
      name: 'Ethical AI Advocacy',
      description: 'Raising awareness about responsible AI use',
      participants: 567,
      impact: 'Reached 10,000+ people',
      status: 'active'
    }
  ];

  const impactMetrics = outreachData?.impact_metrics || {
    total_participants: 1247,
    programs_launched: 8,
    community_reach: 15600,
    success_rate: 0.87
  };

  const additionalResources = outreachData?.additional_resources || [
    {
      title: 'AI Ethics Guidelines',
      description: 'Comprehensive guide for ethical AI development',
      type: 'documentation',
      url: '#'
    },
    {
      title: 'Bias Detection Toolkit',
      description: 'Tools and resources for bias detection',
      type: 'toolkit',
      url: '#'
    },
    {
      title: 'Community Outreach Guide',
      description: 'Best practices for community engagement',
      type: 'guide',
      url: '#'
    }
  ];

  if (loading) {
    return (
      <div className="card p-6">
        <div className="flex items-center justify-center space-x-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-600"></div>
          <div className="text-center">
            <h3 className="text-lg font-medium text-slate-800 mb-2">Loading Community Outreach</h3>
            <p className="text-slate-600">Fetching community initiatives...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card p-6">
        <div className="text-center">
          <BookOpen className="h-12 w-12 mx-auto mb-4 text-red-500" />
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
        <div className="p-3 bg-gradient-to-r from-orange-500 to-amber-500 rounded-xl">
          <BookOpen className="h-6 w-6 text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-bold gradient-text">Community Outreach</h2>
          <p className="text-slate-600 text-sm">Educational programs and community initiatives</p>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-2 mb-6">
        {['overview', 'educational-programs', 'community-initiatives', 'resources'].map((tab) => (
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
            <div className="p-4 bg-gradient-to-br from-orange-50 to-amber-50 rounded-xl border border-orange-200">
              <div className="flex items-center space-x-2 mb-3">
                <Users className="h-5 w-5 text-orange-600" />
                <h3 className="font-semibold text-orange-800">Total Participants</h3>
              </div>
              <div className="text-3xl font-bold text-orange-600 mb-2">
                {(impactMetrics.total_participants || 0).toLocaleString()}
              </div>
              <p className="text-orange-700 text-sm">
                People engaged in community programs
              </p>
            </div>

            <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-200">
              <div className="flex items-center space-x-2 mb-3">
                <Award className="h-5 w-5 text-green-600" />
                <h3 className="font-semibold text-green-800">Success Rate</h3>
              </div>
              <div className="text-3xl font-bold text-green-600 mb-2">
                {((impactMetrics.success_rate || 0) * 100).toFixed(0)}%
              </div>
              <p className="text-green-700 text-sm">
                Programs achieving their objectives
              </p>
            </div>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl">
            <h3 className="font-semibold text-slate-800 mb-3">Quick Stats</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{impactMetrics.programs_launched || 0}</div>
                <div className="text-sm text-slate-600">Programs Launched</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{(impactMetrics.community_reach || 0).toLocaleString()}</div>
                <div className="text-sm text-slate-600">Community Reach</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{educationalPrograms.length}</div>
                <div className="text-sm text-slate-600">Active Programs</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'educational-programs' && (
        <div className="space-y-4">
          {educationalPrograms.map((program, index) => (
            <div key={index} className="p-4 bg-white border border-slate-200 rounded-xl">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${
                    program.status === 'ongoing' 
                      ? 'bg-green-100 text-green-600' 
                      : 'bg-blue-100 text-blue-600'
                  }`}>
                    <BookOpen className="h-4 w-4" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-800">{program.name}</h3>
                    <p className="text-sm text-slate-600">{program.description}</p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  program.status === 'ongoing' 
                    ? 'bg-green-100 text-green-700' 
                    : 'bg-blue-100 text-blue-700'
                }`}>
                  {program.status}
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center space-x-2">
                  <Users className="h-4 w-4 text-slate-600" />
                  <span className="text-sm text-slate-700">{program.participants || 0} participants</span>
                </div>
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-4 w-4 text-green-600" />
                  <span className="text-sm text-green-700 font-medium">{program.impact}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'community-initiatives' && (
        <div className="space-y-4">
          {communityInitiatives.map((initiative, index) => (
            <div key={index} className="p-4 bg-white border border-slate-200 rounded-xl">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg">
                    <Globe className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-800">{initiative.name}</h3>
                    <p className="text-sm text-slate-600">{initiative.description}</p>
                  </div>
                </div>
                <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                  {initiative.status}
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center space-x-2">
                  <Users className="h-4 w-4 text-slate-600" />
                  <span className="text-sm text-slate-700">{initiative.participants || 0} participants</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Target className="h-4 w-4 text-purple-600" />
                  <span className="text-sm text-purple-700 font-medium">{initiative.impact}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'resources' && (
        <div className="space-y-4">
          {additionalResources.map((resource, index) => (
            <div key={index} className="p-4 bg-white border border-slate-200 rounded-xl">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg">
                    <BookOpen className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-800">{resource.title}</h3>
                    <p className="text-sm text-slate-600">{resource.description}</p>
                  </div>
                </div>
                <button className="px-3 py-1 bg-blue-100 text-blue-700 rounded-lg text-sm font-medium hover:bg-blue-200 transition-colors">
                  Access
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CommunityOutreach; 