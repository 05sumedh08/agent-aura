'use client';

import { Settings } from 'lucide-react';

export default function SettingsPage() {
  return (
    <div className="p-8">
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

      <div className="glass rounded-2xl p-12 text-center">
        <Settings className="w-16 h-16 mx-auto text-gray-400 mb-4" />
        <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">
          System Settings
        </h2>
        <p className="text-gray-500">
          Settings configuration coming soon.
        </p>
      </div>
    </div>
  );
}
