import React from 'react';

const statusConfig = {
  approved: { bg: 'bg-emerald-100', text: 'text-emerald-700', dot: 'bg-emerald-500' },
  pending: { bg: 'bg-amber-100', text: 'text-amber-700', dot: 'bg-amber-500' },
  rejected: { bg: 'bg-red-100', text: 'text-red-700', dot: 'bg-red-500' },
  processing: { bg: 'bg-blue-100', text: 'text-blue-700', dot: 'bg-blue-500' },
  shipped: { bg: 'bg-purple-100', text: 'text-purple-700', dot: 'bg-purple-500' },
  in_transit: { bg: 'bg-indigo-100', text: 'text-indigo-700', dot: 'bg-indigo-500' },
  out_for_delivery: { bg: 'bg-orange-100', text: 'text-orange-700', dot: 'bg-orange-500' },
  delivered: { bg: 'bg-emerald-100', text: 'text-emerald-700', dot: 'bg-emerald-500' },
  completed: { bg: 'bg-emerald-100', text: 'text-emerald-700', dot: 'bg-emerald-500' },
  confirmed: { bg: 'bg-emerald-100', text: 'text-emerald-700', dot: 'bg-emerald-500' },
  cancelled: { bg: 'bg-gray-100', text: 'text-gray-700', dot: 'bg-gray-500' },
  active: { bg: 'bg-emerald-100', text: 'text-emerald-700', dot: 'bg-emerald-500' },
};

export const StatusBadge = ({ status, size = 'normal' }) => {
  const config = statusConfig[status] || statusConfig.pending;
  
  return (
    <span 
      data-testid={`status-badge-${status}`}
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full ${size === 'small' ? 'text-xs' : 'text-sm'} font-medium ${config.bg} ${config.text}`}
    >
      <span className={`w-2 h-2 rounded-full ${config.dot}`}></span>
      {status?.replace('_', ' ').toUpperCase()}
    </span>
  );
};

export default StatusBadge;
