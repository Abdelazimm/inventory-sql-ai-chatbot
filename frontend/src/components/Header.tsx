import React from 'react';
import { Database, Upload, Shield, LogIn, LogOut, Code2, Menu } from 'lucide-react';
import { UserProfile } from '../types';

interface HeaderProps {
  user: UserProfile | null;
  onOpenLogin: () => void;
  onLogout: () => void;
  onOpenUpload: () => void;
  onOpenMutation: () => void;
  debugMode: boolean;
  setDebugMode: (val: boolean) => void;
  onToggleSidebar?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  user,
  onOpenLogin,
  onLogout,
  onOpenUpload,
  onOpenMutation,
  debugMode,
  setDebugMode,
  onToggleSidebar
}) => {
  return (
    <header className="header-container" style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '12px 24px',
      borderBottom: '1px solid var(--border-color)',
      background: 'rgba(11, 15, 25, 0.95)',
      backdropFilter: 'blur(10px)',
      zIndex: 50
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        {/* Mobile Hamburger Toggle */}
        <button
          className="btn-icon mobile-only"
          onClick={onToggleSidebar}
          aria-label="Open conversation history"
        >
          <Menu size={18} />
        </button>

        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '10px',
          background: 'var(--accent-gradient)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: 'var(--accent-glow)',
          flexShrink: 0
        }}>
          <Database size={20} color="#fff" />
        </div>
        <div>
          <h1 className="header-title-text" style={{ fontSize: '17px', fontWeight: 600, letterSpacing: '-0.02em', background: 'linear-gradient(90deg, #fff, #9ca3af)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', whiteSpace: 'nowrap' }}>
            Inventory SQL AI
          </h1>
          <span className="header-subtitle-text" style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            Natural Language Text-to-SQL Analytics
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        {/* Toggle Debug Mode */}
        <button
          className={`btn ${debugMode ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setDebugMode(!debugMode)}
          title="Toggle SQL Query Inspector"
          style={{ fontSize: '12px', padding: '6px 10px' }}
        >
          <Code2 size={15} />
          <span className="desktop-only">{debugMode ? 'Debug: ON' : 'Debug: OFF'}</span>
        </button>

        {/* Manager/Admin CSV Ingestion */}
        {user && (user.role === 'manager' || user.role === 'admin') && (
          <button className="btn btn-secondary" onClick={onOpenUpload} title="Import CSV Data" style={{ fontSize: '12px', padding: '6px 10px' }}>
            <Upload size={15} />
            <span className="desktop-only">CSV</span>
          </button>
        )}

        {/* Manager/Admin Safe Mutations */}
        {user && (user.role === 'manager' || user.role === 'admin') && (
          <button className="btn btn-secondary" onClick={onOpenMutation} title="Manage Records" style={{ fontSize: '12px', padding: '6px 10px' }}>
            <Shield size={15} />
            <span className="desktop-only">Manage</span>
          </button>
        )}

        {/* User Badge / Login Logout */}
        {user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className={`badge badge-${user.role}`}>
              {user.role}
            </span>
            <button className="btn btn-secondary" onClick={onLogout} title="Log Out" style={{ padding: '6px 8px' }}>
              <LogOut size={15} />
            </button>
          </div>
        ) : (
          <button className="btn btn-primary" onClick={onOpenLogin} style={{ fontSize: '12px', padding: '6px 12px' }}>
            <LogIn size={15} />
            <span>Sign In</span>
          </button>
        )}
      </div>
    </header>
  );
};
