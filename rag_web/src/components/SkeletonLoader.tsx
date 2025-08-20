'use client';

import React from 'react';

interface SkeletonLoaderProps {
  className?: string;
  lines?: number;
  height?: string;
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  className = '',
  lines = 1,
  height = 'h-4'
}) => {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className={`${height} bg-muted/20 rounded animate-pulse`}
          style={{
            animationDelay: `${index * 0.1}s`
          }}
        />
      ))}
    </div>
  );
};

export const MessageSkeleton: React.FC = () => (
  <div className="flex justify-start mb-6 animate-fade-in">
    <div className="max-w-3xl order-1">
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-muted/20 animate-pulse" />
        <div className="flex-1">
          <div className="bg-panel border border-ring/20 rounded-theme p-4 shadow-theme">
            <SkeletonLoader lines={3} height="h-3" />
            <div className="mt-3">
              <SkeletonLoader lines={1} height="h-2" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

export const SourceSkeleton: React.FC = () => (
  <div className="p-4 rounded-theme border border-ring/20 bg-panel animate-fade-in">
    <div className="space-y-3">
      <div className="flex items-center space-x-2">
        <div className="w-16 h-5 bg-muted/20 rounded-full animate-pulse" />
        <div className="w-20 h-5 bg-muted/20 rounded-full animate-pulse" />
      </div>
      <div className="w-3/4 h-4 bg-muted/20 rounded animate-pulse" />
      <div className="w-1/2 h-3 bg-muted/20 rounded animate-pulse" />
    </div>
  </div>
);
