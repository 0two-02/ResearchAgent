import React, { useState } from 'react';
import { getRecommendations } from '../services/api';
import './ResearchIdeasPage.css';

const DIFFICULTY_COLORS = { low: 'badge-green', medium: 'badge-yellow', high: 'badge-red' };

export default function ResearchIdeasPage() {
  const [paperIds, setPaperIds] = useState('');
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [ideas, setIdeas] = useState([]);
  const [error, setError] = useState('');

  const handleGenerate = async () => {
    setError('');
    const ids = paperIds
      .split(',')
      .map(s => parseInt(s.trim()))
      .filter(n => !isNaN(n));

    if (ids.length === 0) {
      setError('Enter at least one paper ID. Search papers in Workspace first.');
      return;
    }
    setLoading(true);
    try {
      const data = await getRecommendations({ paper_ids: ids, research_topic: topic });
      setIdeas(data.recommendations || []);
    } catch (err) {
      setError('Failed to generate ideas. Try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    const json = JSON.stringify(ideas, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'research-ideas.json';
    a.click();
  };

  return (
    <div className="container page">
      <div className="page-header">
        <h1 className="page-title">💡 Research Ideas & Recommendations</h1>
        <p className="page-subtitle">AI-powered future research direction suggestions grounded in evidence</p>
      </div>

      <div className="ideas-controls card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div style={{ flex: '1 1 200px' }}>
            <label style={{ fontSize: 12, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>Research Topic (optional)</label>
            <input className="input" placeholder="e.g., AI in healthcare" value={topic} onChange={e => setTopic(e.target.value)} />
          </div>
          <div style={{ flex: '1 1 200px' }}>
            <label style={{ fontSize: 12, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>Paper IDs</label>
            <input className="input" placeholder="e.g., 1, 2, 3" value={paperIds} onChange={e => setPaperIds(e.target.value)} />
          </div>
          <button className="btn btn-primary" onClick={handleGenerate} disabled={loading}>
            {loading ? '⏳ Generating...' : '💡 Generate Ideas'}
          </button>
          {ideas.length > 0 && (
            <button className="btn btn-secondary" onClick={handleExport}>📥 Export JSON</button>
          )}
        </div>
        {error && <div className="alert alert-error" style={{ marginTop: 12 }}>{error}</div>}
      </div>

      <div className="alert alert-info">
        🤖 <strong>AI Transparency:</strong> All research suggestions are grounded in evidence from the analyzed papers.
        Suggestions represent unexplored directions identified by AI analysis — not guaranteed discoveries.
      </div>

      {loading && (
        <div className="loading-overlay">
          <div className="spinner" />
          <p>🤖 Research Recommendation Agent generating ideas...</p>
        </div>
      )}

      {ideas.length > 0 && (
        <div className="ideas-grid">
          {ideas.map((idea, i) => (
            <div key={i} className="idea-card card">
              <div className="idea-header">
                <span className="idea-number">#{i + 1}</span>
                <span className={`badge ${DIFFICULTY_COLORS[idea.difficulty_level] || 'badge-yellow'}`}>
                  {idea.difficulty_level} difficulty
                </span>
              </div>
              <h3 className="idea-title">{idea.research_idea}</h3>
              <div className="idea-fields">
                {[
                  ['💡 Why It Matters', idea.why_it_matters],
                  ['📊 Existing Evidence', idea.existing_evidence],
                  ['🔭 Research Gap', idea.research_gap],
                  ['🔬 Suggested Methodology', idea.suggested_methodology],
                  ['💾 Possible Dataset', idea.possible_dataset],
                  ['🎯 Expected Contribution', idea.expected_contribution],
                ].map(([label, val]) => val && (
                  <div key={label} className="idea-field">
                    <strong className="idea-field-label">{label}</strong>
                    <p className="idea-field-value">{val}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && ideas.length === 0 && (
        <div className="ideas-empty card">
          <div style={{ fontSize: 48 }}>💡</div>
          <h3>No Research Ideas Yet</h3>
          <p>Enter paper IDs from your Workspace and click Generate Ideas.<br />
          The AI Recommendation Agent will analyze gaps and suggest future directions.</p>
        </div>
      )}
    </div>
  );
}
