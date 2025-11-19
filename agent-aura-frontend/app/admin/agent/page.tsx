'use client';

import { useState, useEffect } from 'react';
import { useAuth, useSession } from '@/lib/store';
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
        enabled_agents: enabledAgentIds
      });
      
      for await (const event of stream) {
        addStreamEvent(event);
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
    switch(agentId) {
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
      const events = await apiClient.getSessionEvents(session.session_id);
      events.forEach(event => addStreamEvent(event));
    } catch (error) {
      console.error('Failed to load session events:', error);
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
                />
              </div>

              {/* Right: Main Area */}
              <div className="lg:col-span-2 space-y-6">
                {/* Header */}
                <div className="glass rounded-3xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="p-3 glass rounded-xl bg-gradient-to-r from-aura-primary to-aura-secondary">
                        <Sparkles className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
                          AI Multi-Agent Assistant
                        </h1>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          4 specialized agents working in parallel
                        </p>
                      </div>
                    </div>
                    {user?.role === 'admin' && (
                      <button
                        onClick={() => setShowAgentConfig(!showAgentConfig)}
                        className="p-2 glass rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                      >
                        <Settings className="w-5 h-5" />
                      </button>
                    )}
                  </div>

                  {/* Agent Configuration (Admin Only) */}
                  {showAgentConfig && user?.role === 'admin' && (
                    <div className="mb-4 p-4 glass rounded-xl border border-gray-200 dark:border-gray-700">
                      <h3 className="font-semibold mb-3 text-sm text-gray-700 dark:text-gray-300">
                        Agent Configuration
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {agents.map((agent) => {
                          const Icon = getAgentIcon(agent.id);
                          return (
                            <div
                              key={agent.id}
                              className={`p-3 glass rounded-xl border transition-all ${
                                agent.enabled
                                  ? 'border-aura-primary bg-aura-primary bg-opacity-5'
                                  : 'border-gray-300 dark:border-gray-600 opacity-50'
                              }`}
                            >
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2 flex-1">
                                  <Icon className="w-4 h-4" />
                                  <div>
                                    <div className="font-medium text-sm">{agent.name}</div>
                                    <div className="text-xs text-gray-500">{agent.description}</div>
                                  </div>
                                </div>
                                <button
                                  onClick={() => toggleAgent(agent.id)}
                                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                                    agent.enabled ? 'bg-aura-primary' : 'bg-gray-300'
                                  }`}
                                >
                                  <span
                                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                                      agent.enabled ? 'translate-x-6' : 'translate-x-1'
                                    }`}
                                  />
                                </button>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                      <div className="mt-3 text-xs text-gray-500">
                        {agents.filter(a => a.enabled).length} / {agents.length} agents active
                      </div>
                    </div>
                  )}

                  {/* Input Form */}
                  <form onSubmit={handleSubmit} className="flex gap-3">
                    <input
                      type="text"
                      id="agent-goal-input"
                      name="goal"
                      autoComplete="off"
                      value={goal}
                      onChange={(e) => setGoal(e.target.value)}
                      placeholder="What would you like to know?"
                      className="flex-1 px-4 py-3 glass rounded-xl border border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-aura-primary"
                      disabled={isStreaming}
                    />
                    <button
                      type="submit"
                      disabled={isStreaming || !goal.trim()}
                      className="px-6 py-3 bg-gradient-to-r from-aura-primary to-aura-secondary text-white font-semibold rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      {isStreaming ? (
                        <>
                          <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          Processing...
                        </>
                      ) : (
                        <>
                          <Send className="w-5 h-5" />
                          Ask
                        </>
                      )}
                    </button>
                  </form>
                </div>

                {/* Trajectory View (Glass Box) */}
                <TrajectoryView events={streamEvents} isStreaming={isStreaming} />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
