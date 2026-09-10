import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, NavLink, useNavigate } from 'react-router-dom';
import HomePage from './pages/HomePage';
import WorkspacePage from './pages/WorkspacePage';
import DashboardPage from './pages/DashboardPage';
import LiteratureReviewPage from './pages/LiteratureReviewPage';
import ResearchIdeasPage from './pages/ResearchIdeasPage';
import UploadPage from './pages/UploadPage';
import PaperDetailPage from './pages/PaperDetailPage';
import ComparePage from './pages/ComparePage';
import { getInfo } from './services/api';
import './App.css';

function Navbar({ ibmConnected, demoMode }) {
  return (
    <nav className="navbar">
      <div className="navbar-inner container">
        <NavLink to="/" className="navbar-brand">
          <span className="brand-icon">🔬</span>
          <span className="brand-name">ResearchPilot AI</span>
        </NavLink>
        <div className="navbar-links">
          <NavLink to="/workspace" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Workspace</NavLink>
          <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Dashboard</NavLink>
          <NavLink to="/literature-review" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Literature Review</NavLink>
          <NavLink to="/research-ideas" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Research Ideas</NavLink>
          <NavLink to="/upload" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Upload</NavLink>
        </div>
        <div className="navbar-status">
          {demoMode && <span className="badge badge-orange">Demo Mode</span>}
          <span className={`ibm-status ${ibmConnected ? 'connected' : 'demo'}`}>
            {ibmConnected
              ? `● ${(window._llmProvider === 'groq' ? 'Groq' : window._llmProvider === 'ibm_watsonx' ? 'IBM watsonx' : 'LLM')} Active`
              : '● Demo Mode'}
          </span>
        </div>
      </div>
    </nav>
  );
}

function App() {
  const [ibmConnected, setIbmConnected] = useState(false);
  const [demoMode, setDemoMode] = useState(false);

  useEffect(() => {
    getInfo()
      .then((info) => {
        setIbmConnected(info.ibm_connected || info.groq_connected);
        setDemoMode(info.demo_mode);
        // store provider label for the status badge
        window._llmProvider = info.llm_provider || 'demo';
      })
      .catch(() => {});
  }, []);

  return (
    <BrowserRouter>
      <Navbar ibmConnected={ibmConnected} demoMode={demoMode} />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/workspace" element={<WorkspacePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/literature-review" element={<LiteratureReviewPage />} />
          <Route path="/research-ideas" element={<ResearchIdeasPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/papers/:id" element={<PaperDetailPage />} />
          <Route path="/compare" element={<ComparePage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;
