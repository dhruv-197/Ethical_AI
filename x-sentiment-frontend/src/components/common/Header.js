import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BarChart3, Home, Users, Sparkles, Shield } from 'lucide-react';
import PostPortalLogo from '../../PostPortal.png';

const Header = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Home', icon: Home },
    { path: '/users', label: 'Community', icon: Users },
    { path: '/profile', label: 'View Profile', icon: Shield },
    { path: '/analysis', label: 'Insights Hub', icon: BarChart3 },
  ];

  return (
    <header className="glass border-b border-slate-200/50 sticky top-0 z-50">
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-20">
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="relative">
              <img 
                src={PostPortalLogo} 
                alt="PostPortal Logo" 
                className="h-12 w-12 group-hover:scale-110 transition-transform duration-300"
              />
              <Sparkles className="h-4 w-4 text-amber-400 absolute -top-1 -right-1 animate-pulse" />
            </div>
            <div className="flex flex-col">
              <span className="text-2xl font-bold gradient-text">PostPatrol</span>
              <span className="text-sm text-slate-500 font-medium">Watch. Detect. Protect.</span>
            </div>
          </Link>
          
          <nav className="flex space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300 ${
                    isActive
                      ? 'bg-slate-200/80 text-slate-700 shadow-lg backdrop-blur-sm border border-slate-300/50'
                      : 'text-slate-600 hover:text-slate-800 hover:bg-slate-100/80 backdrop-blur-sm border border-transparent hover:border-slate-300/50'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;