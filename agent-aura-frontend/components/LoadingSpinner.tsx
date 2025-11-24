'use client';

export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center p-12 gap-6">
      <div className="relative">
        {/* Outer ring */}
        <div className="w-20 h-20 border-4 border-purple-500/20 rounded-full" />
        {/* Middle spinning ring */}
        <div className="absolute top-0 left-0 w-20 h-20 border-4 border-aura-primary border-t-transparent rounded-full animate-spin" />
        {/* Inner reverse spinning ring */}
        <div className="absolute top-2 left-2 w-16 h-16 border-4 border-pink-500/50 border-t-transparent rounded-full animate-spin" style={{animationDirection: 'reverse', animationDuration: '1.5s'}} />
        {/* Center glow */}
        <div className="absolute top-1/2 left-1/2 w-8 h-8 -translate-x-1/2 -translate-y-1/2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full blur-lg animate-pulse" />
      </div>
      
      {/* Loading dots */}
      <div className="flex items-center gap-2">
        <div className="w-2.5 h-2.5 bg-purple-500 rounded-full animate-bounce shadow-lg shadow-purple-500/50" />
        <div className="w-2.5 h-2.5 bg-purple-500 rounded-full animate-bounce shadow-lg shadow-purple-500/50" style={{animationDelay: '0.1s'}} />
        <div className="w-2.5 h-2.5 bg-purple-500 rounded-full animate-bounce shadow-lg shadow-purple-500/50" style={{animationDelay: '0.2s'}} />
      </div>
      
      {/* Loading text */}
      <p className="text-gray-300 text-base font-medium animate-pulse">Loading your experience...</p>
    </div>
  );
}
