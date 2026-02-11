import React from 'react';

/**
 * Skeleton loading component for product cards
 */
export const ProductCardSkeleton = () => (
  <div className="bg-white rounded-xl shadow-lg overflow-hidden animate-pulse">
    {/* Image placeholder */}
    <div className="w-full h-48 bg-gray-200"></div>
    {/* Content */}
    <div className="p-4 space-y-3">
      {/* Brand */}
      <div className="h-3 bg-gray-200 rounded w-1/4"></div>
      {/* Title */}
      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
      {/* Rating */}
      <div className="flex items-center gap-2">
        <div className="h-4 w-16 bg-gray-200 rounded"></div>
        <div className="h-3 w-8 bg-gray-200 rounded"></div>
      </div>
      {/* Price */}
      <div className="h-6 bg-gray-200 rounded w-1/3"></div>
      {/* Button */}
      <div className="h-10 bg-gray-200 rounded w-full mt-4"></div>
    </div>
  </div>
);

/**
 * Skeleton loading component for product grid
 */
export const ProductGridSkeleton = ({ count = 8 }) => (
  <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
    {Array.from({ length: count }).map((_, i) => (
      <ProductCardSkeleton key={i} />
    ))}
  </div>
);

/**
 * Skeleton for dashboard stat cards
 */
export const StatCardSkeleton = () => (
  <div className="bg-white rounded-2xl shadow-lg p-6 animate-pulse">
    <div className="flex items-start justify-between">
      <div className="flex-1 space-y-3">
        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
        <div className="h-8 bg-gray-200 rounded w-2/3"></div>
        <div className="h-3 bg-gray-200 rounded w-1/3"></div>
      </div>
      <div className="w-14 h-14 bg-gray-200 rounded-2xl"></div>
    </div>
  </div>
);

/**
 * Skeleton for dashboard page
 */
export const DashboardSkeleton = () => (
  <div className="space-y-8 animate-pulse">
    {/* Stats grid */}
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <StatCardSkeleton key={i} />
      ))}
    </div>
    {/* Table */}
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <div className="h-6 bg-gray-200 rounded w-1/4 mb-6"></div>
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gray-200 rounded"></div>
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
            <div className="h-6 bg-gray-200 rounded w-20"></div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

/**
 * Skeleton for profile/user card
 */
export const ProfileSkeleton = () => (
  <div className="bg-white rounded-2xl shadow-lg p-6 animate-pulse">
    <div className="flex items-center gap-4 mb-6">
      <div className="w-20 h-20 bg-gray-200 rounded-full"></div>
      <div className="flex-1 space-y-2">
        <div className="h-6 bg-gray-200 rounded w-1/3"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      </div>
    </div>
    <div className="space-y-4">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="h-12 bg-gray-200 rounded"></div>
      ))}
    </div>
  </div>
);

/**
 * Skeleton for order list
 */
export const OrderListSkeleton = ({ count = 3 }) => (
  <div className="space-y-4 animate-pulse">
    {Array.from({ length: count }).map((_, i) => (
      <div key={i} className="bg-white rounded-xl shadow p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="h-5 bg-gray-200 rounded w-1/4"></div>
          <div className="h-6 bg-gray-200 rounded-full w-24"></div>
        </div>
        <div className="flex gap-3">
          {Array.from({ length: 2 }).map((_, j) => (
            <div key={j} className="w-16 h-16 bg-gray-200 rounded"></div>
          ))}
        </div>
        <div className="flex items-center justify-between mt-4">
          <div className="h-4 bg-gray-200 rounded w-1/3"></div>
          <div className="h-6 bg-gray-200 rounded w-20"></div>
        </div>
      </div>
    ))}
  </div>
);

/**
 * Skeleton for hero banner
 */
export const HeroBannerSkeleton = () => (
  <div className="w-full h-[400px] bg-gray-200 rounded-2xl animate-pulse">
    <div className="h-full flex flex-col justify-center items-start p-8 md:p-16 space-y-4">
      <div className="h-10 bg-gray-300 rounded w-3/4"></div>
      <div className="h-6 bg-gray-300 rounded w-1/2"></div>
      <div className="h-12 bg-gray-300 rounded w-32 mt-4"></div>
    </div>
  </div>
);

/**
 * Skeleton for category grid
 */
export const CategoryGridSkeleton = ({ count = 8 }) => (
  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 animate-pulse">
    {Array.from({ length: count }).map((_, i) => (
      <div key={i} className="relative h-40 bg-gray-200 rounded-xl overflow-hidden">
        <div className="absolute bottom-4 left-4 h-5 bg-gray-300 rounded w-2/3"></div>
      </div>
    ))}
  </div>
);

/**
 * Generic text line skeleton
 */
export const TextLineSkeleton = ({ width = 'w-full', height = 'h-4' }) => (
  <div className={`${width} ${height} bg-gray-200 rounded animate-pulse`}></div>
);

/**
 * Full page loading skeleton
 */
export const PageSkeleton = () => (
  <div className="min-h-screen bg-gray-50 p-4 md:p-8 animate-pulse">
    {/* Header placeholder */}
    <div className="h-16 bg-white shadow-sm rounded-lg mb-8"></div>
    
    {/* Content */}
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Hero */}
      <HeroBannerSkeleton />
      
      {/* Categories */}
      <div>
        <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
        <CategoryGridSkeleton count={4} />
      </div>
      
      {/* Products */}
      <div>
        <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
        <ProductGridSkeleton count={4} />
      </div>
    </div>
  </div>
);

export default {
  ProductCardSkeleton,
  ProductGridSkeleton,
  StatCardSkeleton,
  DashboardSkeleton,
  ProfileSkeleton,
  OrderListSkeleton,
  HeroBannerSkeleton,
  CategoryGridSkeleton,
  TextLineSkeleton,
  PageSkeleton,
};
