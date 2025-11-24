'use client';

import { StreamEvent } from '@/lib/types';
import { Brain, Play, Eye, CheckCircle, Users, AlertTriangle, Target, TrendingUp, Zap, Download, FileText } from 'lucide-react';
import { format } from 'date-fns';
import ReactMarkdown from 'react-markdown';
import { apiClient } from '@/lib/api';

interface EventCardProps {
  event: StreamEvent;
  index: number;
}

export default function EventCard({ event, index }: EventCardProps) {
  const getIcon = () => {
    // Multi-agent events
    if (event.type === 'agent_start' || event.type === 'agent_complete') {
      const agentName = (event as any).agent_name || '';
      if (agentName.includes('Data Collection')) return <Users className="w-5 h-5 text-blue-500" />;
      if (agentName.includes('Risk Analysis')) return <AlertTriangle className="w-5 h-5 text-orange-500" />;
      if (agentName.includes('Intervention')) return <Target className="w-5 h-5 text-green-500" />;
      if (agentName.includes('Outcome')) return <TrendingUp className="w-5 h-5 text-purple-500" />;
    }

    if (event.type === 'orchestrator_thought') return <Zap className="w-5 h-5 text-yellow-500" />;
    if (event.type === 'final_report') return <CheckCircle className="w-5 h-5 text-indigo-500" />;

    // Original event types
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
    // Multi-agent events
    if (event.type === 'agent_start') return 'from-cyan-500/20 to-blue-600/20 border-cyan-500/30';
    if (event.type === 'agent_complete') return 'from-emerald-500/20 to-green-600/20 border-emerald-500/30';
    if (event.type === 'orchestrator_thought') return 'from-yellow-500/20 to-amber-600/20 border-yellow-500/30';
    if (event.type === 'final_report') return 'from-indigo-500/20 via-purple-500/20 to-pink-500/20 border-indigo-500/30';

    // Original event types
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
    // Multi-agent events
    if (event.type === 'agent_start') return `🚀 ${(event as any).agent_name || 'Agent'} Starting`;
    if (event.type === 'agent_complete') return `✅ ${(event as any).agent_name || 'Agent'} Complete`;
    if (event.type === 'orchestrator_thought') return '🧠 Orchestrator';
    if (event.type === 'final_report') return '📊 Comprehensive Report';

    // Original event types
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
          <div className="p-2 glass rounded-xl border border-white/5">{getIcon()}</div>
          <div>
            <h3 className="font-semibold text-white">
              {getTitle()}
            </h3>
            <p className="text-xs text-gray-400">
              {event.timestamp ? (() => {
                try {
                  return format(new Date(event.timestamp), 'HH:mm:ss');
                } catch {
                  return event.timestamp;
                }
              })() : 'N/A'}
            </p>
          </div>
        </div>
        <div className="text-xs font-mono glass px-3 py-1 rounded-full border border-white/5 text-gray-300">
          #{index + 1}
        </div>
      </div>

      {/* Content */}
      <div className="space-y-3">
        {/* Agent Start Event */}
        {event.type === 'agent_start' && (
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/5">
            <p className="text-sm text-gray-300 leading-relaxed">
              {(event as any).description || 'Agent starting execution...'}
            </p>
          </div>
        )}

        {/* Agent Complete Event */}
        {event.type === 'agent_complete' && (
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/5">
            <p className="text-xs font-semibold text-gray-400 mb-2">
              Result:
            </p>
            <pre className="text-xs text-gray-300 overflow-x-auto max-h-64 overflow-y-auto">
              {JSON.stringify((event as any).result, null, 2)}
            </pre>
          </div>
        )}

        {/* Orchestrator Thought */}
        {event.type === 'orchestrator_thought' && event.content && (
          <div className="bg-gradient-to-r from-yellow-900/20 to-amber-900/20 rounded-xl p-4 border border-yellow-500/20">
            <p className="text-sm text-gray-200 leading-relaxed font-medium">
              {event.content}
            </p>
          </div>
        )}

        {/* Final Report */}
        {event.type === 'final_report' && event.content && (
          <div className="bg-gradient-to-br from-indigo-900/30 via-purple-900/30 to-pink-900/30 rounded-xl p-6 border border-purple-500/20">
            <div className="prose prose-sm prose-invert max-w-none mb-6">
              <ReactMarkdown>{event.content}</ReactMarkdown>
            </div>

            {/* Download Buttons */}
            <div className="flex gap-3 pt-4 border-t border-white/10">
              <button
                onClick={() => event.session_id && apiClient.exportSessionPDF(event.session_id)}
                className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors text-sm text-white font-medium"
              >
                <FileText className="w-4 h-4" />
                Download PDF
              </button>
              <button
                onClick={() => event.session_id && apiClient.exportSessionCSV(event.session_id)}
                className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors text-sm text-white font-medium"
              >
                <Download className="w-4 h-4" />
                Download CSV
              </button>
            </div>
          </div>
        )}

        {/* Original event types */}
        {event.type === 'thought' && event.content && (
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/5">
            <p className="text-sm text-gray-300 leading-relaxed">
              {event.content}
            </p>
          </div>
        )}

        {event.type === 'action' && (
          <>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-gray-400">
                Tool:
              </span>
              <span className="font-mono text-sm bg-blue-900/30 px-3 py-1 rounded-lg border border-blue-500/20 text-blue-300">
                {event.tool}
              </span>
            </div>
            {event.tool_input && (
              <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/5">
                <p className="text-xs font-semibold text-gray-400 mb-2">
                  Input:
                </p>
                <pre className="text-xs text-gray-300 overflow-x-auto">
                  {JSON.stringify(event.tool_input, null, 2)}
                </pre>
              </div>
            )}
          </>
        )}

        {event.type === 'observation' && event.result && (
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/5">
            <p className="text-xs font-semibold text-gray-400 mb-2">
              Result:
            </p>
            <pre className="text-xs text-gray-300 overflow-x-auto max-h-48 overflow-y-auto">
              {typeof event.result === 'string'
                ? event.result
                : JSON.stringify(event.result, null, 2)}
            </pre>
          </div>
        )}

        {event.type === 'response' && event.response && (
          <div className="bg-gradient-to-br from-indigo-900/30 to-purple-900/30 rounded-xl p-4 border border-purple-500/20">
            <p className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap">
              {event.response}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
