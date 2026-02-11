import React from 'react';
import { Link } from 'react-router-dom';
import { Clock, X, Star, ArrowRight } from 'lucide-react';
import { useRecentlyViewed } from '../hooks/useRecentlyViewed';

/**
 * Recently Viewed Products Component
 * Shows products the user has recently viewed
 */
const RecentlyViewed = ({ maxItems = 4, showClear = true, className = '' }) => {
  const { recentlyViewed, clearRecentlyViewed, removeFromRecentlyViewed } = useRecentlyViewed();

  if (recentlyViewed.length === 0) {
    return null;
  }

  const displayedProducts = recentlyViewed.slice(0, maxItems);

  return (
    <section 
      data-testid="recently-viewed-section"
      className={`bg-white rounded-2xl shadow-lg border border-gray-100 p-6 ${className}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-amber-100 rounded-xl">
            <Clock className="w-5 h-5 text-amber-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Recently Viewed</h2>
            <p className="text-sm text-gray-500">Continue where you left off</p>
          </div>
        </div>
        {showClear && recentlyViewed.length > 0 && (
          <button
            onClick={clearRecentlyViewed}
            data-testid="clear-recently-viewed"
            className="text-sm text-gray-500 hover:text-red-500 transition-colors"
          >
            Clear all
          </button>
        )}
      </div>

      {/* Products Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {displayedProducts.map((product) => (
          <Link
            key={product.id}
            to={`/products/${product.id}`}
            data-testid={`recently-viewed-product-${product.id}`}
            className="group relative bg-gray-50 rounded-xl overflow-hidden hover:shadow-md transition-all"
          >
            {/* Remove button */}
            <button
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                removeFromRecentlyViewed(product.id);
              }}
              className="absolute top-2 right-2 z-10 p-1 bg-white/80 rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-100"
            >
              <X className="w-3 h-3 text-gray-500 hover:text-red-500" />
            </button>

            {/* Product Image */}
            <div className="aspect-square overflow-hidden">
              <img
                src={product.image || '/placeholder.png'}
                alt={product.name}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
            </div>

            {/* Product Info */}
            <div className="p-3">
              <p className="text-xs text-emerald-600 font-medium truncate">{product.brand}</p>
              <h3 className="font-semibold text-gray-900 text-sm truncate mt-1">{product.name}</h3>
              <div className="flex items-center justify-between mt-2">
                <span className="text-emerald-600 font-bold">£{product.price?.toFixed(2)}</span>
                {product.rating && (
                  <div className="flex items-center gap-1 text-xs text-gray-500">
                    <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                    {product.rating.toFixed(1)}
                  </div>
                )}
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* View All Link */}
      {recentlyViewed.length > maxItems && (
        <div className="mt-4 text-center">
          <Link
            to="/products"
            className="inline-flex items-center gap-2 text-emerald-600 hover:text-emerald-700 font-medium text-sm"
          >
            View all recently viewed
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      )}
    </section>
  );
};

export default RecentlyViewed;
