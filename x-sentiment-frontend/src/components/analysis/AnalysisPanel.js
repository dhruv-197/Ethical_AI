import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { BarChart3, TrendingUp, AlertTriangle, Shield } from 'lucide-react';
import { analyzeUserProfile } from '../../store/slices/analysisSlice';
import toast from 'react-hot-toast';

const AnalysisPanel = () => {
  const dispatch = useDispatch();
  const { currentUser } = useSelector((state) => state.user);
  const { loading, error, analysisResults } = useSelector((state) => state.analysis);

  const handleAnalyze = async () => {
    if (!currentUser) {
      toast.error('Please search for a user first');
      return;
    }

    try {
      await dispatch(analyzeUserProfile(currentUser.username)).unwrap();
      toast.success('Analysis completed successfully!');
    } catch (error) {
      toast.error(error || 'Analysis failed');
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-red-600';
    if (score >= 60) return 'text-orange-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getScoreBgColor = (score) => {
    if (score >= 80) return 'bg-red-100';
    if (score >= 60) return 'bg-orange-100';
    if (score >= 40) return 'bg-yellow-100';
    return 'bg-green-100';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Profile Analysis</h2>
        <button
          onClick={handleAnalyze}
          disabled={loading || !currentUser}
          className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
        >
          <BarChart3 className="h-4 w-4" />
          <span>{loading ? 'Analyzing...' : 'Analyze Profile'}</span>
        </button>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {!currentUser && (
        <div className="text-center py-8">
          <BarChart3 className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">Please search for a user first to analyze their profile</p>
        </div>
      )}

      {analysisResults && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className={`rounded-lg p-4 ${getScoreBgColor(analysisResults.radical_score)}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Radical</p>
                  <p className={`text-2xl font-bold ${getScoreColor(analysisResults.radical_score)}`}>
                    {analysisResults.radical_score}%
                  </p>
                </div>
                <AlertTriangle className={`h-8 w-8 ${getScoreColor(analysisResults.radical_score)}`} />
              </div>
            </div>

            <div className={`rounded-lg p-4 ${getScoreBgColor(100 - analysisResults.radical_score)}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Non-Radical</p>
                  <p className={`text-2xl font-bold ${getScoreColor(100 - analysisResults.radical_score)}`}>
                    {100 - analysisResults.radical_score}%
                  </p>
                </div>
                <Shield className={`h-8 w-8 ${getScoreColor(100 - analysisResults.radical_score)}`} />
              </div>
            </div>

            <div className={`rounded-lg p-4 ${getScoreBgColor(analysisResults.political_score)}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Political</p>
                  <p className={`text-2xl font-bold ${getScoreColor(analysisResults.political_score)}`}>
                    {analysisResults.political_score}%
                  </p>
                </div>
                <TrendingUp className={`h-8 w-8 ${getScoreColor(analysisResults.political_score)}`} />
              </div>
            </div>

            <div className={`rounded-lg p-4 ${getScoreBgColor(analysisResults.crime_score)}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Crime</p>
                  <p className={`text-2xl font-bold ${getScoreColor(analysisResults.crime_score)}`}>
                    {analysisResults.crime_score}%
                  </p>
                </div>
                <AlertTriangle className={`h-8 w-8 ${getScoreColor(analysisResults.crime_score)}`} />
              </div>
            </div>
          </div>

          {analysisResults.summary && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">Analysis Summary</h3>
              <p className="text-gray-700">{analysisResults.summary}</p>
            </div>
          )}

          <div className="text-sm text-gray-500">
            Analysis completed on {new Date(analysisResults.timestamp).toLocaleString()}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisPanel;