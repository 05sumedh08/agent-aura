'use client';

import { useRouter, usePathname } from 'next/navigation';
import { Home, Users, BarChart3, MessageSquare, Settings, X } from 'lucide-react';
import { useAuth } from '@/lib/store';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export default function Sidebar({ isOpen = true, onClose }: SidebarProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();

  const getMenuItems = () => {
    const baseItems = [
      { icon: Home, label: 'Dashboard', path: `/${user?.role}` },
      { icon: MessageSquare, label: 'Ask AI Agent', path: `/${user?.role}/agent` },
    ];

    if (user?.role === 'admin') {
      return [
        ...baseItems,
        { icon: Users, label: 'All Students', path: '/admin/students' },
        { icon: Users, label: 'Teachers', path: '/admin/teachers' },
        { icon: BarChart3, label: 'Analytics', path: '/admin/analytics' },
        { icon: Settings, label: 'Settings', path: '/admin/settings' },
      ];
    } else if (user?.role === 'teacher') {
      return [
        ...baseItems,
        { icon: Users, label: 'My Students', path: '/teacher/students' },
        { icon: BarChart3, label: 'Class Analytics', path: '/teacher/analytics' },
      ];
    } else {
      return [
        ...baseItems,
        { icon: BarChart3, label: 'My Progress', path: '/student/progress' },
      ];
    }
  };

  const menuItems = getMenuItems();

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && onClose && (
        <div
          className="fixed inset-0 bg-black/50 lg:hidden z-40"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:sticky top-0 left-0 h-screen bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-r border-gray-200 dark:border-gray-700 z-50 transition-transform ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        } w-64`}
      >
        <div className="flex flex-col h-full p-4">
          {/* Close button for mobile */}
          {onClose && (
            <button
              onClick={onClose}
              className="lg:hidden self-end p-2 glass rounded-xl mb-4"
            >
              <X className="w-5 h-5" />
            </button>
          )}

          {/* Navigation */}
          <nav className="flex-1 space-y-2">
            {menuItems.map((item) => {
              const isActive = pathname === item.path;
              return (
                <button
                  key={item.path}
                  onClick={() => {
                    router.push(item.path);
                    onClose?.();
                  }}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                    isActive
                      ? 'bg-gradient-to-r from-aura-primary to-aura-secondary text-white shadow-lg'
                      : 'glass hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300'
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Footer */}
          <div className="glass rounded-xl p-4 text-center">
            <p className="text-xs text-gray-600 dark:text-gray-400">
              Agent Aura v2.0
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
              Powered by AI
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}
