import React, { useState } from 'react';
import { X, ShieldAlert, CheckCircle, Trash2, Edit, Plus } from 'lucide-react';
import { api } from '../services/api';
import { MutationPreview } from '../types';

interface MutationModalProps {
  isOpen: boolean;
  onClose: () => void;
  userRole?: string;
}

export const MutationModal: React.FC<MutationModalProps> = ({ isOpen, onClose, userRole }) => {
  const [action, setAction] = useState('create');
  const [entityType, setEntityType] = useState('asset');
  const [entityId, setEntityId] = useState('');
  const [fieldsJson, setFieldsJson] = useState('{\n  "AssetTag": "TAG-9999",\n  "AssetName": "Test MacBook",\n  "SiteId": 1,\n  "Cost": 1999.00\n}');
  const [preview, setPreview] = useState<MutationPreview | null>(null);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handlePreview = async () => {
    setError(null);
    setLoading(true);
    try {
      const parsedFields = action === 'delete' ? {} : JSON.parse(fieldsJson);
      const data = await api.previewMutation(action, entityType, entityId || undefined, parsedFields);
      setPreview(data);
    } catch (err: any) {
      setError(err.message || err.response?.data?.detail || 'Failed to prepare mutation preview.');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!preview) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.confirmMutation(preview.action_id);
      setResult(res);
      setPreview(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to execute mutation.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(6px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div className="glass-panel" style={{ width: '560px', padding: '24px', position: 'relative' }}>
        <button
          onClick={onClose}
          style={{ position: 'absolute', top: '16px', right: '16px', background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
        >
          <X size={18} />
        </button>

        <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '6px' }}>
          Safe Parameterized Mutation Control
        </h3>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
          Execute authorized changes with 2-step verification. The LLM cannot execute raw arbitrary DML.
        </p>

        {error && (
          <div style={{ padding: '8px 12px', background: 'rgba(239, 68, 68, 0.2)', border: '1px solid rgba(239, 68, 68, 0.4)', borderRadius: '6px', color: '#fca5a5', fontSize: '12px', marginBottom: '14px' }}>
            {error}
          </div>
        )}

        {!preview && !result && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <div>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Action</label>
                <select
                  value={action}
                  onChange={(e) => setAction(e.target.value)}
                  style={{ width: '100%', padding: '8px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '6px', color: '#fff', fontSize: '13px' }}
                >
                  <option value="create">Create New Record</option>
                  <option value="update">Update Existing Record</option>
                  {userRole === 'admin' && <option value="delete">Delete Record (Admin Only)</option>}
                </select>
              </div>

              <div>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Entity Type</label>
                <select
                  value={entityType}
                  onChange={(e) => setEntityType(e.target.value)}
                  style={{ width: '100%', padding: '8px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '6px', color: '#fff', fontSize: '13px' }}
                >
                  <option value="asset">Asset</option>
                  <option value="vendor">Vendor</option>
                  <option value="item">Item</option>
                </select>
              </div>
            </div>

            {(action === 'update' || action === 'delete') && (
              <div>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Entity Identifier (Code/Tag)</label>
                <input
                  type="text"
                  value={entityId}
                  onChange={(e) => setEntityId(e.target.value)}
                  placeholder="e.g. TAG-1001 or V001"
                  style={{ width: '100%', padding: '8px 12px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '6px', color: '#fff', fontSize: '13px' }}
                />
              </div>
            )}

            {action !== 'delete' && (
              <div>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Fields JSON</label>
                <textarea
                  value={fieldsJson}
                  onChange={(e) => setFieldsJson(e.target.value)}
                  rows={4}
                  style={{ width: '100%', padding: '8px 12px', background: '#090d16', border: '1px solid var(--border-color)', borderRadius: '6px', color: '#38bdf8', fontFamily: 'JetBrains Mono', fontSize: '12px' }}
                />
              </div>
            )}

            <button className="btn btn-secondary" onClick={handlePreview} disabled={loading} style={{ marginTop: '8px' }}>
              Generate Confirmation Preview
            </button>
          </div>
        )}

        {preview && (
          <div style={{ padding: '16px', background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#fcd34d', fontWeight: 600, marginBottom: '8px' }}>
              <ShieldAlert size={18} />
              Explicit Confirmation Required
            </div>
            <p style={{ fontSize: '13px', color: '#fff', marginBottom: '12px' }}>{preview.summary}</p>
            <pre style={{ background: '#090d16', padding: '8px', borderRadius: '6px', fontSize: '11px', color: '#93c5fd', marginBottom: '16px' }}>
              {JSON.stringify(preview.fields, null, 2)}
            </pre>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button className="btn btn-danger" onClick={handleConfirm} disabled={loading} style={{ flex: 1 }}>
                Confirm & Execute Mutation
              </button>
              <button className="btn btn-secondary" onClick={() => setPreview(null)}>
                Cancel
              </button>
            </div>
          </div>
        )}

        {result && (
          <div style={{ padding: '16px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#6ee7b7', fontWeight: 600 }}>
              <CheckCircle size={18} />
              {result.message}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
