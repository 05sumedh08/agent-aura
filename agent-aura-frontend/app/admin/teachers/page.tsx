'use client';

import { useState, useEffect } from 'react';
import { Users, TrendingUp, AlertCircle, CheckCircle, BookOpen, Award } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { Student } from '@/lib/types';
import LoadingSpinner from '@/components/LoadingSpinner';
import RiskBadge from '@/components/RiskBadge';

interface TeacherStats {
  totalStudents: number;
  avgGPA: number;
  avgAttendance: number;
  criticalRisk: number;
  highRisk: number;
  moderateRisk: number;
  lowRisk: number;
}

export default function TeachersPage() {
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<TeacherStats>({
    totalStudents: 0,
    avgGPA: 0,
    avgAttendance: 0,
    criticalRisk: 0,
    highRisk: 0,
    moderateRisk: 0,
    lowRisk: 0
  });

  useEffect(() => {
    loadTeacherData();
  }, []);

  async function loadTeacherData() {
    try {
      setLoading(true);
      const data = await apiClient.getAllStudents();
      setStudents(data);

      // Calculate statistics
      const total = data.length;
      const avgGPA = data.reduce((sum, s) => sum + s.gpa, 0) / total;
      const avgAttendance = data.reduce((sum, s) => sum + s.attendance, 0) / total;

      // Calculate risk levels based on GPA and attendance
      let critical = 0, high = 0, moderate = 0, low = 0;
      data.forEach(s => {
        if (s.gpa < 2.0 || s.attendance < 75) critical++;
        else if (s.gpa < 2.5 || s.attendance < 85) high++;
        else if (s.gpa < 3.0 || s.attendance < 90) moderate++;
        else low++;
      });

      setStats({
        totalStudents: total,
        avgGPA: parseFloat(avgGPA.toFixed(2)),
        avgAttendance: parseFloat(avgAttendance.toFixed(1)),
        criticalRisk: critical,
        highRisk: high,
        moderateRisk: moderate,
        lowRisk: low
      });

      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load teacher data');
    } finally {
      setLoading(false);
    }
  }

  function getRiskLevel(student: Student): 'CRITICAL' | 'HIGH' | 'MODERATE' | 'LOW' {
    if (student.gpa < 2.0 || student.attendance < 75) return 'CRITICAL';
    if (student.gpa < 2.5 || student.attendance < 85) return 'HIGH';
    if (student.gpa < 3.0 || student.attendance < 90) return 'MODERATE';
    return 'LOW';
  }

  function getPerformanceCategory(gpa: number): string {
    if (gpa >= 3.5) return 'Excellent';
    if (gpa >= 3.0) return 'Good';
    if (gpa >= 2.5) return 'Average';
    return 'Below Average';
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Users className="w-8 h-8 text-aura-primary" />
          <h1 className="text-3xl font-bold bg-gradient-to-r from-aura-primary to-aura-secondary bg-clip-text text-transparent">
            Teacher Dashboard
          </h1>
        </div>
        <p className="text-gray-600 dark:text-gray-400">
          Monitor your students and class performance
        </p>
      </div>

      {error && (
        <div className="glass bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4 mb-6 rounded-lg">
          <p className="text-red-700 dark:text-red-300">{error}</p>
        </div>
      )}

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="glass rounded-xl p-6">
          <div className="flex items-center justify-between mb-2">
            <Users className="w-8 h-8 text-blue-500" />
            <span className="text-3xl font-bold text-gray-900 dark:text-white">
              {stats.totalStudents}
            </span>
          </div>
          <p className="text-gray-600 dark:text-gray-400 text-sm">Total Students</p>
        </div>

        <div className="glass rounded-xl p-6">
          <div className="flex items-center justify-between mb-2">
            <Award className="w-8 h-8 text-green-500" />
            <span className="text-3xl font-bold text-gray-900 dark:text-white">
              {stats.avgGPA}
            </span>
          </div>
          <p className="text-gray-600 dark:text-gray-400 text-sm">Average GPA</p>
        </div>

        <div className="glass rounded-xl p-6">
          <div className="flex items-center justify-between mb-2">
            <CheckCircle className="w-8 h-8 text-purple-500" />
            <span className="text-3xl font-bold text-gray-900 dark:text-white">
              {stats.avgAttendance}%
            </span>
          </div>
          <p className="text-gray-600 dark:text-gray-400 text-sm">Average Attendance</p>
        </div>

        <div className="glass rounded-xl p-6">
          <div className="flex items-center justify-between mb-2">
            <AlertCircle className="w-8 h-8 text-red-500" />
            <span className="text-3xl font-bold text-gray-900 dark:text-white">
              {stats.criticalRisk + stats.highRisk}
            </span>
          </div>
          <p className="text-gray-600 dark:text-gray-400 text-sm">At-Risk Students</p>
        </div>
      </div>

      {/* Risk Distribution */}
      <div className="glass rounded-xl p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
          Risk Distribution
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-red-600 mb-1">{stats.criticalRisk}</div>
            <RiskBadge level="CRITICAL" />
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600 mb-1">{stats.highRisk}</div>
            <RiskBadge level="HIGH" />
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-yellow-600 mb-1">{stats.moderateRisk}</div>
            <RiskBadge level="MODERATE" />
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600 mb-1">{stats.lowRisk}</div>
            <RiskBadge level="LOW" />
          </div>
        </div>
      </div>

      {/* Students Table */}
      <div className="glass rounded-xl p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
          <BookOpen className="w-6 h-6" />
          My Students ({students.length})
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700">
                <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300 font-semibold">Student ID</th>
                <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300 font-semibold">Name</th>
                <th className="text-center py-3 px-4 text-gray-700 dark:text-gray-300 font-semibold">Grade</th>
                <th className="text-center py-3 px-4 text-gray-700 dark:text-gray-300 font-semibold">GPA</th>
                <th className="text-center py-3 px-4 text-gray-700 dark:text-gray-300 font-semibold">Attendance</th>
                <th className="text-center py-3 px-4 text-gray-700 dark:text-gray-300 font-semibold">Performance</th>
                <th className="text-center py-3 px-4 text-gray-700 dark:text-gray-300 font-semibold">Risk Level</th>
              </tr>
            </thead>
            <tbody>
              {students.map((student) => (
                <tr
                  key={student.student_id}
                  className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                >
                  <td className="py-3 px-4 font-mono text-sm text-gray-900 dark:text-white">
                    {student.student_id}
                  </td>
                  <td className="py-3 px-4 text-gray-900 dark:text-white font-medium">
                    {student.full_name}
                  </td>
                  <td className="py-3 px-4 text-center text-gray-700 dark:text-gray-300">
                    {student.grade}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className={`font-semibold ${student.gpa >= 3.5 ? 'text-green-600' :
                        student.gpa >= 3.0 ? 'text-blue-600' :
                          student.gpa >= 2.5 ? 'text-yellow-600' :
                            'text-red-600'
                      }`}>
                      {student.gpa.toFixed(2)}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className={`font-semibold ${student.attendance >= 90 ? 'text-green-600' :
                        student.attendance >= 85 ? 'text-yellow-600' :
                          'text-red-600'
                      }`}>
                      {student.attendance.toFixed(0)}%
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center text-gray-700 dark:text-gray-300">
                    {getPerformanceCategory(student.gpa)}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <RiskBadge level={getRiskLevel(student)} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
