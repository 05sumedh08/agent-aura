'use client';

import { useEffect, useState } from 'react';
import { useAuth, useStudents } from '@/lib/store';
import { apiClient } from '@/lib/api';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import StudentCard from '@/components/StudentCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import { Users, AlertTriangle, BookOpen, Award } from 'lucide-react';

export default function TeacherDashboard() {
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

    if (user?.role !== 'teacher') {
      router.push(`/${user?.role || 'login'}`);
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
    atRisk: students.filter(s => 
      s.latest_risk?.risk_level === 'CRITICAL' || 
      s.latest_risk?.risk_level === 'HIGH'
    ).length,
    avgGPA: students.length > 0 
      ? (students.reduce((sum, s) => sum + s.gpa, 0) / students.length).toFixed(2)
      : '0.00',
    lowAttendance: students.filter(s => s.attendance < 90).length,
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
                Teacher Dashboard
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Welcome back, {user?.full_name || 'Teacher'}
              </p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="glass rounded-2xl p-6 border border-blue-500/30 bg-gradient-to-br from-blue-500/10 to-indigo-500/10">
                <div className="flex items-center justify-between mb-4">
                  <Users className="w-8 h-8 text-blue-500" />
                  <span className="text-xs font-semibold text-blue-600 dark:text-blue-400">
                    MY STUDENTS
                  </span>
                </div>
                <div className="text-3xl font-bold text-gray-800 dark:text-white">
                  {stats.total}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  In Your Classes
                </div>
              </div>

              <div className="glass rounded-2xl p-6 border border-red-500/30 bg-gradient-to-br from-red-500/10 to-orange-500/10">
                <div className="flex items-center justify-between mb-4">
                  <AlertTriangle className="w-8 h-8 text-red-500" />
                  <span className="text-xs font-semibold text-red-600 dark:text-red-400">
                    AT RISK
                  </span>
                </div>
                <div className="text-3xl font-bold text-gray-800 dark:text-white">
                  {stats.atRisk}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Need Intervention
                </div>
              </div>

              <div className="glass rounded-2xl p-6 border border-green-500/30 bg-gradient-to-br from-green-500/10 to-emerald-500/10">
                <div className="flex items-center justify-between mb-4">
                  <Award className="w-8 h-8 text-green-500" />
                  <span className="text-xs font-semibold text-green-600 dark:text-green-400">
                    AVG GPA
                  </span>
                </div>
                <div className="text-3xl font-bold text-gray-800 dark:text-white">
                  {stats.avgGPA}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Class Average
                </div>
              </div>

              <div className="glass rounded-2xl p-6 border border-orange-500/30 bg-gradient-to-br from-orange-500/10 to-yellow-500/10">
                <div className="flex items-center justify-between mb-4">
                  <BookOpen className="w-8 h-8 text-orange-500" />
                  <span className="text-xs font-semibold text-orange-600 dark:text-orange-400">
                    ATTENDANCE
                  </span>
                </div>
                <div className="text-3xl font-bold text-gray-800 dark:text-white">
                  {stats.lowAttendance}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Below 90%
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="glass rounded-3xl p-6">
              <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4">
                Quick Actions
              </h2>
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={() => router.push('/admin/agent')}
                  className="px-6 py-3 bg-gradient-to-r from-aura-primary to-aura-secondary text-white font-semibold rounded-xl hover:opacity-90 transition-opacity"
                >
                  🤖 Run AI Analysis
                </button>
                <button
                  onClick={() => loadStudents()}
                  className="px-6 py-3 glass border border-gray-300 dark:border-gray-700 text-gray-800 dark:text-white font-semibold rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  🔄 Refresh Data
                </button>
              </div>
            </div>

            {/* Students List */}
            <div className="glass rounded-3xl p-6">
              <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4">
                My Students ({students.length})
              </h2>
              
              {students.length === 0 ? (
                <div className="text-center py-12">
                  <Users className="w-16 h-16 mx-auto mb-4 text-gray-400 opacity-50" />
                  <p className="text-gray-600 dark:text-gray-400">
                    No students assigned to your classes
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
                        router.push(`/teacher/students/${student.student_id}`);
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
