import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './PaperCard.css';

export default function PaperCard({ paper, rank, isSelected, onToggleSelect }) {
  const navigate = useNavigate();
  const [expanded, setExpanded] = useState(false);

  const abstractPreview = paper.abstract
    ? (paper.abstract.length > 200 ? paper.abstract.slice(0, 200) + '…' : paper.abstract)
    : 'No abstract available.';

  const SOURCE_COLORS = {
    arxiv: 'badge-blue',
    semantic_scholar: 'badge-purple',
    openalex: 'badge-green',
    crossref: 'badge-yellow',
    demo: 'badge-orange',
  };

  return (
    <div className={`paper-card card ${isSelected ? 'selected' : ''}`}>
      <div className="paper-card-top">
        <div className="paper-rank">#{rank}</div>
        <div className="paper-main">
          <div className="paper-header">
            <h3
              className="paper-title"
              onClick={() => navigate(`/papers/${paper.id}`)}
            >
              {paper.title}
            </h3>
            <div className="paper-actions">
              {onToggleSelect && (
                <button
                  className={`btn btn-sm ${isSelected ? 'btn-primary' : 'btn-ghost'}`}
                  onClick={() => onToggleSelect(paper.id)}
                >
                  {isSelected ? '✓ Selected' : 'Select'}
                </button>
              )}
            </div>
          </div>

          <div className="paper-meta">
            {paper.authors?.length > 0 && (
              <span className="paper-authors">
                {paper.authors.slice(0, 3).map(a => a.name || a).join(', ')}
                {paper.authors.length > 3 && ` +${paper.authors.length - 3}`}
              </span>
            )}
            {paper.year && <span className="paper-year">{paper.year}</span>}
            {paper.journal && <span className="paper-journal">{paper.journal}</span>}
          </div>

          <div className="paper-badges">
            {paper.source && (
              <span className={`badge ${SOURCE_COLORS[paper.source] || 'badge-blue'}`}>
                {paper.source.replace('_', ' ')}
              </span>
            )}
            {paper.is_demo && <span className="badge badge-orange">Demo</span>}
            {paper.citation_count > 0 && (
              <span className="badge badge-yellow">🏆 {paper.citation_count.toLocaleString()} citations</span>
            )}
            {paper.research_field && (
              <span className="badge badge-purple">{paper.research_field}</span>
            )}
          </div>

          <p className="paper-abstract">
            {expanded ? paper.abstract : abstractPreview}
          </p>

          {paper.abstract && paper.abstract.length > 200 && (
            <button className="expand-btn" onClick={() => setExpanded(!expanded)}>
              {expanded ? 'Show less' : 'Read more'}
            </button>
          )}

          {paper.keywords?.length > 0 && (
            <div className="tags" style={{ marginTop: 8 }}>
              {paper.keywords.slice(0, 5).map((kw) => (
                <span key={kw} className="tag">{kw}</span>
              ))}
            </div>
          )}

          <div className="paper-links">
            {paper.url && <a href={paper.url} target="_blank" rel="noreferrer" className="paper-link">🔗 View Paper</a>}
            {paper.pdf_url && <a href={paper.pdf_url} target="_blank" rel="noreferrer" className="paper-link">📄 PDF</a>}
            {paper.doi && <span className="paper-doi">DOI: {paper.doi}</span>}
          </div>
        </div>
      </div>
    </div>
  );
}
