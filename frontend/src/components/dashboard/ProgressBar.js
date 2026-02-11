import React from 'react';

const colorClasses = {
  emerald: 'bg-emerald-500',
  blue: 'bg-blue-500',
  purple: 'bg-purple-500',
  orange: 'bg-orange-500',
};

export const ProgressBar = ({ value, max, color = 'emerald', showLabel = true }) => {
  const percentage = max > 0 ? (value / max) * 100 : 0;
  
  return (
    <div className="w-full">
      <div className="flex justify-between mb-1">
        {showLabel && <span className="text-sm text-gray-600">{value}</span>}
        {showLabel && <span className="text-sm text-gray-400">{percentage.toFixed(0)}%</span>}
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className={`${colorClasses[color]} h-2 rounded-full transition-all duration-500`} 
          style={{ width: `${Math.min(percentage, 100)}%` }}
        ></div>
      </div>
    </div>
  );
};

export default ProgressBar;
