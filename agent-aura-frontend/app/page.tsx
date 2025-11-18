'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/store';
import { apiClient } from '@/lib/api';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, setUser } = useAuth();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const user = await apiClient.getCurrentUser();
        setUser(user);
        
        // Route based on role
        switch (user.role) {
          case 'admin':
            router.push('/admin');
            break;
          case 'teacher':
            router.push('/teacher');
            break;
          case 'student':
            router.push('/student');
            break;
          default:
            router.push('/login');
        }
      } catch (error) {
        router.push('/login');
      }
    };

    checkAuth();
  }, [router, setUser]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="glass rounded-3xl p-12 text-center">
        <div className="animate-pulse-slow">
          <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-gradient-to-r from-aura-primary to-aura-secondary" />
          <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-2">
            Agent Aura
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Loading your personalized dashboard...
          </p>
        </div>
      </div>
    </div>
  );
}
