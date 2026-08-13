import React, { useState } from 'react';
import { X, Upload, Check, AlertCircle, FileText } from 'lucide-react';
import { api } from '../services/api';
import { IngestPreview } from '../types';

interface CSVUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CSVUploadModal: React.FC<CSVUploadModalProps> = ({ isOpen, onClose }) => {
  const [entityType, setEntityType] = useState('assets');
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<IngestPreview | null>(null);
  const [loading, setLoading] = useState(false);
  const [commitResult, setCommitResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setPreview(null);
      setCommitResult(null);
      setError(null);
    }
  };

  const handlePreview = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.previewCSV(entityType, file);
      setPreview(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to parse CSV preview.');
    } finally {
      setLoading(false);
    }
  };

  const handleCommit = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const result = await api.commitCSV(entityType, file);
      setCommitResult(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to commit CSV ingestion.');
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
      <div className="glass-panel" style={{ width: '680px', maxHeight: '85vh', display: 'flex', flexDirection: 'column', padding: '24px', position: 'relative' }}>
        <button
          onClick={onClose}
          style={{ position: 'absolute', top: '16px', right: '16px', background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
        >
          <X size={18} />
        </button>

        <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '6px' }}>
          CSV Data Ingestion Pipeline
        </h3>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '20px' }}>
          Upload inventory records with schema validation, transactional preview, and atomic rollback.
        </p>

        {error && (
          <div style={{ padding: '10px 14px', background: 'rgba(239, 68, 68, 0.2)', border: '1px solid rgba(239, 68, 68, 0.4)', borderRadius: '6px', color: '#fca5a5', fontSize: '13px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={16} />
            {error}
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '12px', marginBottom: '16px' }}>
          <div>
            <label style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>
              Target Entity
            </label>
            <select
              value={entityType}
              onChange={(e) => setEntityType(e.target.value)}
              style={{ width: '100%', padding: '8px 12px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '6px', color: '#fff', fontSize: '13px', outline: 'none' }}
            >
              <option value="assets">Assets</option>
              <option value="vendors">Vendors</option>
              <option value="items">Items</option>
              <option value="sites">Sites</option>
              <option value="locations">Locations</option>
              <option value="customers">Customers</option>
            </select>
          </div>

          <div>
            <label style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>
              Choose CSV File
            </label>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              style={{ width: '100%', padding: '6px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '6px', color: '#fff', fontSize: '13px' }}
            />
          </div>
        </div>

        {!preview && !commitResult && (
          <button
            className="btn btn-secondary"
            onClick={handlePreview}
            disabled={!file || loading}
            style={{ width: '100%', marginBottom: '12px' }}
          >
            <Upload size={16} />
            {loading ? 'Validating & Parsing...' : 'Preview CSV'}
          </button>
        )}

        {/* Preview Results */}
        {preview && !commitResult && (
          <div style={{ flex: 1, overflowY: 'auto', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                Found {preview.total_rows} rows. Schema Valid: {preview.is_valid ? '✅ Yes' : '❌ No'}
              </span>
              {preview.missing_required_columns.length > 0 && (
                <span style={{ fontSize: '12px', color: 'var(--danger)' }}>
                  Missing: {preview.missing_required_columns.join(', ')}
                </span>
              )}
            </div>

            <div style={{ maxHeight: '200px', overflow: 'auto', border: '1px solid var(--border-color)', borderRadius: '6px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', textAlign: 'left' }}>
                <thead style={{ background: 'var(--bg-secondary)', color: 'var(--text-muted)' }}>
                  <tr>
                    {preview.columns_found.map((col, i) => (
                      <th key={i} style={{ padding: '6px 10px', borderBottom: '1px solid var(--border-color)' }}>{col}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {preview.preview.map((row, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                      {preview.columns_found.map((col, cIdx) => (
                        <td key={cIdx} style={{ padding: '6px 10px' }}>{String(row[col])}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <button
              className="btn btn-primary"
              onClick={handleCommit}
              disabled={!preview.is_valid || loading}
              style={{ width: '100%', marginTop: '16px' }}
            >
              <Check size={16} />
              {loading ? 'Importing...' : `Confirm & Ingest ${preview.total_rows} Records`}
            </button>
          </div>
        )}

        {/* Commit Success State */}
        {commitResult && (
          <div style={{ padding: '16px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', marginBottom: '16px' }}>
            <h4 style={{ color: '#6ee7b7', fontSize: '15px', fontWeight: 600, marginBottom: '8px' }}>
              Ingestion Completed Successfully
            </h4>
            <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              Total: {commitResult.total_processed} | Inserted: {commitResult.inserted} | Updated: {commitResult.updated} | Rejected: {commitResult.rejected}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
