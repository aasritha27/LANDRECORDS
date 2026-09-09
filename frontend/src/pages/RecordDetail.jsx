import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getDocumentById, verifyDocument } from '../api/client';
import { ArrowLeft, CheckCircle2, AlertTriangle, ShieldCheck, Edit3, Eye } from 'lucide-react';

export default function RecordDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [doc, setDoc] = useState(null);
  const [loading, setLoading] = useState(true);
  const [edits, setEdits] = useState({});
  const [isSaving, setIsSaving] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);

  useEffect(() => {
    async function loadDetail() {
      try {
        setLoading(true);
        const data = await getDocumentById(id);
        setDoc(data);
        
        const initialEdits = {};
        data.extracted_fields.forEach(field => {
          initialEdits[field.id] = field.corrected_value || field.field_value || '';
        });
        setEdits(initialEdits);
      } catch (err) {
        console.error("Failed to load document details", err);
      } finally {
        setLoading(false);
      }
    }
    loadDetail();
  }, [id]);

  const handleFieldChange = (fieldId, val) => {
    setEdits(prev => ({ ...prev, [fieldId]: val }));
  };

  const handleVerify = async (approve = true) => {
    try {
      setIsSaving(true);
      const updates = Object.keys(edits).map(fieldId => ({
        field_id: parseInt(fieldId),
        corrected_value: edits[fieldId],
        validation_notes: "Verifier approved field corrections."
      }));

      await verifyDocument(id, { updates, approve });
      setStatusMessage({ type: 'success', text: approve ? 'Record verified & committed to PostGIS database!' : 'Record updated successfully!' });
      
      const refreshed = await getDocumentById(id);
      setDoc(refreshed);
    } catch (err) {
      setStatusMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to save verification.' });
    } finally {
      setIsSaving(false);
    }
  };

  if (loading) return <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>Loading workspace...</div>;
  if (!doc) return <div style={{ padding: '40px', textAlign: 'center', color: '#f87171' }}>Document #{id} not found.</div>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Action Header */}
      <div className="card-panel" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button onClick={() => navigate('/review')} className="btn-secondary">
            <ArrowLeft size={16} /> Back
          </button>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h1 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: '700', color: '#ffffff' }}>{doc.filename}</h1>
              <span className={`status-pill status-${doc.status}`}>{doc.status.replace('_', ' ')}</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Record ID: #{doc.id} • Created: {new Date(doc.created_at).toLocaleString()}</div>
          </div>
        </div>

        <button onClick={() => handleVerify(true)} disabled={isSaving} className="btn-primary" style={{ width: 'auto' }}>
          <ShieldCheck size={18} /> Approve & Commit to PostGIS
        </button>
      </div>

      {statusMessage && (
        <div style={{
          padding: '12px 16px',
          borderRadius: '8px',
          fontSize: '0.85rem',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          background: statusMessage.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)',
          border: statusMessage.type === 'success' ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(244, 63, 94, 0.3)',
          color: statusMessage.type === 'success' ? '#34d399' : '#f87171'
        }}>
          {statusMessage.type === 'success' ? <CheckCircle2 size={18} /> : <AlertTriangle size={18} />}
          {statusMessage.text}
        </div>
      )}

      {/* Side-by-Side Split Workspace */}
      <div className="grid-2col">
        
        {/* Left Column: Image Viewer */}
        <div className="card-panel" style={{ height: '650px', display: 'flex', flexDirection: 'column' }}>
          <div style={{ paddingBottom: '12px', marginBottom: '12px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#94a3b8' }}>
            <span style={{ fontWeight: '700', color: '#ffffff', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Eye size={16} color="#06b6d4" /> Scanned Document Viewer
            </span>
            <span>{doc.preprocessed_filepath ? 'Preprocessed View' : 'Original Scan'}</span>
          </div>

          <div style={{ flex: 1, background: '#020617', borderRadius: '12px', border: '1px solid var(--border-subtle)', padding: '8px', display: 'flex', alignItems: 'center', justifyContents: 'center', overflow: 'hidden' }}>
            <img
              src={`/${doc.preprocessed_filepath || doc.original_filepath}`}
              alt="Scan"
              style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }}
              onError={(e) => {
                e.target.src = 'https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=600&auto=format&fit=crop&q=60';
              }}
            />
          </div>
        </div>

        {/* Right Column: Editable Fields */}
        <div className="card-panel" style={{ maxHeight: '650px', overflowY: 'auto' }}>
          <div style={{ marginBottom: '16px' }}>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.1rem', fontWeight: '700', color: '#ffffff', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Edit3 size={18} color="#10b981" />
              Extracted Fields Verification
            </h2>
            <p style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
              Review extracted values and edit any OCR mistakes before approving.
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {doc.extracted_fields.map((field) => {
              const isLowConf = field.confidence_score < 0.85;
              return (
                <div key={field.id} style={{
                  padding: '14px',
                  borderRadius: '10px',
                  background: isLowConf ? 'rgba(245, 158, 11, 0.05)' : 'rgba(15, 23, 42, 0.6)',
                  border: isLowConf ? '1px solid rgba(245, 158, 11, 0.3)' : '1px solid var(--border-subtle)'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <label style={{ fontSize: '0.75rem', fontWeight: '700', color: '#cbd5e1', textTransform: 'capitalize' }}>
                      {field.field_name.replace(/_/g, ' ')}
                    </label>
                    <span style={{ fontSize: '0.7rem', fontWeight: '700', padding: '2px 6px', borderRadius: '4px', background: isLowConf ? 'rgba(245, 158, 11, 0.2)' : 'rgba(16, 185, 129, 0.2)', color: isLowConf ? '#fbbf24' : '#34d399' }}>
                      Conf: {Math.round(field.confidence_score * 100)}%
                    </span>
                  </div>

                  <input
                    type="text"
                    value={edits[field.id] || ''}
                    onChange={(e) => handleFieldChange(field.id, e.target.value)}
                    className="form-input"
                  />
                </div>
              );
            })}
          </div>
        </div>

      </div>
    </div>
  );
}
