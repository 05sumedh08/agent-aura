'use client';

import { StreamEvent } from '@/lib/types';
import { Brain, Play, Eye, CheckCircle } from 'lucide-react';
import { format } from 'date-fns';

interface EventCardProps {
  event: StreamEvent;
  index: number;
}

export default function EventCard({ event, index }: EventCardProps) {
  const getIcon = () => {
    switch (event.type) {
      case 'thought':
        return <Brain className="w-5 h-5 text-purple-500" />;
      case 'action':
        return <Play className="w-5 h-5 text-blue-500" />;
      case 'observation':
        return <Eye className="w-5 h-5 text-green-500" />;
      case 'response':
        return <CheckCircle className="w-5 h-5 text-indigo-500" />;
      default:
        return <Brain className="w-5 h-5 text-gray-500" />;
    }
  };

  const getColor = () => {
    switch (event.type) {
      case 'thought':
        return 'from-purple-500/20 to-purple-600/20 border-purple-500/30';
      case 'action':
        return 'from-blue-500/20 to-blue-600/20 border-blue-500/30';
      case 'observation':
        return 'from-green-500/20 to-green-600/20 border-green-500/30';
      case 'response':
        return 'from-indigo-500/20 to-indigo-600/20 border-indigo-500/30';
      default:
        return 'from-gray-500/20 to-gray-600/20 border-gray-500/30';
    }
  };

  const getTitle = () => {
    switch (event.type) {
      case 'thought':
        return 'Thinking';
      case 'action':
        return 'Action';
      case 'observation':
        return 'Observation';
      case 'response':
        return 'Final Response';
      default:
        return event.type;
    }
  };

  return (
    <div
      className={`glass border bg-gradient-to-br ${getColor()} rounded-2xl p-6 animate-slide-up`}
      style={{ animationDelay: `${index * 100}ms` }}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 glass rounded-xl">{getIcon()}</div>
          <div>
            <h3 className="font-semibold text-gray-800 dark:text-white">
              {getTitle()}
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {format(new Date(event.timestamp), 'HH:mm:ss')}
            </p>
          </div>
        </div>
        <div className="text-xs font-mono glass px-3 py-1 rounded-full">
          #{index + 1}
        </div>
      </div>

      {/* Content */}
      <div className="space-y-3">
        {event.type === 'thought' && event.content && (
          <div className="bg-white/50 dark:bg-gray-800/50 rounded-xl p-4">
            <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
              {event.content}
            </p>
          </div>
        )}

        {event.type === 'action' && (
          <>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-gray-600 dark:text-gray-400">
                Tool:
              </span>
              <span className="font-mono text-sm bg-blue-100 dark:bg-blue-900/30 px-3 py-1 rounded-lg">
                {event.tool}
              </span>
            </div>
            {event.tool_input && (
              <div className="bg-white/50 dark:bg-gray-800/50 rounded-xl p-4">
                <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">
                  Input:
                </p>
                <pre className="text-xs text-gray-700 dark:text-gray-300 overflow-x-auto">
                  {JSON.stringify(event.tool_input, null, 2)}
                </pre>
              </div>
            )}
          </>
        )}

        {event.type === 'observation' && event.result && (
          <div className="bg-white/50 dark:bg-gray-800/50 rounded-xl p-4">
            <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">
              Result:
            </p>
            <pre className="text-xs text-gray-700 dark:text-gray-300 overflow-x-auto max-h-48 overflow-y-auto">
              {typeof event.result === 'string'
                ? event.result
                : JSON.stringify(event.result, null, 2)}
            </pre>
          </div>
        )}

        {event.type === 'response' && event.response && (
          <div className="bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/30 dark:to-purple-900/30 rounded-xl p-4">
            <p className="text-sm text-gray-800 dark:text-gray-200 leading-relaxed whitespace-pre-wrap">
              {event.response}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
