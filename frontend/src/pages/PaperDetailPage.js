import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPaper, analyzePapers } from '../services/api';
import './PaperDetailPage.css';

export default function PaperDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [paper, setPaper] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    getPaper(parseInt(id))
      .then(setPaper)
      .catch(() => setError('Paper not found.'))
      .finally(() => setLoading(false));
  }, [id]);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const result = await analyzePapers([parseInt(id)]);
      const analysis = result.analyses?.[0]?.analysis;
      if (analysis) {
        setPaper(prev => ({ ...prev, analysis }));
      }
    } catch {
      setError('Analysis failed.');
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) return <div className="loading-overlay"><div className="spinner" /></div>;
  if (error) return <div className="container page"><div className="alert alert-error">{error}</div></div>;
  if (!paper) return null;

  const a = paper.analysis;

  return (
    <div className="container page">
      <button className="btn btn-ghost btn-sm" onClick={() => navigate(-1)} style={{ marginBottom: 16 }}>
        ← Back
      </button>

      <div className="paper-detail-layout">
        {/* Main Content */}
        <div className="paper-detail-main">
          <div className="card" style={{ padding: 24, marginBottom: 16 }}>
            <div className="paper-detail-badges" style={{ marginBottom: 12 }}>
              {paper.source && <span className="badge badge-blue">{paper.source}</span>}
              {paper.is_demo && <span className="badge badge-orange">Demo</span>}
              {paper.research_field && <span className="badge badge-purple">{paper.research_field}</span>}
              {paper.citation_count > 0 && <span className="badge badge-yellow">🏆 {paper.citation_count.toLocaleString()} citations</span>}
            </div>
            <h1 className="paper-detail-title">{paper.title}</h1>
            <div className="paper-detail-meta">
              {paper.authors?.map(a => a.name || a).join(', ')}
              {paper.year && ` · ${paper.year}`}
              {paper.journal && ` · ${paper.journal}`}
            </div>
            {paper.doi && <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>DOI: {paper.doi}</p>}
            <div style={{ display: 'flex', gap: 12, marginTop: 12 }}>
              {paper.url && <a href={paper.url} target="_blank" rel="noreferrer" className="btn btn-secondary btn-sm">🔗 View Paper</a>}
              {paper.pdf_url && <a href={paper.pdf_url} target="_blank" rel="noreferrer" className="btn btn-secondary btn-sm">📄 PDF</a>}
            </div>
          </div>

          {paper.abstract && (
            <div className="card" style={{ padding: 20, marginBottom: 16 }}>
              <h3 className="section-title">📋 Abstract</h3>
              <p style={{ fontSize: 14, lineHeight: 1.8, color: 'var(--text-muted)' }}>{paper.abstract}</p>
            </div>
          )}

          {paper.keywords?.length > 0 && (
            <div className="card" style={{ padding: 20, marginBottom: 16 }}>
              <h3 className="section-title">🏷️ Keywords</h3>
              <div className="tags">
                {paper.keywords.map(kw => <span key={kw} className="tag">{kw}</span>)}
              </div>
            </div>
          )}

          {/* Analysis Section */}
          {!a ? (
            <div className="card" style={{ padding: 20, textAlign: 'center' }}>
              <p style={{ color: 'var(--text-muted)', marginBottom: 12 }}>No AI analysis yet.</p>
              <button className="btn btn-primary" onClick={handleAnalyze} disabled={analyzing}>
                {analyzing ? '⏳ Analyzing...' : '🔬 Analyze with IBM watsonx.ai'}
              </button>
            </div>
          ) : (
            <div className="analysis-grid">
              {[
                ['Problem Statement', a.problem_statement, '❓'],
                ['Objective', a.objective, '🎯'],
                ['Methodology', a.methodology, '🔬'],
                ['Dataset', a.dataset, '💾'],
                ['Results', a.results, '📊'],
                ['Key Findings', a.key_findings, '✨'],
                ['Limitations', a.limitations, '⚠️'],
                ['Future Work', a.future_work, '🔭'],
              ].map(([label, value, icon]) => value && (
                <div key={label} className="analysis-card card">
                  <h4 className="analysis-label">{icon} {label}</h4>
                  <p className="analysis-value">{value}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Sidebar */}
        <aside className="paper-detail-sidebar">
          <div className="card" style={{ padding: 16 }}>
            <h3 className="section-title">📊 Paper Metadata</h3>
            <div className="metadata-grid">
              {[
                ['Source', paper.source],
                ['Year', paper.year],
                ['Citations', paper.citation_count],
                ['Field', paper.research_field],
                ['Journal', paper.journal],
              ].map(([label, val]) => val != null && (
                <div key={label} className="metadata-row">
                  <span className="metadata-label">{label}</span>
                  <span className="metadata-val">{val}</span>
                </div>
              ))}
            </div>
          </div>
          {paper.authors?.length > 0 && (
            <div className="card" style={{ padding: 16, marginTop: 16 }}>
              <h3 className="section-title">👥 Authors</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {paper.authors.map((auth, i) => (
                  <div key={i} style={{ fontSize: 13 }}>{auth.name || auth}</div>
                ))}
              </div>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
