'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '@/lib/store';
import { apiClient } from '@/lib/api';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import RiskBadge from '@/components/RiskBadge';
import LoadingSpinner from '@/components/LoadingSpinner';
import { 
  ArrowLeft, 
  User, 
  GraduationCap, 
  Calendar,
  TrendingUp,
  Mail,
  Phone,
  AlertCircle,
  Target,
  Activity
} from 'lucide-react';
import type { Student } from '@/lib/types';

export default function StudentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { isAuthenticated, user } = useAuth();
  const [student, setStudent] = useState<Student | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (user?.role !== 'admin') {
      router.push(`/${user?.role || 'login'}`);
      return;
    }

    loadStudent();
  }, [isAuthenticated, user, router, params.id]);

  const loadStudent = async () => {
    try {
      const studentId = params.id as string;
      const data = await apiClient.getStudentDetail(studentId);
      setStudent(data);
    } catch (error) {
      console.error('Failed to load student:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (!student) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 mx-auto mb-4 text-red-500" />
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-2">
            Student Not Found
          </h2>
          <button
            onClick={() => router.push('/admin')}
            className="mt-4 px-6 py-3 bg-gradient-to-r from-aura-primary to-aura-secondary text-white rounded-xl hover:opacity-90 transition-opacity"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const riskLevel = student.latest_risk?.risk_level || 'LOW';
  const riskScore = student.latest_risk?.risk_score || 0;

  return (
    <div className="min-h-screen flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      <div className="flex-1 flex flex-col">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        
        <main className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-7xl mx-auto space-y-6">
            {/* Back Button */}
            <button
              onClick={() => router.push('/admin')}
              className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-aura-primary transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              Back to Dashboard
            </button>

            {/* Student Header */}
            <div className="glass rounded-3xl p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-20 h-20 rounded-full bg-gradient-to-r from-aura-primary to-aura-secondary flex items-center justify-center">
                    <User className="w-10 h-10 text-white" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-1">
                      {student.full_name}
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400">
                      Student ID: {student.student_id} • Grade {student.grade}
                    </p>
                  </div>
                </div>
                <RiskBadge level={riskLevel as any} score={riskScore} />
              </div>
            </div>

            {/* Academic Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="glass rounded-2xl p-6 border border-green-500/30 bg-gradient-to-br from-green-500/10 to-emerald-500/10">
                <div className="flex items-center justify-between mb-4">
                  <GraduationCap className="w-8 h-8 text-green-500" />
                  <span className="text-xs font-semibold text-green-600 dark:text-green-400">
                    GPA
                  </span>
                </div>
                <div className="text-3xl font-bold text-gray-800 dark:text-white">
                  {student.gpa.toFixed(2)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Grade Point Average
                </div>
              </div>

              <div className="glass rounded-2xl p-6 border border-blue-500/30 bg-gradient-to-br from-blue-500/10 to-indigo-500/10">
                <div className="flex items-center justify-between mb-4">
                  <Calendar className="w-8 h-8 text-blue-500" />
                  <span className="text-xs font-semibold text-blue-600 dark:text-blue-400">
                    ATTENDANCE
                  </span>
                </div>
                <div className="text-3xl font-bold text-gray-800 dark:text-white">
                  {student.attendance.toFixed(0)}%
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Days Present
                </div>
              </div>

              <div className="glass rounded-2xl p-6 border border-purple-500/30 bg-gradient-to-br from-purple-500/10 to-pink-500/10">
                <div className="flex items-center justify-between mb-4">
                  <TrendingUp className="w-8 h-8 text-purple-500" />
                  <span className="text-xs font-semibold text-purple-600 dark:text-purple-400">
                    PERFORMANCE
                  </span>
                </div>
                <div className="text-3xl font-bold text-gray-800 dark:text-white">
                  {(student.performance_score || 0).toFixed(0)}%
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Overall Score
                </div>
              </div>

              <div className={`glass rounded-2xl p-6 border ${
                riskLevel === 'CRITICAL' ? 'border-red-500/30 bg-gradient-to-br from-red-500/10 to-orange-500/10' :
                riskLevel === 'HIGH' ? 'border-orange-500/30 bg-gradient-to-br from-orange-500/10 to-yellow-500/10' :
                riskLevel === 'MODERATE' ? 'border-yellow-500/30 bg-gradient-to-br from-yellow-500/10 to-green-500/10' :
                'border-green-500/30 bg-gradient-to-br from-green-500/10 to-emerald-500/10'
              }`}>
                <div className="flex items-center justify-between mb-4">
                  <Activity className={`w-8 h-8 ${
                    riskLevel === 'CRITICAL' ? 'text-red-500' :
                    riskLevel === 'HIGH' ? 'text-orange-500' :
                    riskLevel === 'MODERATE' ? 'text-yellow-500' :
                    'text-green-500'
                  }`} />
                  <span className={`text-xs font-semibold ${
                    riskLevel === 'CRITICAL' ? 'text-red-600 dark:text-red-400' :
                    riskLevel === 'HIGH' ? 'text-orange-600 dark:text-orange-400' :
                    riskLevel === 'MODERATE' ? 'text-yellow-600 dark:text-yellow-400' :
                    'text-green-600 dark:text-green-400'
                  }`}>
                    RISK LEVEL
                  </span>
                </div>
                <div className="text-3xl font-bold text-gray-800 dark:text-white">
                  {(riskScore * 100).toFixed(0)}%
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Risk Score
                </div>
              </div>
            </div>

            {/* Contact Information */}
            <div className="glass rounded-3xl p-6">
              <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4">
                Contact Information
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center gap-3">
                  <Mail className="w-5 h-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Parent Email</p>
                    <p className="text-gray-800 dark:text-white font-medium">
                      {student.parent_email || 'Not provided'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Phone className="w-5 h-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Parent Phone</p>
                    <p className="text-gray-800 dark:text-white font-medium">
                      {student.parent_phone || 'Not provided'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Risk Analysis */}
            {student.latest_risk && (
              <div className="glass rounded-3xl p-6">
                <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                  <Target className="w-6 h-6" />
                  Risk Analysis
                </h2>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      Last Assessment: {new Date(student.latest_risk.assessed_at!).toLocaleDateString()}
                    </p>
                    <p className="text-gray-800 dark:text-white">
                      This student has been assessed at <strong>{riskLevel}</strong> risk level 
                      with a score of <strong>{(riskScore * 100).toFixed(0)}%</strong>.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Quick Actions */}
            <div className="glass rounded-3xl p-6">
              <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4">
                Quick Actions
              </h2>
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={() => router.push(`/admin/agent?student=${student.student_id}`)}
                  className="px-6 py-3 bg-gradient-to-r from-aura-primary to-aura-secondary text-white font-semibold rounded-xl hover:opacity-90 transition-opacity"
                >
                  🤖 Run AI Analysis
                </button>
                <button
                  onClick={() => loadStudent()}
                  className="px-6 py-3 glass border border-gray-300 dark:border-gray-700 text-gray-800 dark:text-white font-semibold rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  🔄 Refresh Data
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
