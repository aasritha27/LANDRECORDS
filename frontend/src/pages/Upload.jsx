import React, { useState, useEffect } from 'react';
import { uploadDocument, getDocuments } from '../api/client';
import { UploadCloud, FileText, CheckCircle, ArrowRight, RefreshCw, AlertCircle, Cpu, ShieldCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Upload() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const navigate = useNavigate();

  const loadRecentDocs = async () => {
    try {
      setLoadingDocs(true);
      const data = await getDocuments();
      setDocuments(data);
    } catch (err) {
      console.error("Failed to load documents", err);
    } finally {
      setLoadingDocs(false);
    }
  };

  useEffect(() => {
    loadRecentDocs();
  }, []);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setUploadMessage(null);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    try {
      setIsUploading(true);
      setUploadMessage({ type: 'info', text: 'Processing document via AI OCR & Validation Engine...' });
      
      const response = await uploadDocument(selectedFile);
      
      setUploadMessage({
        type: 'success',
        text: `Record '${response.filename}' processed successfully! Status: ${response.status}`
      });
      setSelectedFile(null);
      loadRecentDocs();
    } catch (err) {
      setUploadMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Failed to process document. Please try again.'
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Official Banner */}
      <div className="hero-banner">
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', color: '#34d399', padding: '4px 12px', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: '700', marginBottom: '12px' }}>
          <Cpu size={14} /> AI-Powered Land Record Ingestion Pipeline
        </div>
        <h1 className="hero-title">
          Ingest & Digitise Land Records
        </h1>
        <p className="hero-desc">
          Upload scanned Khasra/Khata records, mutation notices, or cadastral survey maps. The automated AI engine performs deskewing, OCR extraction, rules engine validation, and confidence scoring.
        </p>
      </div>

      <div className="grid-3col">
        
        {/* Upload Form Box */}
        <div className="card-panel">
          <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.1rem', fontWeight: '700', color: '#ffffff', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <UploadCloud size={20} color="#10b981" />
            Upload Document Scan
          </h2>

          <form onSubmit={handleUpload} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div className="dropzone">
              <input
                type="file"
                accept=".jpg,.jpeg,.png,.pdf,.tiff"
                onChange={handleFileChange}
                style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', opacity: 0, cursor: 'pointer' }}
              />
              <div className="dropzone-icon">
                <UploadCloud size={24} />
              </div>
              <p style={{ fontSize: '0.875rem', fontWeight: '600', color: '#ffffff', marginBottom: '4px' }}>
                {selectedFile ? selectedFile.name : 'Choose or drag & drop scan file'}
              </p>
              <p style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                Supports PNG, JPG, JPEG, TIFF, PDF (Max 25MB)
              </p>
            </div>

            {uploadMessage && (
              <div style={{
                padding: '10px 14px',
                borderRadius: '8px',
                fontSize: '0.8rem',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                background: uploadMessage.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)',
                border: uploadMessage.type === 'success' ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(244, 63, 94, 0.3)',
                color: uploadMessage.type === 'success' ? '#34d399' : '#f87171'
              }}>
                {uploadMessage.type === 'success' ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
                {uploadMessage.text}
              </div>
            )}

            <button
              type="submit"
              disabled={!selectedFile || isUploading}
              className="btn-primary"
            >
              {isUploading ? (
                <>
                  <RefreshCw size={16} className="spin" /> Processing AI Pipeline...
                </>
              ) : (
                <>
                  Process Document <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>

          <div style={{ marginTop: '24px', paddingTop: '16px', borderTop: '1px solid var(--border-subtle)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            <div style={{ fontWeight: '700', color: '#ffffff', marginBottom: '6px' }}>Automated Pipeline Steps:</div>
            <ul style={{ paddingLeft: '16px', lineHeight: '1.6' }}>
              <li>OpenCV Deskewing & Noise Filtering</li>
              <li>Multi-lingual OCR (English / Hindi)</li>
              <li>Fuzzy Village & Format Validation</li>
              <li>Human-in-the-Loop Queue Routing</li>
            </ul>
          </div>
        </div>

        {/* Ingested Queue Table */}
        <div className="card-panel">
          <div style={{ display: 'flex', alignItems: 'center', justifyContents: 'space-between', marginBottom: '16px' }}>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.1rem', fontWeight: '700', color: '#ffffff', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={20} color="#06b6d4" />
              Ingested Document Registry
            </h2>
            <button
              onClick={loadRecentDocs}
              className="btn-secondary"
              style={{ padding: '6px 12px', fontSize: '0.75rem' }}
            >
              <RefreshCw size={14} /> Refresh
            </button>
          </div>

          {loadingDocs ? (
            <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8', fontSize: '0.875rem' }}>
              Loading document queue...
            </div>
          ) : documents.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8', fontSize: '0.875rem', border: '1px dashed var(--border-subtle)', borderRadius: '12px' }}>
              No documents ingested yet. Upload a land record scan above.
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Record ID</th>
                    <th>Filename</th>
                    <th>Status</th>
                    <th>AI Confidence</th>
                    <th style={{ textAlign: 'right' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc) => (
                    <tr key={doc.id}>
                      <td style={{ fontFamily: 'monospace', fontWeight: '700', color: '#94a3b8' }}>#{doc.id}</td>
                      <td style={{ fontWeight: '600', color: '#ffffff' }}>{doc.filename}</td>
                      <td>
                        <span className={`status-pill status-${doc.status}`}>
                          {doc.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                          <div className="progress-bar-bg" style={{ width: '80px' }}>
                            <div
                              className={`progress-bar-fill ${
                                doc.overall_confidence >= 0.85 ? 'bg-emerald' : 'bg-amber'
                              }`}
                              style={{ width: `${Math.max(15, doc.overall_confidence * 100)}%` }}
                            />
                          </div>
                          <span style={{ fontFamily: 'monospace', fontSize: '0.8rem', fontWeight: '700' }}>
                            {(doc.overall_confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <button
                          onClick={() => navigate(`/review/${doc.id}`)}
                          className="btn-secondary"
                        >
                          Inspect <ArrowRight size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
