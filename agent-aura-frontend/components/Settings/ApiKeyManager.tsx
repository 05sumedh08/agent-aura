'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import { Key, Check, AlertCircle, Trash2, Save } from 'lucide-react';

export default function ApiKeyManager() {
    const [apiKey, setApiKey] = useState('');
    const [isSet, setIsSet] = useState(false);
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

    useEffect(() => {
        checkStatus();
    }, []);

    const checkStatus = async () => {
        try {
            const status = await apiClient.getApiKeyStatus();
            setIsSet(status.is_set);
        } catch (error) {
            console.error('Failed to check API key status', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        if (!apiKey) return;
        setLoading(true);
        setMessage(null);
        try {
            await apiClient.updateApiKey(apiKey);
            setIsSet(true);
            setApiKey('');
            setMessage({ type: 'success', text: 'API Key updated successfully' });
        } catch (error) {
            setMessage({ type: 'error', text: 'Failed to update API Key' });
        } finally {
            setLoading(false);
        }
    };

    const handleRemove = async () => {
        if (!confirm('Are you sure you want to remove the API Key? The system will stop working.')) return;
        setLoading(true);
        setMessage(null);
        try {
            await apiClient.removeApiKey();
            setIsSet(false);
            setMessage({ type: 'success', text: 'API Key removed successfully' });
        } catch (error) {
            setMessage({ type: 'error', text: 'Failed to remove API Key' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="glass rounded-2xl p-8 mb-8">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-3 rounded-xl bg-indigo-500/20 text-indigo-400">
                    <Key className="w-6 h-6" />
                </div>
                <div>
                    <h2 className="text-xl font-bold text-white">Gemini API Key</h2>
                    <p className="text-sm text-gray-400">Manage your Google Gemini API connection</p>
                </div>
                <div className={`ml-auto px-3 py-1 rounded-full text-xs font-medium border ${isSet
                        ? 'bg-green-500/10 border-green-500/20 text-green-400'
                        : 'bg-red-500/10 border-red-500/20 text-red-400'
                    }`}>
                    {loading ? 'Checking...' : isSet ? 'Active' : 'Not Configured'}
                </div>
            </div>

            <div className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                        API Key
                    </label>
                    <div className="flex gap-3">
                        <input
                            type="password"
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            placeholder={isSet ? "••••••••••••••••••••••••" : "Enter your Gemini API Key"}
                            className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-aura-primary/50"
                        />
                        <button
                            onClick={handleSave}
                            disabled={loading || !apiKey}
                            className="btn-primary flex items-center gap-2"
                        >
                            <Save className="w-4 h-4" />
                            Save
                        </button>
                        {isSet && (
                            <button
                                onClick={handleRemove}
                                disabled={loading}
                                className="px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 transition-colors"
                            >
                                <Trash2 className="w-4 h-4" />
                            </button>
                        )}
                    </div>
                </div>

                {message && (
                    <div className={`flex items-center gap-2 text-sm ${message.type === 'success' ? 'text-green-400' : 'text-red-400'
                        }`}>
                        {message.type === 'success' ? <Check className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                        {message.text}
                    </div>
                )}
            </div>
        </div>
    );
}
