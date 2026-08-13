import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { SessionSidebar } from './components/SessionSidebar';
import { ChatWindow } from './components/ChatWindow';
import { LoginModal } from './components/LoginModal';
import { CSVUploadModal } from './components/CSVUploadModal';
import { MutationModal } from './components/MutationModal';
import { api } from './services/api';
import { Message, ChatSession, UserProfile } from './types';

export const App: React.FC = () => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [debugMode, setDebugMode] = useState(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Modals
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isMutationOpen, setIsMutationOpen] = useState(false);

  // Load user profile on startup if token exists
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      api.getMe()
        .then((u) => setUser(u))
        .catch(() => localStorage.removeItem('access_token'));
    }
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const data = await api.getSessions();
      setSessions(data);
      if (data.length > 0 && !activeSessionId) {
        setActiveSessionId(data[0].session_id);
      }
    } catch (err) {
      console.error('Failed to load sessions:', err);
    }
  };

  const handleCreateSession = async () => {
    try {
      const newSession = await api.createSession();
      setSessions([newSession, ...sessions]);
      setActiveSessionId(newSession.session_id);
      setMessages([]);
      setIsSidebarOpen(false);
    } catch (err) {
      console.error('Failed to create session:', err);
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      await api.deleteSession(sessionId);
      const remaining = sessions.filter((s) => s.session_id !== sessionId);
      setSessions(remaining);
      if (activeSessionId === sessionId) {
        setActiveSessionId(remaining.length > 0 ? remaining[0].session_id : null);
        setMessages([]);
      }
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  const handleSendMessage = async (text: string) => {
    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text,
      timestamp: new Date().toISOString()
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await api.sendMessage(text, activeSessionId || undefined);
      
      // Update session if new one created
      if (!activeSessionId && res.session_id) {
        setActiveSessionId(res.session_id);
        loadSessions();
      }

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: res.answer,
        timestamp: new Date().toISOString(),
        metadata: res.metadata
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: err.response?.data?.detail || 'Failed to connect to the SQL Assistant backend.',
        timestamp: new Date().toISOString()
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%', background: 'var(--bg-primary)', position: 'fixed', inset: 0, overflow: 'hidden' }}>
      <Header
        user={user}
        onOpenLogin={() => setIsLoginOpen(true)}
        onLogout={handleLogout}
        onOpenUpload={() => setIsUploadOpen(true)}
        onOpenMutation={() => setIsMutationOpen(true)}
        debugMode={debugMode}
        setDebugMode={setDebugMode}
        onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
      />

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden', position: 'relative' }}>
        <SessionSidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelectSession={(id) => {
            setActiveSessionId(id);
            setMessages([]);
            setIsSidebarOpen(false);
          }}
          onCreateSession={handleCreateSession}
          onDeleteSession={handleDeleteSession}
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />

        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', minWidth: 0, overflow: 'hidden' }}>
          <ChatWindow
            messages={messages}
            isLoading={isLoading}
            onSendMessage={handleSendMessage}
            debugMode={debugMode}
          />
        </main>
      </div>

      <LoginModal
        isOpen={isLoginOpen}
        onClose={() => setIsLoginOpen(false)}
        onLoginSuccess={(u) => setUser(u)}
      />

      <CSVUploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
      />

      <MutationModal
        isOpen={isMutationOpen}
        onClose={() => setIsMutationOpen(false)}
        userRole={user?.role}
      />
    </div>
  );
};
