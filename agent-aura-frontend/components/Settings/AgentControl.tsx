'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import { Bot, ToggleLeft, ToggleRight, Loader2 } from 'lucide-react';

interface AgentConfig {
    id: string;
    name: string;
    description: string;
    enabled: boolean;
}

export default function AgentControl() {
    const [agents, setAgents] = useState<AgentConfig[]>([]);
    const [loading, setLoading] = useState(true);
    const [toggling, setToggling] = useState<string | null>(null);

    useEffect(() => {
        fetchAgents();
    }, []);

    const fetchAgents = async () => {
        try {
            const response = await apiClient.getAgentConfig();
            setAgents(response.agents);
        } catch (error) {
            console.error('Failed to fetch agent config', error);
        } finally {
            setLoading(false);
        }
    };

    const toggleAgent = async (agentId: string, currentStatus: boolean) => {
        setToggling(agentId);
        try {
            await apiClient.updateAgentConfig(agentId, !currentStatus);

            setAgents(agents.map(agent =>
                agent.id === agentId ? { ...agent, enabled: !currentStatus } : agent
            ));
        } catch (error) {
            console.error('Failed to toggle agent', error);
        } finally {
            setToggling(null);
        }
    };

    if (loading) {
        return (
            <div className="glass rounded-2xl p-8 flex justify-center">
                <Loader2 className="w-8 h-8 text-aura-primary animate-spin" />
            </div>
        );
    }

    return (
        <div className="glass rounded-2xl p-8">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-3 rounded-xl bg-purple-500/20 text-purple-400">
                    <Bot className="w-6 h-6" />
                </div>
                <div>
                    <h2 className="text-xl font-bold text-white">Agent Configuration</h2>
                    <p className="text-sm text-gray-400">Enable or disable specific AI agents</p>
                </div>
            </div>

            <div className="space-y-4">
                {agents.map((agent) => (
                    <div
                        key={agent.id}
                        className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                    >
                        <div>
                            <h3 className="font-semibold text-white">{agent.name}</h3>
                            <p className="text-sm text-gray-400">{agent.description}</p>
                        </div>

                        <button
                            onClick={() => toggleAgent(agent.id, agent.enabled)}
                            disabled={toggling === agent.id}
                            className={`transition-colors ${agent.enabled ? 'text-green-400' : 'text-gray-500'
                                }`}
                        >
                            {toggling === agent.id ? (
                                <Loader2 className="w-8 h-8 animate-spin" />
                            ) : agent.enabled ? (
                                <ToggleRight className="w-8 h-8" />
                            ) : (
                                <ToggleLeft className="w-8 h-8" />
                            )}
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}
