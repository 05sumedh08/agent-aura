'use client';

import { RiskBadgeProps } from '@/lib/types';
import { AlertTriangle } from 'lucide-react';

export default function RiskBadge({ level, score, size = 'md' }: RiskBadgeProps) {
  const getColor = () => {
    switch (level) {
      case 'CRITICAL':
        return 'bg-gradient-to-r from-red-500/30 to-orange-500/30 text-red-200 border-red-400/60 shadow-xl shadow-red-500/30';
      case 'HIGH':
        return 'bg-gradient-to-r from-orange-500/30 to-yellow-500/30 text-orange-200 border-orange-400/60 shadow-xl shadow-orange-500/30';
      case 'MODERATE':
        return 'bg-gradient-to-r from-yellow-500/30 to-green-500/30 text-yellow-200 border-yellow-400/60 shadow-xl shadow-yellow-500/30';
      case 'LOW':
        return 'bg-gradient-to-r from-green-500/30 to-emerald-500/30 text-green-200 border-green-400/60 shadow-xl shadow-green-500/30';
    }
  };

  const getIntensity = () => {
    switch (level) {
      case 'CRITICAL':
        return '!!!';
      case 'HIGH':
        return '!!';
      case 'MODERATE':
        return '!';
      case 'LOW':
        return '';
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'px-2 py-1 text-xs';
      case 'lg':
        return 'px-4 py-2 text-base';
      default:
        return 'px-3 py-1.5 text-sm';
    }
  };

  return (
    <div
      className={`inline-flex items-center gap-2 ${getSizeClasses()} rounded-xl border-2 font-extrabold ${getColor()} backdrop-blur-sm transition-all duration-300 hover:scale-105 hover:shadow-2xl`}
    >
      {(level === 'CRITICAL' || level === 'HIGH') && (
        <AlertTriangle className={`${size === 'sm' ? 'w-4 h-4' : 'w-5 h-5'} ${level === 'CRITICAL' ? 'animate-glow' : ''}`} />
      )}
      <span className="tracking-wider">
        {level} {getIntensity()}
      </span>
      {score !== undefined && (
        <span className="font-mono text-sm font-bold opacity-90 bg-black/30 px-2.5 py-1 rounded-md">
          {score.toFixed(2)}
        </span>
      )}
    </div>
  );
}
