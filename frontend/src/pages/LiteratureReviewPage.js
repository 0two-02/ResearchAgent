import React, { useState } from 'react';
import { generateLiteratureReview, getPapers } from '../services/api';
import ReactMarkdown from 'react-markdown';
import './LiteratureReviewPage.css';

export default function LiteratureReviewPage() {
  const [topic, setTopic] = useState('');
  const [paperIds, setPaperIds] = useState('');
  const [loading, setLoading] = useState(false);
  const [review, setReview] = useState(null);
  const [error, setError] = useState('');

  const handleGenerate = async () => {
    setError('');
    const ids = paperIds
      .split(',')
      .map(s => parseInt(s.trim()))
      .filter(n => !isNaN(n));

    if (ids.length === 0) {
      setError('Enter comma-separated paper IDs. Go to Workspace, search papers, and note their IDs.');
      return;
    }
    setLoading(true);
    try {
      const data = await generateLiteratureReview({
        paper_ids: ids,
        topic: topic || 'Research Analysis',
      });
      setReview(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate literature review.');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    if (!review) return;
    const content = review.full_text || '';
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'literature-review.md';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="container page">
      <div className="page-header">
        <h1 className="page-title">📝 Literature Review Generator</h1>
        <p className="page-subtitle">Generate structured literature reviews from selected papers using IBM watsonx.ai</p>
      </div>

      <div className="lr-layout">
        <div className="lr-controls card">
          <h3 className="section-title">⚙️ Configuration</h3>
          <div style={{ marginBottom: 12 }}>
            <label style={{ fontSize: 12, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>Research Topic</label>
            <input
              className="input"
              placeholder="e.g., Deep learning in medical imaging"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />
          </div>
          <div style={{ marginBottom: 12 }}>
            <label style={{ fontSize: 12, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>Paper IDs (comma-separated)</label>
            <input
              className="input"
              placeholder="e.g., 1, 2, 3, 4, 5"
              value={paperIds}
              onChange={(e) => setPaperIds(e.target.value)}
            />
            <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
              💡 Search papers in Workspace first, then enter their IDs here.
            </p>
          </div>
          {error && <div className="alert alert-error">{error}</div>}
          <button className="btn btn-primary" style={{ width: '100%' }} onClick={handleGenerate} disabled={loading}>
            {loading ? '⏳ Generating Review...' : '📝 Generate Literature Review'}
          </button>
          {loading && (
            <div style={{ marginTop: 12, fontSize: 12, color: 'var(--text-muted)', textAlign: 'center' }}>
              <p>🤖 Literature Review Agent is working...</p>
              <p>Analyzing papers and synthesizing findings</p>
            </div>
          )}
        </div>

        <div className="lr-content">
          {!review && !loading && (
            <div className="lr-empty card">
              <div style={{ fontSize: 48 }}>📝</div>
              <h3>No Literature Review Yet</h3>
              <p>Configure the settings on the left and click Generate.</p>
              <div className="lr-sections-preview">
                <strong>Generated sections will include:</strong>
                <ul>
                  <li>Introduction</li>
                  <li>Existing Research</li>
                  <li>Major Approaches & Methods</li>
                  <li>Comparison of Methods</li>
                  <li>Important Findings</li>
                  <li>Limitations</li>
                  <li>Research Gaps</li>
                  <li>Emerging Trends</li>
                  <li>Future Research Directions</li>
                </ul>
              </div>
            </div>
          )}

          {review && (
            <div className="lr-result">
              <div className="lr-result-header">
                <h2>{review.title}</h2>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button className="btn btn-secondary btn-sm" onClick={handleExport}>
                    📥 Export Markdown
                  </button>
                </div>
              </div>
              <div className="alert alert-info">
                ℹ️ <strong>Evidence-based:</strong> All content is derived from the analyzed papers. References are listed below.
              </div>
              <div className="lr-markdown card">
                <ReactMarkdown>{review.full_text}</ReactMarkdown>
              </div>
              {review.references?.length > 0 && (
                <div className="card lr-refs">
                  <h3 className="section-title">📚 References</h3>
                  {review.references.map((ref, i) => (
                    <div key={i} className="lr-ref">
                      [{i + 1}] {ref.title}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
