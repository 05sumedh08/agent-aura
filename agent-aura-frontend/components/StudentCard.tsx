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
      className="w-full glass-card rounded-2xl p-6 text-left transition-all duration-300 hover:scale-[1.03] hover:shadow-2xl hover:shadow-purple-500/30 border border-white/10 group relative overflow-hidden"
    >
      {/* Animated background gradient on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-500/0 to-pink-500/0 group-hover:from-purple-500/5 group-hover:to-pink-500/5 transition-all duration-500 rounded-2xl" />
      {/* Header */}
      <div className="flex items-start justify-between mb-5 relative z-10">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-gradient-to-r from-aura-primary to-aura-secondary flex items-center justify-center shadow-2xl shadow-purple-500/60 group-hover:shadow-purple-500/90 group-hover:scale-110 transition-all duration-300">
            <User className="w-8 h-8 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-white text-xl group-hover:text-purple-100 transition-colors tracking-tight">
              {student.full_name}
            </h3>
            <p className="text-sm text-gray-300 font-mono font-semibold mt-1">
              {student.student_id}
            </p>
          </div>
        </div>
        {student.latest_risk && (
          <RiskBadge level={student.latest_risk.risk_level} score={student.latest_risk.risk_score} />
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3 mb-5 relative z-10">
        <div className="text-center p-4 glass rounded-xl border border-white/10 bg-white/5 group-hover:border-white/15 group-hover:bg-white/8 transition-all duration-300">
          <div className="text-2xl font-extrabold text-white mb-1">
            {student.grade}
          </div>
          <div className="text-xs text-gray-200 uppercase tracking-wider font-bold">Grade</div>
        </div>
        <div className="text-center p-4 glass rounded-xl border border-white/10 bg-white/5 group-hover:border-white/15 group-hover:bg-white/8 transition-all duration-300">
          <div className="flex items-center justify-center gap-1 mb-1">
            <span className="text-2xl font-extrabold text-white">
              {student.gpa.toFixed(2)}
            </span>
            {student.gpa >= 3.5 ? (
              <TrendingUp className="w-4 h-4 text-green-400 animate-bounce" />
            ) : student.gpa < 2.5 ? (
              <TrendingDown className="w-4 h-4 text-red-400" />
            ) : null}
          </div>
          <div className="text-xs text-gray-200 uppercase tracking-wider font-bold">GPA</div>
        </div>
        <div className="text-center p-4 glass rounded-xl border border-white/10 bg-white/5 group-hover:border-white/15 group-hover:bg-white/8 transition-all duration-300">
          <div className="text-2xl font-extrabold text-white mb-1">
            {student.attendance}%
          </div>
          <div className="text-xs text-gray-200 uppercase tracking-wider font-bold">Attendance</div>
        </div>
      </div>

      {/* Performance Score */}
      {student.performance_score !== undefined && (
        <div className="glass rounded-xl p-5 border border-white/10 bg-white/5 group-hover:border-white/15 transition-all duration-300 relative z-10">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-bold text-gray-200 uppercase tracking-wider">
              Performance
            </span>
            <span className="text-lg font-extrabold text-white bg-purple-500/30 px-3 py-1.5 rounded-lg shadow-lg">
              {student.performance_score.toFixed(1)}%
            </span>
          </div>
          <div className="w-full h-3 bg-gray-700/50 rounded-full overflow-hidden relative">
            <div
              className="h-full bg-gradient-to-r from-aura-primary via-purple-500 to-aura-secondary transition-all duration-1000 shadow-lg shadow-purple-500/50 relative"
              style={{ width: `${student.performance_score}%` }}
            >
              <div className="absolute inset-0 bg-white/20 animate-shimmer" />
            </div>
          </div>
        </div>
      )}
    </button>
  );
}
