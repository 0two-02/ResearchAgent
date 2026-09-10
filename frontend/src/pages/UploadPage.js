import React, { useState, useCallback } from 'react';
import { uploadDocument, analyzeDocument, getDocuments } from '../services/api';
import './UploadPage.css';

export default function UploadPage() {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploads, setUploads] = useState([]);
  const [error, setError] = useState('');
  const [analysisResults, setAnalysisResults] = useState({});

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragging(false);
    const files = Array.from(e.dataTransfer.files);
    files.forEach(processFile);
  }, []);

  const handleFileInput = (e) => {
    Array.from(e.target.files).forEach(processFile);
  };

  const processFile = async (file) => {
    setError('');
    const allowedTypes = ['.pdf', '.txt', '.md', '.csv', '.text'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowedTypes.includes(ext)) {
      setError(`Unsupported file type: ${ext}. Allowed: ${allowedTypes.join(', ')}`);
      return;
    }
    if (file.size > 50 * 1024 * 1024) {
      setError(`File too large: ${(file.size / 1e6).toFixed(1)} MB. Max: 50 MB`);
      return;
    }

    setUploading(true);
    try {
      const result = await uploadDocument(file);
      setUploads(prev => [result, ...prev]);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed.');
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyze = async (docId) => {
    try {
      const result = await analyzeDocument(docId);
      setAnalysisResults(prev => ({ ...prev, [docId]: result }));
    } catch (err) {
      setError('Analysis failed.');
    }
  };

  return (
    <div className="container page">
      <div className="page-header">
        <h1 className="page-title">📄 Upload Research Documents</h1>
        <p className="page-subtitle">Upload PDFs, text files, or CSVs. AI extracts, indexes, and makes them searchable.</p>
      </div>

      {/* Drop Zone */}
      <div
        className={`drop-zone card ${dragging ? 'dragging' : ''}`}
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onClick={() => document.getElementById('file-input').click()}
      >
        <div className="drop-icon">📁</div>
        <h3>Drag & Drop or Click to Upload</h3>
        <p>Supported: PDF, TXT, MD, CSV (max 50 MB)</p>
        <input
          id="file-input"
          type="file"
          accept=".pdf,.txt,.md,.csv,.text"
          multiple
          style={{ display: 'none' }}
          onChange={handleFileInput}
        />
        {uploading && (
          <div style={{ marginTop: 12 }}>
            <div className="spinner" style={{ margin: '0 auto' }} />
            <p style={{ marginTop: 8, fontSize: 13 }}>Processing...</p>
          </div>
        )}
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {/* Processing Pipeline Info */}
      <div className="pipeline-info card">
        <h3 className="section-title">⚙️ Processing Pipeline</h3>
        <div className="pipeline-steps">
          {[
            { icon: '📄', label: 'File Upload' },
            { icon: '✂️', label: 'Text Extraction' },
            { icon: '🔪', label: 'Text Chunking' },
            { icon: '🧮', label: 'Embedding Generation' },
            { icon: '🗄️', label: 'Vector Store Index' },
            { icon: '🔍', label: 'Semantic Search Ready' },
          ].map((step, i, arr) => (
            <React.Fragment key={step.label}>
              <div className="pipeline-step">
                <div className="pipeline-step-icon">{step.icon}</div>
                <div className="pipeline-step-label">{step.label}</div>
              </div>
              {i < arr.length - 1 && <span className="pipeline-arrow">→</span>}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Upload Results */}
      {uploads.length > 0 && (
        <div>
          <h3 className="section-title" style={{ marginTop: 24 }}>✅ Uploaded Documents</h3>
          <div className="upload-list">
            {uploads.map((doc) => (
              <div key={doc.id} className="upload-item card">
                <div className="upload-item-header">
                  <div className="upload-item-info">
                    <span className="upload-filename">{doc.filename}</span>
                    <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
                      <span className="badge badge-blue">{doc.file_type.toUpperCase()}</span>
                      <span className="badge badge-green">{doc.chunk_count} chunks</span>
                      {doc.is_indexed && <span className="badge badge-purple">Indexed</span>}
                      <span className="badge badge-yellow">{(doc.file_size / 1024).toFixed(1)} KB</span>
                    </div>
                  </div>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => handleAnalyze(doc.id)}
                  >
                    🔬 Analyze with AI
                  </button>
                </div>
                {doc.detected_title && (
                  <p style={{ fontSize: 13, marginTop: 8 }}><strong>Detected Title:</strong> {doc.detected_title}</p>
                )}
                {doc.detected_abstract && (
                  <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 4 }}>{doc.detected_abstract.slice(0, 300)}...</p>
                )}
                {analysisResults[doc.id] && (
                  <div className="upload-analysis">
                    <strong>AI Analysis:</strong>
                    <p style={{ whiteSpace: 'pre-wrap', fontSize: 13, color: 'var(--text-muted)', marginTop: 8 }}>
                      {analysisResults[doc.id].insights}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
