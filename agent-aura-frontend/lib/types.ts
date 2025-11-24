// TypeScript types for Agent Aura

export interface User {
  id: number;
  user_id?: number;
  username: string;
  email: string;
  role: 'admin' | 'teacher' | 'student';
  full_name?: string;
  student_id?: string;
  teacher_id?: string;
  department?: string;
  subject?: string;
  grade?: number;
  grade_level?: number;
  gpa?: number;
  profile?: AdminProfile | TeacherProfile | StudentProfile;
}

export interface AdminProfile {
  full_name: string;
  department?: string;
}

export interface TeacherProfile {
  teacher_id: string;
  full_name: string;
  subject?: string;
  grade_level?: number;
}

export interface StudentProfile {
  student_id: string;
  full_name: string;
  grade: number;
  gpa: number;
  attendance: number;
}

export interface Student {
  student_id: string;
  full_name: string;
  grade: number;
  gpa: number;
  attendance: number;
  performance_score?: number;
  parent_email?: string;
  parent_phone?: string;
  latest_risk?: {
    risk_level: 'CRITICAL' | 'HIGH' | 'MODERATE' | 'LOW';
    risk_score: number;
    assessed_at: string;
  };
}

export interface AgentSession {
  session_id: string;
  goal: string;
  status: 'active' | 'completed' | 'error';
  created_at: string;
  completed_at?: string;
}

export interface StreamEvent {
  type: 'thought' | 'action' | 'observation' | 'response' | 'error' | 'session_start' | 'agent_start' | 'agent_complete' | 'orchestrator_thought' | 'final_report';
  content?: string;
  tool?: string;
  tool_name?: string;
  tool_input?: Record<string, any>;
  arguments?: Record<string, any>;
  result?: any;
  response?: string;
  success?: boolean;
  timestamp: string;
  session_id?: string;
  goal?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: string;
  user_id: number;
}

export interface AgentRequest {
  goal: string;
  session_id?: string;
  student_id?: string;
  enabled_agents?: string[];
  model_override?: string;
}

export interface RiskBadgeProps {
  level: 'CRITICAL' | 'HIGH' | 'MODERATE' | 'LOW';
  score?: number;
  size?: 'sm' | 'md' | 'lg';
}
