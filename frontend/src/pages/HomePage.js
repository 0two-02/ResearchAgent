import React from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

const IMPACT_BEFORE = [
  '🔍 Search dozens of websites manually',
  '📥 Download papers one by one',
  '📖 Read every paper manually',
  '📊 Compare papers in a spreadsheet',
  '🤔 Guess at research gaps',
  '❓ Speculate about future directions',
];

const IMPACT_AFTER = [
  '💡 One research question',
  '🤖 8 AI agents activate',
  '🌐 Academic APIs searched in parallel',
  '📄 Evidence extracted automatically',
  '📝 Literature synthesized instantly',
  '🔭 Gaps & trends identified by AI',
  '🚀 Future directions generated',
];

const FEATURES = [
  { icon: '🔍', title: 'Intelligent Search', desc: 'Multi-source academic search across arXiv, Semantic Scholar, OpenAlex, CrossRef' },
  { icon: '🤖', title: '8 AI Agents', desc: 'Planner, Discovery, Analysis, Literature Review, Gap Detection, Trends, Citations, Recommendations' },
  { icon: '📄', title: 'PDF & Doc Processing', desc: 'Upload PDFs, notes, CSVs. AI extracts, chunks, and indexes for semantic search' },
  { icon: '🧠', title: 'IBM watsonx.ai', desc: 'Powered by IBM foundation models for reliable, evidence-grounded research analysis' },
  { icon: '📊', title: 'Research Dashboard', desc: 'Interactive topic clusters, publication trends, citation networks, knowledge graphs' },
  { icon: '🔭', title: 'Research Gaps', desc: 'AI identifies understudied areas, contradictions, and missing methodologies' },
  { icon: '📈', title: 'Trend Analysis', desc: 'AI-assisted trend forecasting from publication patterns and keyword evolution' },
  { icon: '💬', title: 'Research Chat', desc: 'Ask questions about papers. Get grounded, cited answers from your research library' },
];

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="home-page">
      {/* Hero */}
      <section className="hero">
        <div className="hero-badge">🔬 Powered by IBM watsonx.ai</div>
        <h1 className="hero-title">
          ResearchPilot AI
        </h1>
        <p className="hero-tagline">From scattered research to actionable knowledge.</p>
        <p className="hero-description">
          An intelligent research companion that uses agentic AI to search, analyze, synthesize, and
          visualize academic research — transforming hundreds of papers into clear insights.
        </p>
        <div className="hero-actions">
          <button className="btn btn-primary hero-btn" onClick={() => navigate('/workspace')}>
            🚀 Start Research
          </button>
          <button className="btn btn-secondary hero-btn" onClick={() => navigate('/upload')}>
            📄 Upload Papers
          </button>
          <button className="btn btn-ghost hero-btn" onClick={() => navigate('/dashboard')}>
            📊 Explore Dashboard
          </button>
        </div>
      </section>

      {/* Features */}
      <section className="home-section container">
        <h2 className="home-section-title">What ResearchPilot Does</h2>
        <div className="features-grid">
          {FEATURES.map((f) => (
            <div key={f.title} className="feature-card card">
              <div className="feature-icon">{f.icon}</div>
              <h3 className="feature-title">{f.title}</h3>
              <p className="feature-desc">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Research Impact */}
      <section className="home-section container impact-section">
        <h2 className="home-section-title">Research Impact</h2>
        <div className="impact-grid">
          <div className="impact-col card">
            <h3 className="impact-col-title before">❌ Before ResearchPilot</h3>
            <ul className="impact-list">
              {IMPACT_BEFORE.map((item) => (
                <li key={item} className="impact-item impact-before">{item}</li>
              ))}
            </ul>
          </div>
          <div className="impact-arrow">→</div>
          <div className="impact-col card">
            <h3 className="impact-col-title after">✅ With ResearchPilot</h3>
            <ul className="impact-list">
              {IMPACT_AFTER.map((item) => (
                <li key={item} className="impact-item impact-after">{item}</li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* IBM Agent Workflow */}
      <section className="home-section container">
        <h2 className="home-section-title">Agentic AI Workflow</h2>
        <div className="workflow-flow card">
          <div className="workflow-steps">
            {[
              { label: 'User Query', icon: '💬' },
              { label: 'Research Planner Agent', icon: '🧠', ibm: true },
              { label: 'Discovery Agent', icon: '🔍', ibm: true },
              { label: 'Academic APIs', icon: '🌐' },
              { label: 'Dedup & Rank', icon: '⚙️' },
              { label: 'Paper Analysis Agent', icon: '📄', ibm: true },
              { label: 'Literature Review Agent', icon: '📝', ibm: true },
              { label: 'Gap Detection Agent', icon: '🔭', ibm: true },
              { label: 'Trend Agent', icon: '📈', ibm: true },
              { label: 'Recommendation Agent', icon: '💡', ibm: true },
              { label: 'Dashboard & Chat', icon: '📊' },
            ].map((step, i, arr) => (
              <React.Fragment key={step.label}>
                <div className={`workflow-step ${step.ibm ? 'ibm-step' : ''}`}>
                  <span className="workflow-icon">{step.icon}</span>
                  <span className="workflow-label">{step.label}</span>
                  {step.ibm && <span className="badge badge-blue" style={{ fontSize: '9px' }}>IBM</span>}
                </div>
                {i < arr.length - 1 && <span className="workflow-arrow">↓</span>}
              </React.Fragment>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="home-footer">
        <p>ResearchPilot AI · Built with IBM watsonx.ai · <a href="http://localhost:8000/api/docs" target="_blank" rel="noreferrer">API Docs</a></p>
      </footer>
    </div>
  );
}
