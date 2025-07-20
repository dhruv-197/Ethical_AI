import React from 'react';
import { BarChart3, TrendingUp, AlertTriangle, CheckCircle, Clock, Image as ImageIcon, MessageCircle, Shield } from 'lucide-react';

const ClassificationBreakdownChart = ({ percentages }) => {
  const categories = [
    { key: 'radical', label: 'Radical', color: 'bg-blue-500', bgColor: 'bg-blue-50', textColor: 'text-blue-600' },
    { key: 'non_radical', label: 'Non-Radical', color: 'bg-green-500', bgColor: 'bg-green-50', textColor: 'text-green-600' },
    { key: 'political', label: 'Politician', color: 'bg-purple-500', bgColor: 'bg-purple-50', textColor: 'text-purple-600' }
  ];

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-6">
        Classification Results
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {categories.map((category) => {
          const percentage = percentages[category.key] || 0;
          return (
            <div key={category.key} className={`p-4 ${category.bgColor} rounded-xl border`}>
              <div className="text-center">
                <h3 className="font-semibold text-gray-800 mb-2">{category.label}</h3>
                <div className={`text-3xl font-bold ${category.textColor} mb-3`}>
                  {percentage}%
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className={`h-3 ${category.color} rounded-full transition-all duration-500`}
                    style={{ width: `${percentage}%` }}
                  ></div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const AnalysisResults = ({ analysis }) => {
  const { classification_summary, content_stats, percentages } = analysis;

  return (
    <div className="space-y-6">
      {/* Overall Classification Summary */}
      <div className="bg-white rounded-lg shadow-md p-6 flex flex-col md:flex-row items-center justify-between">
        <div className="flex items-center space-x-4">
          <BarChart3 className="h-10 w-10 text-blue-500" />
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-1">
              {classification_summary.dominant_category}
            </h2>
            <p className="text-gray-600">
              Confidence: <span className="font-semibold text-blue-600">{classification_summary.confidence_score}%</span>
            </p>
          </div>
        </div>
        <div className="flex space-x-8 mt-4 md:mt-0">
          <div className="flex items-center space-x-2">
            <MessageCircle className="h-6 w-6 text-green-500" />
            <span className="text-gray-700 font-medium">{content_stats.total_tweets} Tweets</span>
          </div>
          <div className="flex items-center space-x-2">
            <ImageIcon className="h-6 w-6 text-purple-500" />
            <span className="text-gray-700 font-medium">{content_stats.total_images} Images</span>
          </div>
          <div className="flex items-center space-x-2">
            <Clock className="h-6 w-6 text-gray-400" />
            <span className="text-gray-500">{content_stats.total_content_analyzed} Items Analyzed</span>
          </div>
        </div>
      </div>

      {/* Classification Results with Progress Bars */}
      <ClassificationBreakdownChart percentages={percentages} />

      {/* Analysis Insights */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Insights</h3>
        <ul className="space-y-2 text-gray-700">
          <li className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span>Content analysis completed with {classification_summary.confidence_score}% confidence</span>
          </li>
          <li className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span>{content_stats.total_content_analyzed} posts analyzed for sentiment patterns</span>
          </li>
          <li className="flex items-center space-x-2">
            <Shield className="h-4 w-4 text-blue-500" />
            <span>Bias detection applied to ensure fair analysis</span>
          </li>
          <li className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span>Protected groups monitored during analysis</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default AnalysisResults;