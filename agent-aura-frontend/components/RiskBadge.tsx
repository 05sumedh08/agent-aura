'use client';

import { RiskBadgeProps } from '@/lib/types';
import { AlertTriangle } from 'lucide-react';

export default function RiskBadge({ level, score }: RiskBadgeProps) {
  const getColor = () => {
    switch (level) {
      case 'CRITICAL':
        return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 border-red-500';
      case 'HIGH':
        return 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 border-orange-500';
      case 'MODERATE':
        return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 border-yellow-500';
      case 'LOW':
        return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 border-green-500';
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

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border-2 font-semibold text-sm ${getColor()}`}
    >
      {(level === 'CRITICAL' || level === 'HIGH') && (
        <AlertTriangle className="w-4 h-4" />
      )}
      <span>
        {level} {getIntensity()}
      </span>
      {score !== undefined && (
        <span className="font-mono text-xs opacity-75">({score.toFixed(2)})</span>
      )}
    </div>
  );
}
