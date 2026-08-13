import React from 'react';
import { Database, Upload, Shield, LogIn, LogOut, Code2 } from 'lucide-react';
import { UserProfile } from '../types';

interface HeaderProps {
  user: UserProfile | null;
  onOpenLogin: () => void;
  onLogout: () => void;
  onOpenUpload: () => void;
  onOpenMutation: () => void;
  debugMode: boolean;
  setDebugMode: (val: boolean) => void;
}

export const Header: React.FC<HeaderProps> = ({
  user,
  onOpenLogin,
  onLogout,
  onOpenUpload,
  onOpenMutation,
  debugMode,
  setDebugMode
}) => {
  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '12px 24px',
      borderBottom: '1px solid var(--border-color)',
      background: 'rgba(11, 15, 25, 0.8)',
      backdropFilter: 'blur(10px)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '10px',
          background: 'var(--accent-gradient)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: 'var(--accent-glow)'
        }}>
          <Database size={20} color="#fff" />
        </div>
        <div>
          <h1 style={{ fontSize: '18px', fontWeight: 600, letterSpacing: '-0.02em', background: 'linear-gradient(90deg, #fff, #9ca3af)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Inventory SQL AI Assistant
          </h1>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            Natural Language Text-to-SQL Analytics
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Toggle Debug Mode */}
        <button
          className={`btn ${debugMode ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setDebugMode(!debugMode)}
          title="Toggle SQL Query Inspector"
          style={{ fontSize: '13px', padding: '6px 12px' }}
        >
          <Code2 size={16} />
          {debugMode ? 'Debug: ON' : 'Debug: OFF'}
        </button>

        {/* Manager/Admin CSV Ingestion */}
        {user && (user.role === 'manager' || user.role === 'admin') && (
          <button className="btn btn-secondary" onClick={onOpenUpload} style={{ fontSize: '13px', padding: '6px 12px' }}>
            <Upload size={16} />
            Import CSV
          </button>
        )}

        {/* Manager/Admin Safe Mutations */}
        {user && (user.role === 'manager' || user.role === 'admin') && (
          <button className="btn btn-secondary" onClick={onOpenMutation} style={{ fontSize: '13px', padding: '6px 12px' }}>
            <Shield size={16} />
            Manage Records
          </button>
        )}

        {/* User Badge / Login Logout */}
        {user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className={`badge badge-${user.role}`}>
              {user.role}
            </span>
            <span style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
              {user.username}
            </span>
            <button className="btn btn-secondary" onClick={onLogout} style={{ padding: '6px 10px' }}>
              <LogOut size={16} />
            </button>
          </div>
        ) : (
          <button className="btn btn-primary" onClick={onOpenLogin} style={{ fontSize: '13px', padding: '6px 14px' }}>
            <LogIn size={16} />
            Sign In
          </button>
        )}
      </div>
    </header>
  );
};
