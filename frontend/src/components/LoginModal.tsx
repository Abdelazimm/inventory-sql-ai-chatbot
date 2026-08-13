import React, { useState } from 'react';
import { X, Key, User } from 'lucide-react';
import { api } from '../services/api';
import { UserProfile } from '../types';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess: (user: UserProfile) => void;
}

export const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onClose, onLoginSuccess }) => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const data = await api.login(username, password);
      localStorage.setItem('access_token', data.access_token);
      const user = await api.getMe();
      onLoginSuccess(user);
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.7)',
      backdropFilter: 'blur(6px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div className="glass-panel" style={{ width: '400px', padding: '24px', position: 'relative' }}>
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '16px',
            right: '16px',
            background: 'transparent',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer'
          }}
        >
          <X size={18} />
        </button>

        <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '6px' }}>
          Sign In to Inventory Portal
        </h3>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '20px' }}>
          Select credentials: admin / manager / viewer (password: role + 123)
        </p>

        {error && (
          <div style={{ padding: '8px 12px', background: 'rgba(239, 68, 68, 0.2)', border: '1px solid rgba(239, 68, 68, 0.4)', borderRadius: '6px', color: '#fca5a5', fontSize: '12px', marginBottom: '16px' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <label style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>
              Username
            </label>
            <div style={{ display: 'flex', alignItems: 'center', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '6px', padding: '8px 12px', gap: '8px' }}>
              <User size={16} color="var(--text-muted)" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                style={{ background: 'transparent', border: 'none', color: '#fff', fontSize: '14px', outline: 'none', width: '100%' }}
                placeholder="admin / manager / viewer"
                required
              />
            </div>
          </div>

          <div>
            <label style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>
              Password
            </label>
            <div style={{ display: 'flex', alignItems: 'center', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '6px', padding: '8px 12px', gap: '8px' }}>
              <Key size={16} color="var(--text-muted)" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{ background: 'transparent', border: 'none', color: '#fff', fontSize: '14px', outline: 'none', width: '100%' }}
                placeholder="Password"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ marginTop: '8px', width: '100%' }}
          >
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
};
