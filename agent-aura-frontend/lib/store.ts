// Global State Management with Zustand

import { create } from 'zustand';
import { User, Student, AgentSession, StreamEvent } from './types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  logout: () => void;
}

interface StudentState {
  students: Student[];
  selectedStudent: Student | null;
  setStudents: (students: Student[]) => void;
  setSelectedStudent: (student: Student | null) => void;
}

interface SessionState {
  currentSession: AgentSession | null;
  sessions: AgentSession[];
  streamEvents: StreamEvent[];
  isStreaming: boolean;
  setCurrentSession: (session: AgentSession | null) => void;
  setSessions: (sessions: AgentSession[]) => void;
  addStreamEvent: (event: StreamEvent) => void;
  clearStreamEvents: () => void;
  setIsStreaming: (isStreaming: boolean) => void;
}

interface SettingsState {
  selectedModel: string | null;
  setSelectedModel: (model: string | null) => void;
}

// Combined store
interface AppState extends AuthState, StudentState, SessionState, SettingsState { }

export const useStore = create<AppState>((set) => ({
  // Auth state
  user: null,
  isAuthenticated: false,
  setUser: (user) => set({ user, isAuthenticated: !!user }),
  logout: () => set({ user: null, isAuthenticated: false }),

  // Student state
  students: [],
  selectedStudent: null,
  setStudents: (students) => set({ students }),
  setSelectedStudent: (selectedStudent) => set({ selectedStudent }),

  // Session state
  currentSession: null,
  sessions: [],
  streamEvents: [],
  isStreaming: false,
  setCurrentSession: (currentSession) => set({ currentSession }),
  setSessions: (sessions) => set({ sessions }),
  addStreamEvent: (event) =>
    set((state) => ({
      streamEvents: [...state.streamEvents, event],
    })),
  clearStreamEvents: () => set({ streamEvents: [] }),
  setIsStreaming: (isStreaming) => set({ isStreaming }),

  // Settings state
  selectedModel: null,
  setSelectedModel: (selectedModel) => set({ selectedModel }),
}));

// Selectors for convenience
export const useAuth = () =>
  useStore((state) => ({
    user: state.user,
    isAuthenticated: state.isAuthenticated,
    setUser: state.setUser,
    logout: state.logout,
  }));

export const useStudents = () =>
  useStore((state) => ({
    students: state.students,
    selectedStudent: state.selectedStudent,
    setStudents: state.setStudents,
    setSelectedStudent: state.setSelectedStudent,
  }));

export const useSession = () =>
  useStore((state) => ({
    currentSession: state.currentSession,
    sessions: state.sessions,
    streamEvents: state.streamEvents,
    isStreaming: state.isStreaming,
    setCurrentSession: state.setCurrentSession,
    setSessions: state.setSessions,
    addStreamEvent: state.addStreamEvent,
    clearStreamEvents: state.clearStreamEvents,
    setIsStreaming: state.setIsStreaming,
  }));

export const useSettings = () =>
  useStore((state) => ({
    selectedModel: state.selectedModel,
    setSelectedModel: state.setSelectedModel,
  }));
