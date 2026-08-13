import React from 'react';
import { MessageSquare, Plus, Trash2, X } from 'lucide-react';
import { ChatSession } from '../types';

interface SessionSidebarProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onCreateSession: () => void;
  onDeleteSession: (id: string) => void;
  isOpen?: boolean;
  onClose?: () => void;
}

export const SessionSidebar: React.FC<SessionSidebarProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onCreateSession,
  onDeleteSession,
  isOpen = false,
  onClose
}) => {
  return (
    <>
      {/* Backdrop for Mobile */}
      {isOpen && (
        <div
          className="drawer-backdrop mobile-only"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`sidebar-drawer ${isOpen ? 'drawer-open' : ''}`}
        style={{
          width: '260px',
          borderRight: '1px solid var(--border-color)',
          background: 'var(--bg-secondary)',
          display: 'flex',
          flexDirection: 'column',
          height: '100%',
          flexShrink: 0
        }}
      >
        <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            className="btn btn-primary"
            style={{ flex: 1, justifyContent: 'center', fontSize: '13px', padding: '8px 12px' }}
            onClick={() => {
              onCreateSession();
              if (onClose) onClose();
            }}
          >
            <Plus size={15} />
            New Conversation
          </button>

          {/* Close button for Mobile Drawer */}
          <button
            className="btn-icon mobile-only"
            onClick={onClose}
            aria-label="Close menu"
            style={{ padding: '6px' }}
          >
            <X size={18} />
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
                  onClick={() => {
                    onSelectSession(s.session_id);
                    if (onClose) onClose();
                  }}
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
                    <MessageSquare size={14} color={isActive ? '#818cf8' : 'var(--text-muted)'} style={{ flexShrink: 0 }} />
                    <span style={{ fontSize: '13px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '160px' }}>
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
                      borderRadius: '4px',
                      display: 'flex',
                      alignItems: 'center'
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
    </>
  );
};
