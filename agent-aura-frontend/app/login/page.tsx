'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';
import { useAuth } from '@/lib/store';

export default function LoginPage() {
  const router = useRouter();
  const { setUser } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await apiClient.login({ username, password });
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
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen p-4 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-float" />
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl animate-float" style={{animationDelay: '1s'}} />
      
      <div className="glass-card rounded-3xl p-8 md:p-12 w-full max-w-md relative z-10 animate-scale-in shadow-2xl border border-white/10">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-24 h-24 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-aura-primary via-purple-600 to-aura-secondary flex items-center justify-center shadow-2xl shadow-purple-500/50 animate-float">
            <svg
              className="w-12 h-12 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2.5}
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
          </div>
          <h1 className="text-4xl font-bold text-white mb-3 gradient-text">
            Agent Aura
          </h1>
          <p className="text-gray-400 text-lg">
            AI-Powered Student Success Platform
          </p>
          <div className="mt-4 h-1 w-24 mx-auto bg-gradient-to-r from-transparent via-purple-500 to-transparent rounded-full" />
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-xl backdrop-blur-sm animate-slide-in-left">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                {error}
              </div>
            </div>
          )}

          <div className="space-y-2">
            <label
              htmlFor="username"
              className="block text-base font-bold text-gray-100 mb-3"
            >
              Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-5 py-4 rounded-xl glass-card border border-white/10 focus:outline-none focus:ring-2 focus:ring-aura-primary focus:border-aura-primary text-white placeholder-gray-500 transition-all duration-300 hover:border-white/20"
              placeholder="Enter your username"
              required
            />
          </div>

          <div className="space-y-2">
            <label
              htmlFor="password"
              className="block text-sm font-semibold text-gray-300 mb-2"
            >
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-5 py-4 rounded-xl glass-card border border-white/10 focus:outline-none focus:ring-2 focus:ring-aura-primary focus:border-aura-primary text-white placeholder-gray-500 transition-all duration-300 hover:border-white/20"
              placeholder="Enter your password"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-aura-primary via-purple-600 to-aura-secondary text-white font-bold py-4 rounded-xl hover:shadow-2xl hover:shadow-purple-500/50 hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 relative overflow-hidden group"
          >
            <div className="absolute inset-0 bg-white/20 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
            <span className="relative z-10">
              {isLoading ? (
                <span className="flex items-center justify-center">
                  <svg
                    className="animate-spin h-5 w-5 mr-2"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Signing in...
                </span>
              ) : (
                'Sign In'
              )}
            </span>
          </button>
        </form>

        {/* Demo Credentials */}
        <div className="mt-8 p-5 glass-card border border-blue-500/20 bg-gradient-to-br from-blue-500/5 to-purple-500/5 rounded-xl">
          <div className="flex items-center gap-2 mb-3">
            <svg className="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <p className="text-sm font-bold text-blue-300">
              Demo Credentials
            </p>
          </div>
          <div className="text-sm text-gray-300 space-y-2 font-mono">
            <div className="flex justify-between p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
              <span className="text-gray-400">Admin:</span>
              <span className="text-white">admin / admin123</span>
            </div>
            <div className="flex justify-between p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
              <span className="text-gray-400">Teacher:</span>
              <span className="text-white">teacher1 / teacher123</span>
            </div>
            <div className="flex justify-between p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
              <span className="text-gray-400">Student:</span>
              <span className="text-white">student1 / student1123</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
