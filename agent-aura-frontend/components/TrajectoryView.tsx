'use client';

import { StreamEvent } from '@/lib/types';
import EventCard from './EventCard';
import { Sparkles } from 'lucide-react';

interface TrajectoryViewProps {
  events: StreamEvent[];
  isStreaming: boolean;
}

export default function TrajectoryView({ events, isStreaming }: TrajectoryViewProps) {
  if (events.length === 0 && !isStreaming) {
    return (
      <div className="glass rounded-3xl p-12 text-center">
        <Sparkles className="w-16 h-16 mx-auto mb-4 text-aura-primary opacity-50" />
        <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-2">
          No Active Session
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          Ask a question to see the agent's thinking process in real-time
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="glass rounded-2xl p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 glass rounded-xl bg-gradient-to-r from-aura-primary to-aura-secondary">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-800 dark:text-white">
              Agent Trajectory
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Think-Act-Observe Loop
            </p>
          </div>
        </div>
        {isStreaming && (
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Streaming...
            </span>
          </div>
        )}
      </div>

      {/* Timeline */}
      <div className="relative space-y-4">
        {/* Vertical line */}
        <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-purple-500 via-blue-500 to-green-500 opacity-20" />
        
        {/* Events */}
        <div className="space-y-4 relative">
          {events.map((event, index) => (
            <EventCard key={index} event={event} index={index} />
          ))}
        </div>

        {/* Loading indicator */}
        {isStreaming && (
          <div className="glass rounded-2xl p-6 border border-purple-500/30 bg-gradient-to-br from-purple-500/10 to-blue-500/10 animate-pulse">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full animate-spin" />
              <div className="flex-1">
                <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-3/4 mb-2" />
                <div className="h-3 bg-gray-300 dark:bg-gray-700 rounded w-1/2" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Stats */}
      {events.length > 0 && !isStreaming && (
        <div className="glass rounded-2xl p-6">
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-500">
                {events.filter(e => e.type === 'thought').length}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">
                Thoughts
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-500">
                {events.filter(e => e.type === 'action').length}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">
                Actions
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-500">
                {events.filter(e => e.type === 'observation').length}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">
                Observations
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-700 dark:text-gray-300">
                {events.length}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">
                Total Steps
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
