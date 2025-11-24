'use client';

import { useEffect, useState } from 'react';
import { useAuth, useStudents, useSettings } from '@/lib/store';
import { apiClient } from '@/lib/api';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import StudentCard from '@/components/StudentCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import { ModelSelector } from '@/components/ModelSelector';
import SystemStatus from '@/components/SystemStatus';
import { Users, AlertTriangle, TrendingUp, GraduationCap } from 'lucide-react';

export default function AdminDashboard() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const { students, setStudents, setSelectedStudent } = useStudents();
  const { selectedModel, setSelectedModel } = useSettings();
  const [isLoading, setIsLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (user?.role !== 'admin') {
      router.push(`/${user?.role}`);
      return;
    }

    loadStudents();
  }, [isAuthenticated, user, router]);

  const loadStudents = async () => {
    try {
      const response = await apiClient.getStudents();
      // Handle both array and {students: []} response formats
      const data = Array.isArray(response) ? response : (response as any).students || [];
      setStudents(data);
    } catch (error) {
      console.error('Failed to load students:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const stats = {
    total: students.length,
    critical: students.filter(s => s.latest_risk?.risk_level === 'CRITICAL').length,
    high: students.filter(s => s.latest_risk?.risk_level === 'HIGH').length,
    avgGPA: students.length > 0
      ? (students.reduce((sum, s) => sum + s.gpa, 0) / students.length).toFixed(2)
      : '0.00',
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col">
        <Header onMenuClick={() => setSidebarOpen(true)} />

        <main className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-7xl mx-auto space-y-6">
            {/* Page Header */}
            <div className="glass-card rounded-3xl p-8 border border-white/10 animate-scale-in bg-gradient-to-br from-white/5 to-white/0">
              <div className="flex items-center gap-4 mb-6">
                <div className="p-4 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 shadow-2xl shadow-purple-500/50 animate-float">
                  <Users className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h1 className="text-4xl font-extrabold text-white mb-2 tracking-tight">
                    Admin Dashboard
                  </h1>
                  <p className="text-gray-300 text-lg font-medium">
                    Monitor all students and system-wide metrics
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <SystemStatus />
                <ModelSelector
                  selectedModel={selectedModel}
                  onModelSelect={setSelectedModel}
                />
              </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="glass-card rounded-2xl p-6 border border-blue-400/40 bg-gradient-to-br from-blue-500/15 to-indigo-500/15 group hover:border-blue-400/60 transition-all duration-300 animate-slide-in-left">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 rounded-xl bg-blue-500/30 group-hover:bg-blue-500/40 transition-colors shadow-lg">
                    <Users className="w-8 h-8 text-blue-300 group-hover:scale-110 transition-transform" />
                  </div>
                  <span className="text-xs font-bold text-blue-200 bg-blue-500/20 px-3 py-1.5 rounded-full tracking-wider">
                    TOTAL
                  </span>
                </div>
                <div className="text-5xl font-extrabold text-white mb-2 group-hover:scale-105 transition-transform">
                  {stats.total}
                </div>
                <div className="text-base text-gray-200 font-semibold">
                  Students
                </div>
              </div>

              <div className="glass-card rounded-2xl p-6 border border-red-400/40 bg-gradient-to-br from-red-500/15 to-orange-500/15 group hover:border-red-400/60 transition-all duration-300 animate-slide-in-left" style={{ animationDelay: '0.1s' }}>
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 rounded-xl bg-red-500/30 group-hover:bg-red-500/40 transition-colors shadow-lg">
                    <AlertTriangle className="w-8 h-8 text-red-300 group-hover:scale-110 transition-transform animate-glow" />
                  </div>
                  <span className="text-xs font-bold text-red-200 bg-red-500/20 px-3 py-1.5 rounded-full tracking-wider">
                    CRITICAL
                  </span>
                </div>
                <div className="text-5xl font-extrabold text-white mb-2 group-hover:scale-105 transition-transform">
                  {stats.critical}
                </div>
                <div className="text-base text-gray-200 font-semibold">
                  At-Risk Students
                </div>
              </div>

              <div className="glass-card rounded-2xl p-6 border border-orange-400/40 bg-gradient-to-br from-orange-500/15 to-yellow-500/15 group hover:border-orange-400/60 transition-all duration-300 animate-slide-in-left" style={{ animationDelay: '0.2s' }}>
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 rounded-xl bg-orange-500/30 group-hover:bg-orange-500/40 transition-colors shadow-lg">
                    <TrendingUp className="w-8 h-8 text-orange-300 group-hover:scale-110 transition-transform" />
                  </div>
                  <span className="text-xs font-bold text-orange-200 bg-orange-500/20 px-3 py-1.5 rounded-full tracking-wider">
                    HIGH RISK
                  </span>
                </div>
                <div className="text-5xl font-extrabold text-white mb-2 group-hover:scale-105 transition-transform">
                  {stats.high}
                </div>
                <div className="text-base text-gray-200 font-semibold">
                  Need Attention
                </div>
              </div>

              <div className="glass-card rounded-2xl p-6 border border-green-400/40 bg-gradient-to-br from-green-500/15 to-emerald-500/15 group hover:border-green-400/60 transition-all duration-300 animate-slide-in-left" style={{ animationDelay: '0.3s' }}>
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 rounded-xl bg-green-500/30 group-hover:bg-green-500/40 transition-colors shadow-lg">
                    <GraduationCap className="w-8 h-8 text-green-300 group-hover:scale-110 transition-transform" />
                  </div>
                  <span className="text-xs font-bold text-green-200 bg-green-500/20 px-3 py-1.5 rounded-full tracking-wider">
                    AVG GPA
                  </span>
                </div>
                <div className="text-5xl font-extrabold text-white mb-2 group-hover:scale-105 transition-transform">
                  {stats.avgGPA}
                </div>
                <div className="text-base text-gray-200 font-semibold">
                  Overall Performance
                </div>
              </div>
            </div>

            {/* Students List */}
            <div className="glass-card rounded-3xl p-8 border border-white/10 animate-slide-up bg-gradient-to-br from-white/5 to-white/0">
              <div className="flex items-center gap-4 mb-8">
                <div className="p-3 rounded-xl bg-purple-500/30 shadow-lg">
                  <Users className="w-7 h-7 text-purple-300" />
                </div>
                <h2 className="text-3xl font-extrabold text-white tracking-tight">
                  All Students ({students.length})
                </h2>
              </div>

              {students.length === 0 ? (
                <div className="text-center py-12">
                  <Users className="w-16 h-16 mx-auto mb-4 text-gray-400 opacity-50" />
                  <p className="text-gray-400">
                    No students found
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {students.map((student) => (
                    <StudentCard
                      key={student.student_id}
                      student={student}
                      onClick={() => {
                        setSelectedStudent(student);
                        router.push(`/admin/students/${student.student_id}`);
                      }}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
