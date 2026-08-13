import axios from 'axios';
import { UserProfile, ChatSession, IngestPreview, MutationPreview } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://127.0.0.1:8000');

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Attach JWT token from localStorage if available
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const api = {
  // Auth
  login: async (username: string, password: string) => {
    const res = await client.post('/auth/login', { username, password });
    return res.data;
  },
  getMe: async (): Promise<UserProfile> => {
    const res = await client.get('/auth/me');
    return res.data;
  },

  // Sessions
  getSessions: async (): Promise<ChatSession[]> => {
    const res = await client.get('/sessions');
    return res.data;
  },
  createSession: async (title?: string): Promise<ChatSession> => {
    const res = await client.post('/sessions', { title: title || 'New Conversation' });
    return res.data;
  },
  deleteSession: async (sessionId: string) => {
    const res = await client.delete(`/sessions/${sessionId}`);
    return res.data;
  },

  // Chat
  sendMessage: async (message: string, sessionId?: string) => {
    const res = await client.post('/chat', { message, session_id: sessionId });
    return res.data;
  },

  // CSV Ingestion
  previewCSV: async (entityType: string, file: File): Promise<IngestPreview> => {
    const formData = new FormData();
    formData.append('entity_type', entityType);
    formData.append('file', file);
    const res = await client.post('/ingest/preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },
  commitCSV: async (entityType: string, file: File) => {
    const formData = new FormData();
    formData.append('entity_type', entityType);
    formData.append('file', file);
    const res = await client.post('/ingest/commit', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  // Mutations
  previewMutation: async (action: string, entityType: string, entityId: any, fields: Record<string, any>): Promise<MutationPreview> => {
    const res = await client.post('/mutations/preview', { action, entity_type: entityType, entity_id: entityId, fields });
    return res.data;
  },
  confirmMutation: async (actionId: string) => {
    const res = await client.post(`/mutations/${actionId}/confirm`);
    return res.data;
  },
  cancelMutation: async (actionId: string) => {
    const res = await client.post(`/mutations/${actionId}/cancel`);
    return res.data;
  }
};
