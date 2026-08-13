import React from 'react';
import { MessageSquare, Plus, Trash2 } from 'lucide-react';
import { ChatSession } from '../types';

interface SessionSidebarProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onCreateSession: () => void;
  onDeleteSession: (id: string) => void;
}

export const SessionSidebar: React.FC<SessionSidebarProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onCreateSession,
  onDeleteSession
}) => {
  return (
    <aside style={{
      width: '260px',
      borderRight: '1px solid var(--border-color)',
      background: 'var(--bg-secondary)',
      display: 'flex',
      flexDirection: 'column',
      height: '100%'
    }}>
      <div style={{ padding: '16px', borderBottom: '1px solid var(--border-color)' }}>
        <button
          className="btn btn-primary"
          style={{ width: '100%', justifyContent: 'center' }}
          onClick={onCreateSession}
        >
          <Plus size={16} />
          New Conversation
        </button>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '12px 8px' }}>
        <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', padding: '0 8px 8px 8px' }}>
          Recent Sessions
        </div>

        {sessions.length === 0 ? (
          <div style={{ padding: '16px 8px', fontSize: '13px', color: 'var(--text-muted)', textAlign: 'center' }}>
            No sessions yet.
          </div>
        ) : (
          sessions.map((s) => {
            const isActive = s.session_id === activeSessionId;
            return (
              <div
                key={s.session_id}
                onClick={() => onSelectSession(s.session_id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px 12px',
                  borderRadius: 'var(--radius-md)',
                  marginBottom: '4px',
                  cursor: 'pointer',
                  background: isActive ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                  border: isActive ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid transparent',
                  color: isActive ? '#fff' : 'var(--text-secondary)',
                  transition: 'all 0.15s ease'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden' }}>
                  <MessageSquare size={14} color={isActive ? '#818cf8' : 'var(--text-muted)'} />
                  <span style={{ fontSize: '13px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '150px' }}>
                    {s.title}
                  </span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(s.session_id);
                  }}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--text-muted)',
                    cursor: 'pointer',
                    padding: '2px 4px',
                    borderRadius: '4px'
                  }}
                  title="Delete Session"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            );
          })
        )}
      </div>
    </aside>
  );
};
