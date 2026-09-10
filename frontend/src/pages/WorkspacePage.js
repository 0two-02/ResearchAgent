import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchResearch, analyzePapers, identifyGaps, getRecommendations } from '../services/api';
import PaperCard from '../components/PaperCard';
import ChatPanel from '../components/ChatPanel';
import ResearchSummary from '../components/ResearchSummary';
import './WorkspacePage.css';

const SOURCES = [
  { id: 'arxiv', label: 'arXiv' },
  { id: 'semantic_scholar', label: 'Semantic Scholar' },
  { id: 'openalex', label: 'OpenAlex' },
  { id: 'crossref', label: 'CrossRef' },
];

export default function WorkspacePage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [selectedSources, setSelectedSources] = useState(['arxiv', 'semantic_scholar', 'openalex']);
  const [maxResults, setMaxResults] = useState(20);
  const [yearFrom, setYearFrom] = useState('');
  const [yearTo, setYearTo] = useState('');
  const [demoMode, setDemoMode] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);
  const [selectedPapers, setSelectedPapers] = useState([]);
  const [activeTab, setActiveTab] = useState('results');

  const [gapsLoading, setGapsLoading] = useState(false);
  const [gaps, setGaps] = useState(null);

  const [recsLoading, setRecsLoading] = useState(false);
  const [recs, setRecs] = useState(null);

  const toggleSource = (id) => {
    setSelectedSources((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );
  };

  const togglePaperSelect = (paperId) => {
    setSelectedPapers((prev) =>
      prev.includes(paperId) ? prev.filter((id) => id !== paperId) : [...prev, paperId]
    );
  };

  const handleSearch = async () => {
    if (!query.trim()) { setError('Please enter a research question.'); return; }
    if (selectedSources.length === 0) { setError('Select at least one source.'); return; }
    setError('');
    setLoading(true);
    setResults(null);
    setSelectedPapers([]);
    setGaps(null);
    setRecs(null);

    try {
      const data = await searchResearch({
        query: query.trim(),
        sources: selectedSources,
        max_results: maxResults,
        year_from: yearFrom ? parseInt(yearFrom) : null,
        year_to: yearTo ? parseInt(yearTo) : null,
        demo_mode: demoMode,
      });
      setResults(data);
      setActiveTab('results');
    } catch (err) {
      setError(err.response?.data?.detail || 'Search failed. Check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (selectedPapers.length === 0) { setError('Select papers to analyze.'); return; }
    setError('');
    setLoading(true);
    try {
      await analyzePapers(selectedPapers);
      setActiveTab('analysis');
    } catch (err) {
      setError('Analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleGaps = async () => {
    const paperIds = selectedPapers.length > 0 ? selectedPapers : (results?.papers?.map(p => p.id) || []);
    if (paperIds.length === 0) { setError('No papers to analyze.'); return; }
    setGapsLoading(true);
    try {
      const data = await identifyGaps({ paper_ids: paperIds, query_id: results?.query_id });
      setGaps(data);
      setActiveTab('gaps');
    } catch (err) {
      setError('Gap analysis failed.');
    } finally {
      setGapsLoading(false);
    }
  };

  const handleRecs = async () => {
    const paperIds = selectedPapers.length > 0 ? selectedPapers : (results?.papers?.map(p => p.id) || []);
    if (paperIds.length === 0) { setError('No papers for recommendations.'); return; }
    setRecsLoading(true);
    try {
      const data = await getRecommendations({ paper_ids: paperIds, research_topic: query });
      setRecs(data);
      setActiveTab('recs');
    } catch (err) {
      setError('Recommendations failed.');
    } finally {
      setRecsLoading(false);
    }
  };

  const handleCompare = () => {
    if (selectedPapers.length < 2) { setError('Select at least 2 papers to compare.'); return; }
    navigate(`/compare?papers=${selectedPapers.join(',')}`);
  };

  const TABS = [
    { id: 'results', label: `Papers${results ? ` (${results.papers.length})` : ''}` },
    { id: 'summary', label: 'AI Summary' },
    { id: 'gaps', label: 'Research Gaps' },
    { id: 'recs', label: 'Recommendations' },
  ];

  return (
    <div className="workspace-layout">
      {/* Left Sidebar */}
      <aside className="workspace-sidebar">
        <div className="sidebar-section">
          <h3 className="section-title">🔍 Research Question</h3>
          <textarea
            className="textarea"
            placeholder="e.g., Applications of AI in early disease detection..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={4}
            onKeyDown={(e) => { if (e.key === 'Enter' && e.ctrlKey) handleSearch(); }}
          />
          <button
            className="btn btn-primary"
            style={{ width: '100%', marginTop: 10 }}
            onClick={handleSearch}
            disabled={loading}
          >
            {loading ? '⏳ Searching...' : '🚀 Start Research'}
          </button>
        </div>

        <div className="sidebar-section">
          <h3 className="section-title">📚 Academic Sources</h3>
          <div className="source-checkboxes">
            {SOURCES.map((s) => (
              <label key={s.id} className="source-check">
                <input
                  type="checkbox"
                  checked={selectedSources.includes(s.id)}
                  onChange={() => toggleSource(s.id)}
                />
                {s.label}
              </label>
            ))}
          </div>
        </div>

        <div className="sidebar-section">
          <h3 className="section-title">⚙️ Filters</h3>
          <div className="filter-row">
            <label>Max Results</label>
            <input className="input" type="number" min={5} max={100} value={maxResults} onChange={(e) => setMaxResults(parseInt(e.target.value))} />
          </div>
          <div className="filter-row">
            <label>Year From</label>
            <input className="input" type="number" min={1990} max={2024} placeholder="e.g. 2018" value={yearFrom} onChange={(e) => setYearFrom(e.target.value)} />
          </div>
          <div className="filter-row">
            <label>Year To</label>
            <input className="input" type="number" min={1990} max={2024} placeholder="e.g. 2024" value={yearTo} onChange={(e) => setYearTo(e.target.value)} />
          </div>
          <label className="source-check">
            <input type="checkbox" checked={demoMode} onChange={(e) => setDemoMode(e.target.checked)} />
            Demo Mode
          </label>
        </div>

        {results && (
          <div className="sidebar-section">
            <h3 className="section-title">🛠 Actions</h3>
            <div className="action-btns">
              <button className="btn btn-secondary btn-sm" onClick={handleAnalyze} disabled={loading || selectedPapers.length === 0}>
                🔬 Analyze Selected ({selectedPapers.length})
              </button>
              <button className="btn btn-secondary btn-sm" onClick={handleGaps} disabled={gapsLoading}>
                {gapsLoading ? '⏳ Finding Gaps...' : '🔭 Find Research Gaps'}
              </button>
              <button className="btn btn-secondary btn-sm" onClick={handleRecs} disabled={recsLoading}>
                {recsLoading ? '⏳ Generating...' : '💡 Get Recommendations'}
              </button>
              <button className="btn btn-ghost btn-sm" onClick={handleCompare} disabled={selectedPapers.length < 2}>
                📊 Compare ({selectedPapers.length})
              </button>
              <button className="btn btn-ghost btn-sm" onClick={() => navigate('/literature-review')}>
                📝 Literature Review
              </button>
            </div>
          </div>
        )}
      </aside>

      {/* Center Panel */}
      <main className="workspace-main">
        {error && <div className="alert alert-error">{error}</div>}

        {!loading && !results && (
          <div className="workspace-empty">
            <div style={{ fontSize: 64 }}>🔬</div>
            <h2>Start Your Research</h2>
            <p>Enter a research question and click Start Research.<br />Our AI agents will search academic sources and analyze the results.</p>
          </div>
        )}

        {loading && (
          <div className="loading-overlay">
            <div className="spinner" />
            <p>🤖 AI agents are searching academic sources...</p>
            <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>Research Planner → Discovery → Ranking</p>
          </div>
        )}

        {results && (
          <>
            {results.demo_mode && (
              <div className="demo-banner">
                ⚠️ Demo Data — This is sample research data, not live API results.
              </div>
            )}

            <div className="results-header">
              <div>
                <strong>{results.total_found}</strong> papers found for "{results.query}"
                <span style={{ marginLeft: 10 }}>
                  {results.sources_searched.map(s => (
                    <span key={s} className="badge badge-blue" style={{ marginLeft: 4 }}>{s}</span>
                  ))}
                </span>
              </div>
              {selectedPapers.length > 0 && (
                <span className="badge badge-purple">{selectedPapers.length} selected</span>
              )}
            </div>

            <div className="tabs">
              {TABS.map((t) => (
                <button key={t.id} className={`tab ${activeTab === t.id ? 'active' : ''}`} onClick={() => setActiveTab(t.id)}>
                  {t.label}
                </button>
              ))}
            </div>

            {activeTab === 'results' && (
              <div className="paper-list">
                {results.papers.map((paper, i) => (
                  <PaperCard
                    key={paper.id}
                    paper={paper}
                    rank={i + 1}
                    isSelected={selectedPapers.includes(paper.id)}
                    onToggleSelect={togglePaperSelect}
                  />
                ))}
              </div>
            )}

            {activeTab === 'summary' && (
              <ResearchSummary summary={results.summary} plan={results.research_plan} />
            )}

            {activeTab === 'gaps' && gaps && (
              <div className="gaps-panel">
                <h3 className="section-title">🔭 Research Gaps Identified</h3>
                {(gaps.research_gaps || []).map((gap, i) => (
                  <div key={i} className="gap-card card">
                    <div className="gap-header">
                      <strong className="gap-text">{gap}</strong>
                      <span className={`badge badge-${(gaps.importance?.[i] || 'medium') === 'high' ? 'red' : (gaps.importance?.[i] || 'medium') === 'low' ? 'green' : 'yellow'}`}>
                        {gaps.importance?.[i] || 'medium'}
                      </span>
                    </div>
                    {gaps.evidence?.[i] && (
                      <p className="gap-evidence"><strong>Evidence:</strong> {gaps.evidence[i]}</p>
                    )}
                    {gaps.possible_research_questions?.[i] && (
                      <p className="gap-question"><strong>Research Question:</strong> {gaps.possible_research_questions[i]}</p>
                    )}
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'recs' && recs && (
              <div className="recs-panel">
                <h3 className="section-title">💡 Research Recommendations</h3>
                {(recs.recommendations || []).map((rec, i) => (
                  <div key={i} className="rec-card card">
                    <h4 className="rec-title">{rec.research_idea}</h4>
                    <div className="rec-grid">
                      {[
                        ['Why It Matters', rec.why_it_matters],
                        ['Existing Evidence', rec.existing_evidence],
                        ['Research Gap', rec.research_gap],
                        ['Suggested Methodology', rec.suggested_methodology],
                        ['Possible Dataset', rec.possible_dataset],
                        ['Expected Contribution', rec.expected_contribution],
                      ].map(([label, val]) => val && (
                        <div key={label} className="rec-field">
                          <strong>{label}:</strong> {val}
                        </div>
                      ))}
                    </div>
                    <span className={`badge badge-${rec.difficulty_level === 'high' ? 'red' : rec.difficulty_level === 'low' ? 'green' : 'yellow'}`}>
                      {rec.difficulty_level} difficulty
                    </span>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </main>

      {/* Right Panel: Chat */}
      <aside className="workspace-chat">
        <ChatPanel paperIds={results?.papers?.map(p => p.id) || []} queryId={results?.query_id} />
      </aside>
    </div>
  );
}
