import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { comparePapers, analyzePapers } from '../services/api';
import './ComparePage.css';

export default function ComparePage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  const paperIdsParam = searchParams.get('papers') || '';
  const paperIds = paperIdsParam.split(',').map(s => parseInt(s)).filter(n => !isNaN(n));

  useEffect(() => {
    if (paperIds.length >= 2) {
      handleCompare();
    }
  }, []);

  const handleCompare = async () => {
    if (paperIds.length < 2) { setError('Need at least 2 papers.'); return; }
    setLoading(true);
    setError('');
    try {
      // First analyze papers
      await analyzePapers(paperIds);
      const result = await comparePapers(paperIds);
      setData(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Comparison failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleExportCSV = () => {
    if (!data) return;
    const headers = ['Feature', ...data.papers.map((p, i) => `Paper ${i+1}: ${p.title?.slice(0,40)}`)];
    const rows = (data.comparison_table || []).map(row =>
      [row.feature, ...data.papers.map((_, i) => row[`paper_${i+1}`] || '')].map(v => `"${String(v).replace(/"/g, '""')}"`)
    );
    const csv = [headers, ...rows].map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'paper-comparison.csv';
    a.click();
  };

  if (loading) return (
    <div className="loading-overlay">
      <div className="spinner" />
      <p>🔬 Paper Analysis Agents working...</p>
      <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>Analyzing and comparing {paperIds.length} papers</p>
    </div>
  );

  return (
    <div className="container page">
      <div className="page-header">
        <button className="btn btn-ghost btn-sm" onClick={() => navigate(-1)}>← Back</button>
        <h1 className="page-title" style={{ marginTop: 12 }}>📊 Paper Comparison</h1>
        <p className="page-subtitle">AI-powered side-by-side comparison of selected papers</p>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {!data && !loading && (
        <div className="card" style={{ padding: 40, textAlign: 'center' }}>
          <p>Papers: {paperIds.join(', ')}</p>
          <button className="btn btn-primary" onClick={handleCompare} style={{ marginTop: 16 }}>
            🔬 Run Comparison
          </button>
        </div>
      )}

      {data && (
        <>
          {/* Paper Headers */}
          <div className="compare-paper-headers">
            {data.papers.map((p, i) => (
              <div key={p.id} className="compare-paper-header card">
                <span className="badge badge-blue">Paper {i + 1}</span>
                <h4 className="compare-paper-title">{p.title}</h4>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
                  {p.authors?.slice(0,2).map(a => a.name || a).join(', ')}
                  {p.year && ` · ${p.year}`}
                </div>
                {p.citation_count > 0 && (
                  <span className="badge badge-yellow" style={{ marginTop: 6 }}>🏆 {p.citation_count.toLocaleString()}</span>
                )}
              </div>
            ))}
          </div>

          {/* Comparison Table */}
          <div className="card compare-table-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h3 className="section-title">Comparison Table</h3>
              <button className="btn btn-secondary btn-sm" onClick={handleExportCSV}>📥 Export CSV</button>
            </div>
            <div className="compare-table-wrapper">
              <table className="compare-table">
                <thead>
                  <tr>
                    <th>Feature</th>
                    {data.papers.map((p, i) => (
                      <th key={p.id}>Paper {i + 1}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(data.comparison_table || []).map((row, i) => (
                    <tr key={i}>
                      <td className="compare-feature">{row.feature}</td>
                      {data.papers.map((_, j) => (
                        <td key={j} className="compare-cell">{row[`paper_${j+1}`] || '—'}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* AI Summary */}
          {data.ai_summary && (
            <div className="card" style={{ padding: 20 }}>
              <h3 className="section-title">🤖 AI Comparison Summary</h3>
              <div className="alert alert-info" style={{ marginBottom: 12 }}>
                ℹ️ Generated by IBM watsonx.ai based on analyzed paper metadata.
              </div>
              <p style={{ fontSize: 14, lineHeight: 1.8, whiteSpace: 'pre-wrap' }}>{data.ai_summary}</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
