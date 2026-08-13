import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, Loader2 } from 'lucide-react';
import { Message } from '../types';
import { DebugPanel } from './DebugPanel';

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (text: string) => void;
  debugMode: boolean;
}

const EXAMPLE_QUESTIONS = [
  "What is the most expensive asset?",
  "Which vendor supplied the most expensive asset?",
  "How many assets are currently in repair?",
  "What is the total value of assets at HQ?",
  "Which location contains the most assets?",
  "Show all purchase orders that are Open."
];

export const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  isLoading,
  onSendMessage,
  debugMode
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', position: 'relative' }}>
      {/* Messages Scroll Area */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px 32px' }}>
        {messages.length === 0 ? (
          <div style={{ maxWidth: '640px', margin: '40px auto', textAlign: 'center' }}>
            <div style={{
              width: '60px',
              height: '60px',
              borderRadius: '16px',
              background: 'var(--accent-gradient)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 20px auto',
              boxShadow: 'var(--accent-glow)'
            }}>
              <Sparkles size={32} color="#fff" />
            </div>
            <h2 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '8px' }}>
              Welcome to Inventory SQL Assistant
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '28px' }}>
              Ask natural language questions about your inventory, assets, vendors, locations, purchase orders, and sales orders.
            </p>

            <div style={{ textAlign: 'left' }}>
              <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '12px' }}>
                Example Questions:
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '10px' }}>
                {EXAMPLE_QUESTIONS.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => onSendMessage(q)}
                    style={{
                      padding: '12px 16px',
                      background: 'rgba(31, 41, 55, 0.4)',
                      border: '1px solid var(--border-color)',
                      borderRadius: 'var(--radius-md)',
                      color: 'var(--text-primary)',
                      textAlign: 'left',
                      fontSize: '13px',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease'
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.5)')}
                    onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--border-color)')}
                  >
                    "{q}"
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {messages.map((msg) => {
              const isUser = msg.sender === 'user';
              return (
                <div
                  key={msg.id}
                  className="animate-fade-in"
                  style={{
                    display: 'flex',
                    gap: '14px',
                    alignSelf: isUser ? 'flex-end' : 'flex-start',
                    maxWidth: '85%'
                  }}
                >
                  {!isUser && (
                    <div style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '8px',
                      background: 'var(--accent-gradient)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0
                    }}>
                      <Bot size={18} color="#fff" />
                    </div>
                  )}

                  <div style={{ flex: 1 }}>
                    <div style={{
                      padding: '14px 18px',
                      borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                      background: isUser ? 'var(--accent-gradient)' : 'rgba(31, 41, 55, 0.6)',
                      border: isUser ? 'none' : '1px solid var(--border-color)',
                      color: '#fff',
                      fontSize: '14px',
                      whiteSpace: 'pre-wrap',
                      lineHeight: 1.6
                    }}>
                      {msg.text}
                    </div>

                    {/* Show Debug Panel if Assistant message and Debug mode is ON */}
                    {!isUser && debugMode && (
                      <DebugPanel metadata={msg.metadata} />
                    )}
                  </div>

                  {isUser && (
                    <div style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '8px',
                      background: 'var(--bg-tertiary)',
                      border: '1px solid var(--border-color)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0
                    }}>
                      <User size={18} color="var(--text-secondary)" />
                    </div>
                  )}
                </div>
              );
            })}

            {isLoading && (
              <div style={{ display: 'flex', gap: '14px', alignSelf: 'flex-start', maxWidth: '85%' }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '8px',
                  background: 'var(--accent-gradient)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  <Bot size={18} color="#fff" />
                </div>
                <div style={{
                  padding: '14px 18px',
                  borderRadius: '16px 16px 16px 4px',
                  background: 'rgba(31, 41, 55, 0.6)',
                  border: '1px solid var(--border-color)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontSize: '14px',
                  color: 'var(--text-secondary)'
                }}>
                  <Loader2 size={16} className="animate-spin" />
                  Analyzing relational schema & generating SQL...
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Form Bar */}
      <div style={{
        padding: '16px 24px',
        borderTop: '1px solid var(--border-color)',
        background: 'rgba(11, 15, 25, 0.95)'
      }}>
        <form onSubmit={handleSubmit} style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', gap: '12px' }}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your inventory (e.g., 'What is the most expensive asset?')..."
            rows={1}
            style={{
              flex: 1,
              padding: '12px 16px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-color)',
              color: '#fff',
              fontSize: '14px',
              resize: 'none',
              outline: 'none',
              fontFamily: 'inherit'
            }}
            onFocus={(e) => (e.target.style.borderColor = 'var(--accent-primary)')}
            onBlur={(e) => (e.target.style.borderColor = 'var(--border-color)')}
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={!input.trim() || isLoading}
            style={{ opacity: !input.trim() || isLoading ? 0.5 : 1, padding: '0 20px' }}
          >
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
};
