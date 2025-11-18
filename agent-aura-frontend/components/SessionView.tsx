'use client';

import { AgentSession } from '@/lib/types';
import { Clock, CheckCircle, XCircle, Loader } from 'lucide-react';
import { format } from 'date-fns';

interface SessionViewProps {
  sessions: AgentSession[];
  onSelectSession: (session: AgentSession) => void;
  currentSessionId?: string;
}

export default function SessionView({ sessions, onSelectSession, currentSessionId }: SessionViewProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'active':
        return <Loader className="w-4 h-4 text-blue-500 animate-spin" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 dark:bg-green-900/30 border-green-500/30';
      case 'error':
        return 'bg-red-100 dark:bg-red-900/30 border-red-500/30';
      case 'active':
        return 'bg-blue-100 dark:bg-blue-900/30 border-blue-500/30';
      default:
        return 'bg-gray-100 dark:bg-gray-800/30 border-gray-500/30';
    }
  };

  if (sessions.length === 0) {
    return (
      <div className="glass rounded-3xl p-8 text-center">
        <Clock className="w-12 h-12 mx-auto mb-4 text-gray-400 opacity-50" />
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-2">
          No Session History
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Your conversation history will appear here
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="glass rounded-2xl p-4 mb-4">
        <h2 className="font-semibold text-gray-800 dark:text-white flex items-center gap-2">
          <Clock className="w-5 h-5" />
          Session History
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          {sessions.length} session{sessions.length !== 1 ? 's' : ''}
        </p>
      </div>

      <div className="space-y-2 max-h-[600px] overflow-y-auto pr-2">
        {sessions.map((session) => (
          <button
            key={session.session_id}
            onClick={() => onSelectSession(session)}
            className={`w-full glass border rounded-2xl p-4 text-left transition-all hover:scale-[1.02] hover:shadow-lg ${
              session.session_id === currentSessionId
                ? 'ring-2 ring-aura-primary bg-gradient-to-r from-aura-primary/10 to-aura-secondary/10'
                : ''
            } ${getStatusColor(session.status)}`}
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                {getStatusIcon(session.status)}
                <span className="text-xs font-semibold uppercase text-gray-600 dark:text-gray-400">
                  {session.status}
                </span>
              </div>
              <div className="text-xs font-mono glass px-2 py-1 rounded">
                {session.session_id.substring(0, 8)}
              </div>
            </div>

            {/* Goal */}
            <p className="text-sm font-medium text-gray-800 dark:text-white mb-3 line-clamp-2">
              {session.goal}
            </p>

            {/* Timestamps */}
            <div className="flex items-center gap-4 text-xs text-gray-600 dark:text-gray-400">
              <div className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {format(new Date(session.created_at), 'MMM d, HH:mm')}
              </div>
              {session.completed_at && (
                <div className="flex items-center gap-1">
                  <CheckCircle className="w-3 h-3" />
                  {format(new Date(session.completed_at), 'HH:mm')}
                </div>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
