'use client';

import { useEffect, useState } from 'react';
import { useAuth, useStudents } from '@/lib/store';
import { apiClient } from '@/lib/api';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import StudentCard from '@/components/StudentCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import { Users, AlertTriangle, TrendingUp, GraduationCap } from 'lucide-react';

export default function AdminDashboard() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const { students, setStudents, setSelectedStudent } = useStudents();
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
      const data = await apiClient.getStudents();
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
            <div className="glass rounded-3xl p-6">
              <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-2">
                Admin Dashboard
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Monitor all students and system-wide metrics
              </p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="glass rounded-2xl p-6 border border-blue-500/30 bg-gradient-to-br from-blue-500/10 to-indigo-500/10">
                <div className="flex items-center justify-between mb-4">
                  <Users className="w-8 h-8 text-blue-500" />
                  <span className="text-xs font-semibold text-blue-600 dark:text-blue-400">
                    TOTAL
                  </span>
                </div>
                <div className="text-3xl font-bold text-gray-800 dark:text-white">
                  {stats.total}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Students
                </div>
              </div>

              <div className="glass rounded-2xl p-6 border border-red-500/30 bg-gradient-to-br from-red-500/10 to-orange-500/10">
                <div className="flex items-center justify-between mb-4">
                  <AlertTriangle className="w-8 h-8 text-red-500" />
                  <span className="text-xs font-semibold text-red-600 dark:text-red-400">
                    CRITICAL
                  </span>
                </div>
                <div className="text-3xl font-bold text-gray-800 dark:text-white">
                  {stats.critical}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  At-Risk Students
                </div>
              </div>

              <div className="glass rounded-2xl p-6 border border-orange-500/30 bg-gradient-to-br from-orange-500/10 to-yellow-500/10">
                <div className="flex items-center justify-between mb-4">
                  <TrendingUp className="w-8 h-8 text-orange-500" />
                  <span className="text-xs font-semibold text-orange-600 dark:text-orange-400">
                    HIGH RISK
                  </span>
                </div>
                <div className="text-3xl font-bold text-gray-800 dark:text-white">
                  {stats.high}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Need Attention
                </div>
              </div>

              <div className="glass rounded-2xl p-6 border border-green-500/30 bg-gradient-to-br from-green-500/10 to-emerald-500/10">
                <div className="flex items-center justify-between mb-4">
                  <GraduationCap className="w-8 h-8 text-green-500" />
                  <span className="text-xs font-semibold text-green-600 dark:text-green-400">
                    AVG GPA
                  </span>
                </div>
                <div className="text-3xl font-bold text-gray-800 dark:text-white">
                  {stats.avgGPA}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Overall Performance
                </div>
              </div>
            </div>

            {/* Students List */}
            <div className="glass rounded-3xl p-6">
              <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4">
                All Students ({students.length})
              </h2>
              
              {students.length === 0 ? (
                <div className="text-center py-12">
                  <Users className="w-16 h-16 mx-auto mb-4 text-gray-400 opacity-50" />
                  <p className="text-gray-600 dark:text-gray-400">
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
