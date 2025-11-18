'use client';

import { useState, useEffect } from 'react';
import { useAuth, useSession } from '@/lib/store';
import { apiClient } from '@/lib/api';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import TrajectoryView from '@/components/TrajectoryView';
import SessionView from '@/components/SessionView';
import { Send, Sparkles } from 'lucide-react';

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
      const stream = apiClient.invokeAgent({ goal: goal.trim() });
      
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
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-3 glass rounded-xl bg-gradient-to-r from-aura-primary to-aura-secondary">
                      <Sparkles className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
                        AI Agent Assistant
                      </h1>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Ask questions about students, risk assessment, or interventions
                      </p>
                    </div>
                  </div>

                  {/* Input Form */}
                  <form onSubmit={handleSubmit} className="flex gap-3">
                    <input
                      type="text"
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
