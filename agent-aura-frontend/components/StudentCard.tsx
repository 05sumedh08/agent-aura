'use client';

import { Student } from '@/lib/types';
import RiskBadge from './RiskBadge';
import { User, TrendingDown, TrendingUp } from 'lucide-react';

interface StudentCardProps {
  student: Student;
  onClick?: () => void;
}

export default function StudentCard({ student, onClick }: StudentCardProps) {
  return (
    <button
      onClick={onClick}
      className="w-full glass rounded-2xl p-6 text-left transition-all hover:scale-[1.02] hover:shadow-lg border border-gray-200 dark:border-gray-700"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-gradient-to-r from-aura-primary to-aura-secondary flex items-center justify-center">
            <User className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-800 dark:text-white">
              {student.full_name}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {student.student_id}
            </p>
          </div>
        </div>
        {student.latest_risk && (
          <RiskBadge level={student.latest_risk.risk_level} score={student.latest_risk.risk_score} />
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center p-3 glass rounded-xl">
          <div className="text-lg font-bold text-gray-800 dark:text-white">
            {student.grade}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">Grade</div>
        </div>
        <div className="text-center p-3 glass rounded-xl">
          <div className="flex items-center justify-center gap-1">
            <span className="text-lg font-bold text-gray-800 dark:text-white">
              {student.gpa.toFixed(2)}
            </span>
            {student.gpa >= 3.5 ? (
              <TrendingUp className="w-4 h-4 text-green-500" />
            ) : student.gpa < 2.5 ? (
              <TrendingDown className="w-4 h-4 text-red-500" />
            ) : null}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">GPA</div>
        </div>
        <div className="text-center p-3 glass rounded-xl">
          <div className="text-lg font-bold text-gray-800 dark:text-white">
            {student.attendance}%
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">Attendance</div>
        </div>
      </div>

      {/* Performance Score */}
      {student.performance_score !== undefined && (
        <div className="glass rounded-xl p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-600 dark:text-gray-400">
              Performance
            </span>
            <span className="text-sm font-bold text-gray-800 dark:text-white">
              {student.performance_score.toFixed(1)}%
            </span>
          </div>
          <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-aura-primary to-aura-secondary transition-all"
              style={{ width: `${student.performance_score}%` }}
            />
          </div>
        </div>
      )}
    </button>
  );
}
