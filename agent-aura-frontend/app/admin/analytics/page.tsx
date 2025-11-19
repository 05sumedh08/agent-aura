'use client';

import { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Users, Activity, Target, Zap, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { apiClient } from '@/lib/api';
import LoadingSpinner from '@/components/LoadingSpinner';

interface Student {
  student_id: string;
  name: string;
  grade_level: number;
  gpa: number;
  attendance_rate: number;
  overall_performance: string;
}

interface AnalyticsData {
  totalStudents: number;
  avgGPA: number;
  avgAttendance: number;
  riskDistribution: {
    critical: number;
    high: number;
    moderate: number;
    low: number;
  };
  gradeDistribution: {
    [key: number]: number;
  };
  performanceDistribution: {
    [key: string]: number;
  };
  gpaRanges: {
    excellent: number;  // 3.5-4.0
    good: number;       // 3.0-3.5
    average: number;    // 2.5-3.0
    below: number;      // <2.5
  };
}

export default function AnalyticsPage() {
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsData>({
    totalStudents: 0,
    avgGPA: 0,
    avgAttendance: 0,
    riskDistribution: { critical: 0, high: 0, moderate: 0, low: 0 },
    gradeDistribution: {},
    performanceDistribution: {},
    gpaRanges: { excellent: 0, good: 0, average: 0, below: 0 }
  });

  useEffect(() => {
    loadAnalytics();
  }, []);

  async function loadAnalytics() {
    try {
      setLoading(true);
      const data = await apiClient.getAllStudents();
      setStudents(data);
      
      // Calculate comprehensive analytics
      const total = data.length;
      const avgGPA = data.reduce((sum, s) => sum + s.gpa, 0) / total;
      const avgAttendance = data.reduce((sum, s) => sum + s.attendance_rate, 0) / total;
      
      // Risk distribution
      let critical = 0, high = 0, moderate = 0, low = 0;
      data.forEach(s => {
        if (s.gpa < 2.0 || s.attendance_rate < 0.75) critical++;
        else if (s.gpa < 2.5 || s.attendance_rate < 0.85) high++;
        else if (s.gpa < 3.0 || s.attendance_rate < 0.90) moderate++;
        else low++;
      });
      
      // Grade distribution
      const gradeDist: { [key: number]: number } = {};
      data.forEach(s => {
        gradeDist[s.grade_level] = (gradeDist[s.grade_level] || 0) + 1;
      });
      
      // Performance distribution
      const perfDist: { [key: string]: number } = {};
      data.forEach(s => {
        perfDist[s.overall_performance] = (perfDist[s.overall_performance] || 0) + 1;
      });
      
      // GPA ranges
      let excellent = 0, good = 0, average = 0, below = 0;
      data.forEach(s => {
        if (s.gpa >= 3.5) excellent++;
        else if (s.gpa >= 3.0) good++;
        else if (s.gpa >= 2.5) average++;
        else below++;
      });
      
      setAnalytics({
        totalStudents: total,
        avgGPA: parseFloat(avgGPA.toFixed(2)),
        avgAttendance: parseFloat((avgAttendance * 100).toFixed(1)),
        riskDistribution: { critical, high, moderate, low },
        gradeDistribution: gradeDist,
        performanceDistribution: perfDist,
        gpaRanges: { excellent, good, average, below }
      });
      
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner />
      </div>
    );
  }

  const riskTotal = analytics.riskDistribution.critical + analytics.riskDistribution.high + 
                    analytics.riskDistribution.moderate + analytics.riskDistribution.low;

  return (
    <div className="p-8">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <BarChart3 className="w-8 h-8 text-aura-primary" />
          <h1 className="text-3xl font-bold bg-gradient-to-r from-aura-primary to-aura-secondary bg-clip-text text-transparent">
            System Analytics
          </h1>
        </div>
        <p className="text-gray-600 dark:text-gray-400">
          Comprehensive insights and performance metrics
        </p>
      </div>

      {error && (
        <div className="glass bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4 mb-6 rounded-lg">
          <p className="text-red-700 dark:text-red-300">{error}</p>
        </div>
      )}

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="glass rounded-xl p-6">
          <div className="flex items-center justify-between mb-2">
            <Users className="w-8 h-8 text-blue-500" />
            <span className="text-3xl font-bold text-gray-900 dark:text-white">
              {analytics.totalStudents}
            </span>
          </div>
          <p className="text-gray-600 dark:text-gray-400 text-sm">Total Students</p>
          <div className="mt-2 flex items-center gap-1 text-xs text-green-600">
            <TrendingUp className="w-4 h-4" />
            <span>Active monitoring</span>
          </div>
        </div>

        <div className="glass rounded-xl p-6">
          <div className="flex items-center justify-between mb-2">
            <Target className="w-8 h-8 text-green-500" />
            <span className="text-3xl font-bold text-gray-900 dark:text-white">
              {analytics.avgGPA}
            </span>
          </div>
          <p className="text-gray-600 dark:text-gray-400 text-sm">Average GPA</p>
          <div className="mt-2 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-green-500 to-emerald-500"
              style={{ width: `${(analytics.avgGPA / 4.0) * 100}%` }}
            />
          </div>
        </div>

        <div className="glass rounded-xl p-6">
          <div className="flex items-center justify-between mb-2">
            <CheckCircle2 className="w-8 h-8 text-purple-500" />
            <span className="text-3xl font-bold text-gray-900 dark:text-white">
              {analytics.avgAttendance}%
            </span>
          </div>
          <p className="text-gray-600 dark:text-gray-400 text-sm">Average Attendance</p>
          <div className="mt-2 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
              style={{ width: `${analytics.avgAttendance}%` }}
            />
          </div>
        </div>

        <div className="glass rounded-xl p-6">
          <div className="flex items-center justify-between mb-2">
            <Zap className="w-8 h-8 text-yellow-500" />
            <span className="text-3xl font-bold text-gray-900 dark:text-white">
              {analytics.riskDistribution.critical + analytics.riskDistribution.high}
            </span>
          </div>
          <p className="text-gray-600 dark:text-gray-400 text-sm">High Priority Cases</p>
          <div className="mt-2 flex items-center gap-1 text-xs text-orange-600">
            <AlertTriangle className="w-4 h-4" />
            <span>Needs attention</span>
          </div>
        </div>
      </div>

      {/* Risk Distribution Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="glass rounded-xl p-6">
          <h2 className="text-xl font-semibold mb-6 text-gray-900 dark:text-white flex items-center gap-2">
            <AlertTriangle className="w-6 h-6 text-orange-500" />
            Risk Distribution
          </h2>
          
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Critical</span>
                </div>
                <span className="text-sm font-bold text-gray-900 dark:text-white">
                  {analytics.riskDistribution.critical} ({((analytics.riskDistribution.critical / riskTotal) * 100).toFixed(0)}%)
                </span>
              </div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-red-500 to-red-600 transition-all duration-500"
                  style={{ width: `${(analytics.riskDistribution.critical / riskTotal) * 100}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-orange-500" />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">High</span>
                </div>
                <span className="text-sm font-bold text-gray-900 dark:text-white">
                  {analytics.riskDistribution.high} ({((analytics.riskDistribution.high / riskTotal) * 100).toFixed(0)}%)
                </span>
              </div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-orange-500 to-orange-600 transition-all duration-500"
                  style={{ width: `${(analytics.riskDistribution.high / riskTotal) * 100}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-yellow-500" />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Moderate</span>
                </div>
                <span className="text-sm font-bold text-gray-900 dark:text-white">
                  {analytics.riskDistribution.moderate} ({((analytics.riskDistribution.moderate / riskTotal) * 100).toFixed(0)}%)
                </span>
              </div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-yellow-500 to-yellow-600 transition-all duration-500"
                  style={{ width: `${(analytics.riskDistribution.moderate / riskTotal) * 100}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Low</span>
                </div>
                <span className="text-sm font-bold text-gray-900 dark:text-white">
                  {analytics.riskDistribution.low} ({((analytics.riskDistribution.low / riskTotal) * 100).toFixed(0)}%)
                </span>
              </div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-green-500 to-green-600 transition-all duration-500"
                  style={{ width: `${(analytics.riskDistribution.low / riskTotal) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* GPA Distribution */}
        <div className="glass rounded-xl p-6">
          <h2 className="text-xl font-semibold mb-6 text-gray-900 dark:text-white flex items-center gap-2">
            <Target className="w-6 h-6 text-green-500" />
            GPA Distribution
          </h2>
          
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-emerald-500" />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Excellent (3.5-4.0)</span>
                </div>
                <span className="text-sm font-bold text-gray-900 dark:text-white">
                  {analytics.gpaRanges.excellent}
                </span>
              </div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-emerald-500 to-emerald-600 transition-all duration-500"
                  style={{ width: `${(analytics.gpaRanges.excellent / analytics.totalStudents) * 100}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-blue-500" />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Good (3.0-3.5)</span>
                </div>
                <span className="text-sm font-bold text-gray-900 dark:text-white">
                  {analytics.gpaRanges.good}
                </span>
              </div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-500"
                  style={{ width: `${(analytics.gpaRanges.good / analytics.totalStudents) * 100}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-yellow-500" />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Average (2.5-3.0)</span>
                </div>
                <span className="text-sm font-bold text-gray-900 dark:text-white">
                  {analytics.gpaRanges.average}
                </span>
              </div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-yellow-500 to-yellow-600 transition-all duration-500"
                  style={{ width: `${(analytics.gpaRanges.average / analytics.totalStudents) * 100}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Below Average (&lt;2.5)</span>
                </div>
                <span className="text-sm font-bold text-gray-900 dark:text-white">
                  {analytics.gpaRanges.below}
                </span>
              </div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-red-500 to-red-600 transition-all duration-500"
                  style={{ width: `${(analytics.gpaRanges.below / analytics.totalStudents) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Grade Level & Performance Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass rounded-xl p-6">
          <h2 className="text-xl font-semibold mb-6 text-gray-900 dark:text-white flex items-center gap-2">
            <Activity className="w-6 h-6 text-blue-500" />
            Students by Grade Level
          </h2>
          
          <div className="space-y-3">
            {Object.entries(analytics.gradeDistribution).map(([grade, count]) => (
              <div key={grade} className="flex items-center gap-3">
                <div className="w-16 text-sm font-semibold text-gray-700 dark:text-gray-300">
                  Grade {grade}
                </div>
                <div className="flex-1 h-8 bg-gray-200 dark:bg-gray-700 rounded-lg overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 flex items-center justify-end px-3 transition-all duration-500"
                    style={{ width: `${(count / analytics.totalStudents) * 100}%` }}
                  >
                    <span className="text-xs font-bold text-white">{count}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass rounded-xl p-6">
          <h2 className="text-xl font-semibold mb-6 text-gray-900 dark:text-white flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-purple-500" />
            Performance Categories
          </h2>
          
          <div className="space-y-3">
            {Object.entries(analytics.performanceDistribution).map(([performance, count]) => (
              <div key={performance} className="flex items-center gap-3">
                <div className="w-32 text-sm font-semibold text-gray-700 dark:text-gray-300">
                  {performance}
                </div>
                <div className="flex-1 h-8 bg-gray-200 dark:bg-gray-700 rounded-lg overflow-hidden">
                  <div 
                    className={`h-full flex items-center justify-end px-3 transition-all duration-500 ${
                      performance === 'Excellent' ? 'bg-gradient-to-r from-emerald-500 to-green-500' :
                      performance === 'Above Average' ? 'bg-gradient-to-r from-blue-500 to-indigo-500' :
                      performance === 'Average' ? 'bg-gradient-to-r from-yellow-500 to-amber-500' :
                      'bg-gradient-to-r from-orange-500 to-red-500'
                    }`}
                    style={{ width: `${(count / analytics.totalStudents) * 100}%` }}
                  >
                    <span className="text-xs font-bold text-white">{count}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* System Insights */}
      <div className="glass rounded-xl p-6 mt-8">
        <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
          <Zap className="w-6 h-6 text-yellow-500" />
          Key Insights
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle2 className="w-5 h-5 text-blue-600" />
              <span className="font-semibold text-blue-900 dark:text-blue-300">High Performers</span>
            </div>
            <p className="text-sm text-blue-800 dark:text-blue-400">
              {analytics.gpaRanges.excellent} students ({((analytics.gpaRanges.excellent / analytics.totalStudents) * 100).toFixed(0)}%) maintaining excellent GPAs
            </p>
          </div>

          <div className="p-4 bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="w-5 h-5 text-orange-600" />
              <span className="font-semibold text-orange-900 dark:text-orange-300">Intervention Needed</span>
            </div>
            <p className="text-sm text-orange-800 dark:text-orange-400">
              {analytics.riskDistribution.critical + analytics.riskDistribution.high} students require immediate support
            </p>
          </div>

          <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-5 h-5 text-purple-600" />
              <span className="font-semibold text-purple-900 dark:text-purple-300">Multi-Agent Active</span>
            </div>
            <p className="text-sm text-purple-800 dark:text-purple-400">
              4 specialized agents monitoring {analytics.totalStudents} students in parallel
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
