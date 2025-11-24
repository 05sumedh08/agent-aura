'use client';

import { Settings } from 'lucide-react';
import ApiKeyManager from '@/components/Settings/ApiKeyManager';
import AgentControl from '@/components/Settings/AgentControl';

export default function SettingsPage() {
  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Settings className="w-8 h-8 text-aura-primary" />
          <h1 className="text-3xl font-bold bg-gradient-to-r from-aura-primary to-aura-secondary bg-clip-text text-transparent">
            Settings
          </h1>
        </div>
        <p className="text-gray-600 dark:text-gray-400">
          Configure system settings and preferences
        </p>
      </div>

      <ApiKeyManager />
      <AgentControl />
    </div>
  );
}
