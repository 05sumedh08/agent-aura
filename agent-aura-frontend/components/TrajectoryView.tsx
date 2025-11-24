'use client';

import { StreamEvent } from '@/lib/types';
import EventCard from './EventCard';
import { Sparkles, Download, FileText } from 'lucide-react';
import { apiClient } from '@/lib/api';

interface TrajectoryViewProps {
  events: StreamEvent[];
  isStreaming: boolean;
  sessionId?: string;
}

export default function TrajectoryView({ events, isStreaming, sessionId }: TrajectoryViewProps) {
  const handleExportPDF = () => {
    if (!sessionId) return;
    apiClient.exportSessionPDF(sessionId);
  };

  const handleExportCSV = () => {
    if (!sessionId) return;
    apiClient.exportSessionCSV(sessionId);
  };

  if (events.length === 0 && !isStreaming) {
    return (
      <div className="glass rounded-3xl p-12 text-center border border-white/5">
        <Sparkles className="w-16 h-16 mx-auto mb-4 text-aura-primary opacity-50" />
        <h3 className="text-xl font-semibold text-white mb-2">
          No Active Session
        </h3>
        <p className="text-gray-400">
          Ask a question to see the agent's thinking process in real-time
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="glass rounded-2xl p-4 flex items-center justify-between border border-white/5">
        <div className="flex items-center gap-3">
          <div className="p-2 glass rounded-xl bg-gradient-to-r from-aura-primary to-aura-secondary shadow-lg shadow-purple-500/50">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-white">
              Agent Trajectory
            </h2>
            <p className="text-sm text-gray-400">
              Think-Act-Observe Loop
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isStreaming && (
            <div className="flex items-center gap-2 mr-4">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse shadow-lg shadow-green-500/50" />
              <span className="text-sm text-gray-400">
                Streaming...
              </span>
            </div>
          )}
          {!isStreaming && sessionId && events.length > 0 && (
            <>
              <button
                onClick={handleExportPDF}
                className="px-3 py-2 text-sm glass rounded-lg hover:bg-white/5 transition-colors flex items-center gap-2 text-gray-400 hover:text-white"
                title="Download as PDF"
              >
                <FileText className="w-4 h-4" />
                PDF
              </button>
              <button
                onClick={handleExportCSV}
                className="px-3 py-2 text-sm glass rounded-lg hover:bg-white/5 transition-colors flex items-center gap-2 text-gray-400 hover:text-white"
                title="Download as CSV"
              >
                <Download className="w-4 h-4" />
                CSV
              </button>
            </>
          )}
        </div>
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
        <div className="glass rounded-2xl p-6 border border-white/5">
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-400">
                {events.filter(e => e.type === 'thought').length}
              </div>
              <div className="text-xs text-gray-400">
                Thoughts
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-400">
                {events.filter(e => e.type === 'action').length}
              </div>
              <div className="text-xs text-gray-400">
                Actions
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">
                {events.filter(e => e.type === 'observation').length}
              </div>
              <div className="text-xs text-gray-400">
                Observations
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">
                {events.length}
              </div>
              <div className="text-xs text-gray-400">
                Total Steps
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
