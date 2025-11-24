// API Client for Agent Aura Backend

import axios, { AxiosInstance } from 'axios';
import { LoginRequest, LoginResponse, User, Student, AgentRequest, AgentSession, StreamEvent } from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    // Load token from localStorage on client
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token');
    }
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  // Authentication
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const params = new URLSearchParams();
    params.append('username', credentials.username);
    params.append('password', credentials.password);

    const response = await this.client.post<LoginResponse>('/api/v1/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });

    this.setToken(response.data.access_token);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/api/v1/auth/me');
    return response.data;
  }

  async logout() {
    this.clearToken();
  }

  // Students
  async getStudents(): Promise<Student[]> {
    const response = await this.client.get<any>('/api/v1/students');
    // Handle both {students: []} and direct array response
    return response.data.students || response.data;
  }

  async getAllStudents(): Promise<Student[]> {
    // Alias for getStudents for consistency
    return this.getStudents();
  }

  async getStudent(studentId: string): Promise<Student> {
    const response = await this.client.get<Student>(`/api/v1/students/${studentId}`);
    return response.data;
  }

  async getStudentDetail(studentId: string): Promise<Student> {
    const response = await this.client.get<Student>(`/api/v1/students/${studentId}`);
    return response.data;
  }

  // Agent Interaction (Streaming)
  async *invokeAgent(request: AgentRequest): AsyncGenerator<StreamEvent> {
    const response = await fetch(`${API_URL}/api/v1/agent/invoke`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.token}`,
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error('No reader available');

    const decoder = new TextDecoder();

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const event: StreamEvent = JSON.parse(line);
            yield event;
          } catch (e) {
            console.error('Failed to parse event:', line, e);
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  // Sessions
  async getSessions(): Promise<AgentSession[]> {
    const response = await this.client.get<AgentSession[]>('/api/v1/sessions');
    return response.data;
  }

  async getSessionEvents(sessionId: string): Promise<StreamEvent[]> {
    const response = await this.client.get<StreamEvent[]>(`/api/v1/sessions/${sessionId}/events`);
    return response.data;
  }

  async deleteSession(sessionId: string): Promise<void> {
    await this.client.delete(`/api/v1/sessions/${sessionId}`);
  }

  async clearAllSessions(): Promise<{ message: string; deleted_count: number }> {
    const response = await this.client.delete('/api/v1/sessions/clear-all');
    return response.data;
  }

  exportSessionPDF(sessionId: string): void {
    const url = `${API_URL}/api/v1/sessions/${sessionId}/export/pdf`;
    window.open(url + `?token=${this.token}`, '_blank');
  }

  exportSessionCSV(sessionId: string): void {
    const url = `${API_URL}/api/v1/sessions/${sessionId}/export/csv`;
    window.open(url + `?token=${this.token}`, '_blank');
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Models
  async getAvailableModels(): Promise<{ id: string; provider: string; name: string }[]> {
    const response = await this.client.get<{ models: { id: string; provider: string; name: string }[] }>('/api/v1/agent/models');
    return response.data.models;
  }

  // Settings
  async updateApiKey(apiKey: string): Promise<void> {
    await this.client.post('/api/v1/settings/apikey', { api_key: apiKey });
  }

  async removeApiKey(): Promise<void> {
    await this.client.delete('/api/v1/settings/apikey');
  }

  async getApiKeyStatus(): Promise<{ is_set: boolean }> {
    const response = await this.client.get<{ is_set: boolean }>('/api/v1/settings/apikey/status');
    return response.data;
  }

  async getAgentConfig(): Promise<{ agents: any[] }> {
    const response = await this.client.get<{ agents: any[] }>('/api/v1/agent/config');
    return response.data;
  }

  async updateAgentConfig(agentId: string, enabled: boolean): Promise<void> {
    await this.client.post('/api/v1/agent/config', { agent_id: agentId, enabled });
  }
}

export const apiClient = new ApiClient();
