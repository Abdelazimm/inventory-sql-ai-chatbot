import React from 'react';
import { Terminal, CheckCircle, AlertTriangle, Clock, Layers } from 'lucide-react';
import { ChatMetadata } from '../types';

interface DebugPanelProps {
  metadata?: ChatMetadata;
}

export const DebugPanel: React.FC<DebugPanelProps> = ({ metadata }) => {
  if (!metadata || !metadata.generated_sql) {
    return (
      <div style={{
        padding: '10px 14px',
        background: 'rgba(0, 0, 0, 0.4)',
        border: '1px dashed var(--border-color)',
        borderRadius: 'var(--radius-md)',
        fontSize: '11px',
        color: 'var(--text-muted)',
        marginTop: '8px'
      }}>
        No SQL query executed for this response.
      </div>
    );
  }

  return (
    <div style={{
      marginTop: '10px',
      padding: '12px 14px',
      background: 'rgba(15, 23, 42, 0.85)',
      border: '1px solid rgba(99, 102, 241, 0.25)',
      borderRadius: 'var(--radius-md)',
      fontSize: '12px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '6px 12px', marginBottom: '8px', borderBottom: '1px solid var(--border-color)', paddingBottom: '6px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#818cf8', fontWeight: 600 }}>
          <Terminal size={14} />
          SQL Execution Telemetry
        </div>
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '8px 12px', color: 'var(--text-secondary)', fontSize: '11px' }}>
          {metadata.execution_time_ms !== undefined && (
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Clock size={12} /> {metadata.execution_time_ms}ms
            </span>
          )}
          {metadata.row_count !== undefined && (
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Layers size={12} /> {metadata.row_count} rows
            </span>
          )}
          {metadata.retry_count !== undefined && metadata.retry_count > 0 && (
            <span style={{ color: 'var(--warning)', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <AlertTriangle size={12} /> Retries: {metadata.retry_count}
            </span>
          )}
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: metadata.is_valid_sql ? 'var(--success)' : 'var(--danger)' }}>
            <CheckCircle size={12} /> {metadata.is_valid_sql ? 'Validated' : 'Invalid'}
          </span>
        </div>
      </div>

      <pre style={{
        background: '#070b12',
        padding: '8px 12px',
        borderRadius: '6px',
        color: '#93c5fd',
        fontSize: '11px',
        overflowX: 'auto',
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word',
        border: '1px solid rgba(255, 255, 255, 0.05)'
      }}>
        {metadata.generated_sql}
      </pre>
    </div>
  );
};
