import React from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

const colorClasses = {
  emerald: 'from-emerald-500 to-emerald-600',
  blue: 'from-blue-500 to-blue-600',
  purple: 'from-purple-500 to-purple-600',
  orange: 'from-orange-500 to-orange-600',
  pink: 'from-pink-500 to-pink-600',
  indigo: 'from-indigo-500 to-indigo-600',
  yellow: 'from-yellow-500 to-yellow-600',
  red: 'from-red-500 to-red-600',
};

export const StatCard = ({ 
  title, 
  value, 
  subtitle, 
  icon: Icon, 
  trend, 
  trendValue, 
  color = 'emerald', 
  size = 'normal' 
}) => {
  return (
    <div 
      data-testid={`stat-card-${title.toLowerCase().replace(/\s+/g, '-')}`}
      className={`relative overflow-hidden bg-white rounded-2xl shadow-lg border border-gray-100 ${size === 'large' ? 'p-8' : 'p-6'} hover:shadow-xl transition-all duration-300 group`}
    >
      <div className="absolute top-0 right-0 w-32 h-32 transform translate-x-8 -translate-y-8">
        <div className={`w-full h-full rounded-full bg-gradient-to-br ${colorClasses[color]} opacity-10 group-hover:opacity-20 transition-opacity`}></div>
      </div>
      <div className="relative flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-500 uppercase tracking-wider">{title}</p>
          <p className={`${size === 'large' ? 'text-4xl' : 'text-3xl'} font-bold text-gray-900 mt-2`}>{value}</p>
          {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
          {trend && (
            <div className={`flex items-center mt-3 ${trend === 'up' ? 'text-emerald-600' : 'text-red-500'}`}>
              {trend === 'up' ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
              <span className="text-sm font-semibold ml-1">{trendValue}</span>
              <span className="text-xs text-gray-500 ml-2">vs last period</span>
            </div>
          )}
        </div>
        <div className={`p-4 rounded-2xl bg-gradient-to-br ${colorClasses[color]} shadow-lg`}>
          <Icon className="w-7 h-7 text-white" />
        </div>
      </div>
    </div>
  );
};

export default StatCard;
