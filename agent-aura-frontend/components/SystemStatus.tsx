'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import { Activity, CheckCircle, XCircle } from 'lucide-react';

export default function SystemStatus() {
  const [status, setStatus] = useState<'healthy' | 'error' | 'checking'>('checking');
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const checkHealth = async () => {
    try {
      await apiClient.healthCheck();
      setStatus('healthy');
      setLastChecked(new Date());
    } catch (error) {
      console.error('Health check failed:', error);
      setStatus('error');
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 backdrop-blur-sm">
      {status === 'checking' && (
        <Activity className="w-4 h-4 text-blue-400 animate-pulse" />
      )}
      {status === 'healthy' && (
        <CheckCircle className="w-4 h-4 text-green-400" />
      )}
      {status === 'error' && (
        <XCircle className="w-4 h-4 text-red-400" />
      )}
      <span className={`text-xs font-medium ${
        status === 'healthy' ? 'text-green-400' : 
        status === 'error' ? 'text-red-400' : 'text-blue-400'
      }`}>
        {status === 'healthy' ? 'System Operational' : 
         status === 'error' ? 'System Issues' : 'Checking Status...'}
      </span>
    </div>
  );
}
