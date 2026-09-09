import React, { useState, useEffect } from 'react';
import { getDocuments } from '../api/client';
import { ShieldAlert, ArrowRight, Search, FileText } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function ReviewQueue() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('needs_review');
  const [search, setSearch] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchQueue() {
      try {
        setLoading(true);
        const data = await getDocuments(filter === 'all' ? null : filter);
        setDocuments(data);
      } catch (err) {
        console.error("Failed to load review queue", err);
      } finally {
        setLoading(false);
      }
    }
    fetchQueue();
  }, [filter]);

  const filteredDocs = documents.filter(d => 
    d.filename.toLowerCase().includes(search.toLowerCase()) || 
    d.id.toString().includes(search)
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Header */}
      <div className="hero-banner" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 className="hero-title" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <ShieldAlert size={28} color="#f59e0b" />
            Human-in-the-Loop Verification Queue
          </h1>
          <p className="hero-desc">
            Official verifier workspace. Review low-confidence OCR extractions, correct flagged field values, and commit canonical records to PostGIS.
          </p>
        </div>

        {/* Search & Filter Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ position: 'relative' }}>
            <Search size={16} color="#94a3b8" style={{ position: 'absolute', left: '12px', top: '10px' }} />
            <input
              type="text"
              placeholder="Search filename or ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="form-input"
              style={{ paddingLeft: '36px', width: '220px' }}
            />
          </div>

          <div style={{ display: 'flex', gap: '4px', background: 'rgba(15, 23, 42, 0.8)', padding: '4px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            {['needs_review', 'auto_validated', 'verified', 'all'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className="btn-secondary"
                style={{
                  padding: '6px 12px',
                  fontSize: '0.75rem',
                  background: filter === f ? 'rgba(16, 185, 129, 0.2)' : 'transparent',
                  color: filter === f ? '#34d399' : '#94a3b8',
                  borderColor: filter === f ? 'rgba(16, 185, 129, 0.4)' : 'transparent'
                }}
              >
                {f.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Grid of Record Cards */}
      <div className="card-panel">
        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>
            Loading queue records...
          </div>
        ) : filteredDocs.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8', border: '1px dashed var(--border-subtle)', borderRadius: '12px' }}>
            No records matching status filter '{filter}'.
          </div>
        ) : (
          <div className="grid-4col">
            {filteredDocs.map((doc) => (
              <div key={doc.id} style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-subtle)', borderRadius: '12px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', display: 'flex', alignItems: 'center', justifyContents: 'center' }}>
                      <FileText size={20} />
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', fontFamily: 'monospace', color: '#94a3b8' }}>Record #{doc.id}</div>
                      <div style={{ fontSize: '0.875rem', fontWeight: '700', color: '#ffffff', maxWidth: '160px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {doc.filename}
                      </div>
                    </div>
                  </div>
                  <span className={`status-pill status-${doc.status}`}>
                    {doc.status.replace('_', ' ')}
                  </span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', paddingTop: '8px', borderTop: '1px solid rgba(255, 255, 255, 0.05)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#94a3b8' }}>
                    <span>Confidence Score</span>
                    <span style={{ fontFamily: 'monospace', color: '#ffffff', fontWeight: '700' }}>{(doc.overall_confidence * 100).toFixed(0)}%</span>
                  </div>
                  <div className="progress-bar-bg">
                    <div
                      className={`progress-bar-fill ${doc.overall_confidence >= 0.85 ? 'bg-emerald' : 'bg-amber'}`}
                      style={{ width: `${Math.max(10, doc.overall_confidence * 100)}%` }}
                    />
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '8px' }}>
                  <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                    {new Date(doc.created_at).toLocaleDateString()}
                  </span>
                  <button
                    onClick={() => navigate(`/review/${doc.id}`)}
                    className="btn-primary"
                    style={{ padding: '6px 12px', fontSize: '0.75rem', width: 'auto' }}
                  >
                    Verify <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
