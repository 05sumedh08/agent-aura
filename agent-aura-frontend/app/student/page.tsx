'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/lib/store';
import { apiClient } from '@/lib/api';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import RiskBadge from '@/components/RiskBadge';
import LoadingSpinner from '@/components/LoadingSpinner';
import { 
  User, 
  TrendingUp, 
  Calendar, 
  Award,
  AlertCircle,
  CheckCircle,
  Target
} from 'lucide-react';

export default function StudentDashboard() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [studentData, setStudentData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (user?.role !== 'student') {
      router.push(`/${user?.role || 'login'}`);
      return;
    }

    loadStudentData();
  }, [isAuthenticated, user, router]);

  const loadStudentData = async () => {
    try {
      if (user?.student_id) {
        const data = await apiClient.getStudentDetail(user.student_id);
        setStudentData(data);
      }
    } catch (error) {
      console.error('Failed to load student data:', error);
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

  const riskLevel = studentData?.latest_risk?.risk_level || 'LOW';
  const riskScore = studentData?.latest_risk?.risk_score || 0;

  return (
    <div className="min-h-screen flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      <div className="flex-1 flex flex-col">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        
        <main className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-7xl mx-auto space-y-6">
            {/* Welcome Header */}
            <div className="glass rounded-3xl p-6">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-gradient-to-r from-aura-primary to-aura-secondary flex items-center justify-center">
                  <User className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-800 dark:text-white">
                    Welcome, {studentData?.full_name || 'Student'}!
                  </h1>
                  <p className="text-gray-600 dark:text-gray-400">
                    Grade {studentData?.grade || 'N/A'} • {studentData?.student_id || ''}
                  </p>
                </div>
              </div>
            </div>

            {/* Academic Status */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="glass rounded-2xl p-6 border border-green-500/30 bg-gradient-to-br from-green-500/10 to-emerald-500/10">
                <div className="flex items-center justify-between mb-4">
                  <Award className="w-8 h-8 text-green-500" />
                  <span className="text-xs font-semibold text-green-600 dark:text-green-400">
                    GPA
                  </span>
                </div>
                <div className="text-3xl font-bold text-gray-800 dark:text-white">
                  {studentData?.gpa?.toFixed(2) || '0.00'}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Current Grade Point Average
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
                  {studentData?.attendance?.toFixed(0) || '0'}%
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Days Present This Semester
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
                  {(studentData?.performance_score || 0).toFixed(0)}%
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Overall Performance Score
                </div>
              </div>

              <div className={`glass rounded-2xl p-6 border ${
                riskLevel === 'CRITICAL' ? 'border-red-500/30 bg-gradient-to-br from-red-500/10 to-orange-500/10' :
                riskLevel === 'HIGH' ? 'border-orange-500/30 bg-gradient-to-br from-orange-500/10 to-yellow-500/10' :
                riskLevel === 'MODERATE' ? 'border-yellow-500/30 bg-gradient-to-br from-yellow-500/10 to-green-500/10' :
                'border-green-500/30 bg-gradient-to-br from-green-500/10 to-emerald-500/10'
              }`}>
                <div className="flex items-center justify-between mb-4">
                  {riskLevel === 'LOW' ? (
                    <CheckCircle className="w-8 h-8 text-green-500" />
                  ) : (
                    <AlertCircle className={`w-8 h-8 ${
                      riskLevel === 'CRITICAL' ? 'text-red-500' :
                      riskLevel === 'HIGH' ? 'text-orange-500' :
                      'text-yellow-500'
                    }`} />
                  )}
                  <RiskBadge level={riskLevel} size="sm" />
                </div>
                <div className="text-3xl font-bold text-gray-800 dark:text-white">
                  {(riskScore * 100).toFixed(0)}%
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Current Risk Score
                </div>
              </div>
            </div>

            {/* Academic Status Card */}
            <div className="glass rounded-3xl p-6">
              <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                <Target className="w-6 h-6" />
                Academic Status & Recommendations
              </h2>
              
              {riskLevel === 'LOW' ? (
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-2xl p-6">
                  <div className="flex items-start gap-4">
                    <CheckCircle className="w-8 h-8 text-green-500 flex-shrink-0 mt-1" />
                    <div>
                      <h3 className="text-lg font-semibold text-green-800 dark:text-green-300 mb-2">
                        Great Work! Keep It Up! 🎉
                      </h3>
                      <p className="text-green-700 dark:text-green-400 mb-4">
                        You're doing excellent academically! Your current performance shows strong engagement and understanding.
                      </p>
                      <div className="space-y-2">
                        <p className="text-sm text-green-600 dark:text-green-500">
                          ✓ Maintain your current study habits
                        </p>
                        <p className="text-sm text-green-600 dark:text-green-500">
                          ✓ Continue attending classes regularly
                        </p>
                        <p className="text-sm text-green-600 dark:text-green-500">
                          ✓ Consider helping peers who may need support
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className={`${
                  riskLevel === 'CRITICAL' ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800' :
                  riskLevel === 'HIGH' ? 'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800' :
                  'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'
                } border rounded-2xl p-6`}>
                  <div className="flex items-start gap-4">
                    <AlertCircle className={`w-8 h-8 flex-shrink-0 mt-1 ${
                      riskLevel === 'CRITICAL' ? 'text-red-500' :
                      riskLevel === 'HIGH' ? 'text-orange-500' :
                      'text-yellow-500'
                    }`} />
                    <div>
                      <h3 className={`text-lg font-semibold mb-2 ${
                        riskLevel === 'CRITICAL' ? 'text-red-800 dark:text-red-300' :
                        riskLevel === 'HIGH' ? 'text-orange-800 dark:text-orange-300' :
                        'text-yellow-800 dark:text-yellow-300'
                      }`}>
                        {riskLevel === 'CRITICAL' ? 'Immediate Attention Required' :
                         riskLevel === 'HIGH' ? 'Academic Support Recommended' :
                         'Consider Additional Support'}
                      </h3>
                      <p className={`mb-4 ${
                        riskLevel === 'CRITICAL' ? 'text-red-700 dark:text-red-400' :
                        riskLevel === 'HIGH' ? 'text-orange-700 dark:text-orange-400' :
                        'text-yellow-700 dark:text-yellow-400'
                      }`}>
                        Your current academic performance indicates you may benefit from additional support.
                        We're here to help you succeed!
                      </p>
                      <div className="space-y-2">
                        <p className={`text-sm ${
                          riskLevel === 'CRITICAL' ? 'text-red-600 dark:text-red-500' :
                          riskLevel === 'HIGH' ? 'text-orange-600 dark:text-orange-500' :
                          'text-yellow-600 dark:text-yellow-500'
                        }`}>
                          → Schedule a meeting with your teacher
                        </p>
                        <p className={`text-sm ${
                          riskLevel === 'CRITICAL' ? 'text-red-600 dark:text-red-500' :
                          riskLevel === 'HIGH' ? 'text-orange-600 dark:text-orange-500' :
                          'text-yellow-600 dark:text-yellow-500'
                        }`}>
                          → Visit the tutoring center for extra help
                        </p>
                        <p className={`text-sm ${
                          riskLevel === 'CRITICAL' ? 'text-red-600 dark:text-red-500' :
                          riskLevel === 'HIGH' ? 'text-orange-600 dark:text-orange-500' :
                          'text-yellow-600 dark:text-yellow-500'
                        }`}>
                          → Create a structured study schedule
                        </p>
                        {studentData?.attendance < 90 && (
                          <p className={`text-sm ${
                            riskLevel === 'CRITICAL' ? 'text-red-600 dark:text-red-500' :
                            riskLevel === 'HIGH' ? 'text-orange-600 dark:text-orange-500' :
                            'text-yellow-600 dark:text-yellow-500'
                          }`}>
                            → Improve attendance (current: {studentData.attendance.toFixed(0)}%)
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
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
                  🎯 Request Analysis
                </button>
                <button
                  onClick={() => loadStudentData()}
                  className="px-6 py-3 glass border border-gray-300 dark:border-gray-700 text-gray-800 dark:text-white font-semibold rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  🔄 Refresh Status
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
