import React from 'react';
import { BookOpen, Clock } from 'lucide-react';

const CommunityOutreach = ({ analysisData }) => {
  return (
    <div className="card p-6">
      <div className="flex items-center space-x-3 mb-6">
        <div className="p-3 bg-gradient-to-r from-orange-500 to-amber-500 rounded-xl">
          <BookOpen className="h-6 w-6 text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-bold gradient-text">Community Outreach</h2>
          <p className="text-slate-600 text-sm">AI-powered community outreach analysis</p>
        </div>
      </div>

      <div className="text-center py-16">
        <div className="mb-8">
          <div className="relative inline-block mb-6">
            <BookOpen className="h-20 w-20 text-slate-300 mx-auto" />
            <Clock className="h-8 w-8 text-orange-500 absolute -top-2 -right-2" />
          </div>
          <h3 className="text-2xl font-bold text-slate-800 mb-4">Coming Soon</h3>
          <p className="text-slate-600 text-lg mb-6 max-w-md mx-auto">
            We're working hard to bring you advanced community outreach analysis features. 
            This module will help you understand and improve community engagement patterns.
          </p>
        </div>
        
        <div className="bg-gradient-to-r from-orange-50 to-amber-50 rounded-xl p-6 max-w-lg mx-auto">
          <h4 className="font-semibold text-slate-800 mb-3">What's Coming:</h4>
          <ul className="text-left text-slate-600 space-y-2">
            <li className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
              <span>Educational program analysis</span>
            </li>
            <li className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
              <span>Community initiative tracking</span>
            </li>
            <li className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
              <span>Impact metrics and reporting</span>
            </li>
            <li className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
              <span>Resource sharing and collaboration tools</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default CommunityOutreach; 