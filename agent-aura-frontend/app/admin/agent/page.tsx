'use client';

import { useState, useEffect } from 'react';
import { useAuth, useSession, useSettings } from '@/lib/store';
import { apiClient } from '@/lib/api';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import TrajectoryView from '@/components/TrajectoryView';
import SessionView from '@/components/SessionView';
import { Send, Sparkles, Settings, Users, AlertTriangle, Target, TrendingUp } from 'lucide-react';

interface Agent {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
}

export default function AgentPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const { selectedModel } = useSettings();
  const {
    streamEvents,
    isStreaming,
    sessions,
    addStreamEvent,
    clearStreamEvents,
    setIsStreaming,
    setSessions,
  } = useSession();

  const [goal, setGoal] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showAgentConfig, setShowAgentConfig] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | undefined>();
  const [agents, setAgents] = useState<Agent[]>([
    { id: 'data_collection', name: 'Data Collection Agent', description: 'Retrieves student data', enabled: true },
    { id: 'risk_analysis', name: 'Risk Analysis Agent', description: 'Evaluates risk level', enabled: true },
    { id: 'intervention_planning', name: 'Intervention Planning Agent', description: 'Designs strategies', enabled: true },
    { id: 'outcome_prediction', name: 'Outcome Prediction Agent', description: 'Forecasts success', enabled: true },
  ]);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    loadSessions();
  }, [isAuthenticated, router]);

  const loadSessions = async () => {
    try {
      const data = await apiClient.getSessions();
      setSessions(data);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goal.trim() || isStreaming) return;

    clearStreamEvents();
    setIsStreaming(true);

    try {
      // Get enabled agents
      const enabledAgentIds = agents.filter(a => a.enabled).map(a => a.id);

      const stream = apiClient.invokeAgent({
        goal: goal.trim(),
        enabled_agents: enabledAgentIds,
        model_override: selectedModel || undefined
      });

      for await (const event of stream) {
        addStreamEvent(event);
        // Track session ID from the first session_start event
        if (event.type === 'session_start' && event.session_id) {
          setCurrentSessionId(event.session_id);
        }
      }

      // Reload sessions after completion
      await loadSessions();
    } catch (error) {
      console.error('Streaming error:', error);
      addStreamEvent({
        type: 'error',
        content: 'Failed to communicate with agent. Please try again.',
        timestamp: new Date().toISOString(),
      });
    } finally {
      setIsStreaming(false);
    }
  };

  const toggleAgent = (agentId: string) => {
    setAgents(agents.map(a =>
      a.id === agentId ? { ...a, enabled: !a.enabled } : a
    ));
  };

  const getAgentIcon = (agentId: string) => {
    switch (agentId) {
      case 'data_collection': return Users;
      case 'risk_analysis': return AlertTriangle;
      case 'intervention_planning': return Target;
      case 'outcome_prediction': return TrendingUp;
      default: return Sparkles;
    }
  };

  const handleSessionClick = async (session: any) => {
    try {
      clearStreamEvents();
      setCurrentSessionId(session.session_id);
      const events = await apiClient.getSessionEvents(session.session_id);
      events.forEach(event => addStreamEvent(event));
    } catch (error) {
      console.error('Failed to load session events:', error);
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      await apiClient.deleteSession(sessionId);
      // Reload sessions after deletion
      await loadSessions();
      // Clear events if the deleted session was currently displayed
      if (streamEvents.length > 0) {
        clearStreamEvents();
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
      alert('Failed to delete session. Please try again.');
    }
  };

  const handleClearAllSessions = async () => {
    try {
      await apiClient.clearAllSessions();
      // Reload sessions after clearing all
      await loadSessions();
      // Clear displayed events
      clearStreamEvents();
    } catch (error) {
      console.error('Failed to clear sessions:', error);
      alert('Failed to clear sessions. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col">
        <Header onMenuClick={() => setSidebarOpen(true)} />

        <main className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left: Sessions */}
              <div className="lg:col-span-1">
                <SessionView
                  sessions={sessions}
                  onSelectSession={handleSessionClick}
                  onDeleteSession={handleDeleteSession}
                  onClearAllSessions={handleClearAllSessions}
                  currentSessionId={currentSessionId}
                />
              </div>

              {/* Right: Main Area */}
              <div className="lg:col-span-2 space-y-6">
                {/* Header */}
                <div className="glass-card rounded-3xl p-8 border border-white/10 animate-scale-in relative overflow-hidden bg-gradient-to-br from-white/5 to-white/0">
                  <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-purple-500/15 to-pink-500/15 rounded-full blur-3xl" />
                  <div className="flex items-center justify-between mb-6 relative z-10">
                    <div className="flex items-center gap-4">
                      <div className="p-4 glass rounded-2xl bg-gradient-to-r from-aura-primary to-aura-secondary shadow-2xl shadow-purple-500/60 animate-float">
                        <Sparkles className="w-8 h-8 text-white" />
                      </div>
                      <div>
                        <h1 className="text-4xl font-extrabold text-white mb-2 gradient-text tracking-tight">
                          AI Multi-Agent Assistant
                        </h1>
                        <p className="text-base text-gray-200 flex items-center gap-2 font-semibold">
                          <span className="inline-block w-2 h-2 bg-green-400 rounded-full pulse-dot" />
                          4 specialized agents working in parallel
                        </p>
                      </div>
                    </div>
                    {user?.role === 'admin' && (
                      <button
                        onClick={() => setShowAgentConfig(!showAgentConfig)}
                        className="p-2 glass rounded-xl hover:bg-white/5 transition-colors text-gray-400 hover:text-white"
                      >
                        <Settings className="w-5 h-5" />
                      </button>
                    )}
                  </div>

                  {/* Agent Configuration (Admin Only) */}
                  {showAgentConfig && user?.role === 'admin' && (
                    <div className="mb-6 p-6 glass rounded-xl border border-purple-400/30 bg-gradient-to-br from-purple-500/10 to-blue-500/10 shadow-lg">
                      <h3 className="font-bold mb-4 text-base text-gray-100">
                        Agent Configuration
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {agents.map((agent) => {
                          const Icon = getAgentIcon(agent.id);
                          return (
                            <div
                              key={agent.id}
                              className={`p-4 glass rounded-xl border transition-all ${agent.enabled
                                ? 'border-purple-400/60 bg-gradient-to-r from-aura-primary/15 to-aura-secondary/15'
                                : 'border-gray-600 opacity-50'
                                }`}
                            >
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3 flex-1">
                                  <Icon className={`w-5 h-5 ${agent.enabled ? 'text-purple-300' : 'text-gray-500'}`} />
                                  <div>
                                    <div className="font-bold text-base text-white">{agent.name}</div>
                                    <div className="text-sm text-gray-300 font-medium">{agent.description}</div>
                                  </div>
                                </div>
                                <button
                                  onClick={() => toggleAgent(agent.id)}
                                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${agent.enabled ? 'bg-aura-primary' : 'bg-gray-600'
                                    }`}
                                >
                                  <span
                                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${agent.enabled ? 'translate-x-6' : 'translate-x-1'
                                      }`}
                                  />
                                </button>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                      <div className="mt-4 text-sm text-gray-200 font-bold">
                        {agents.filter(a => a.enabled).length} / {agents.length} agents active
                      </div>
                    </div>
                  )}

                  {/* Input Form */}
                  <form onSubmit={handleSubmit} className="flex gap-3 relative z-10">
                    <div className="flex-1 relative group">
                      <input
                        type="text"
                        id="agent-goal-input"
                        name="goal"
                        autoComplete="off"
                        value={goal}
                        onChange={(e) => setGoal(e.target.value)}
                        placeholder="What would you like to know?"
                        className="w-full px-6 py-4 glass-card rounded-xl border border-white/20 bg-white/10 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-purple-400 text-white text-lg font-semibold placeholder-gray-400 transition-all duration-300 group-hover:border-white/30 shadow-lg"
                        disabled={isStreaming}
                      />
                      <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-purple-500/0 to-pink-500/0 group-hover:from-purple-500/5 group-hover:to-pink-500/5 pointer-events-none transition-all duration-300" />
                    </div>
                    <button
                      type="submit"
                      disabled={isStreaming || !goal.trim()}
                      className="px-8 py-4 bg-gradient-to-r from-aura-primary via-purple-600 to-aura-secondary text-white font-bold rounded-xl hover:shadow-2xl hover:shadow-purple-500/50 hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center gap-2 shadow-lg shadow-purple-500/50 relative overflow-hidden group"
                    >
                      <div className="absolute inset-0 bg-white/20 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                      <span className="relative z-10">
                        {isStreaming ? (
                          <>
                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                            <span className="font-semibold">Processing...</span>
                          </>
                        ) : (
                          <>
                            <Send className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                            <span className="font-semibold">Ask Agent</span>
                          </>
                        )}
                      </span>
                    </button>
                  </form>
                </div>

                {/* Trajectory View (Glass Box) */}
                <TrajectoryView events={streamEvents} isStreaming={isStreaming} sessionId={currentSessionId} />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
