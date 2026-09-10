import React, { useState, useEffect } from 'react';
import { getDashboard } from '../services/api';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend
} from 'recharts';
import './DashboardPage.css';

const COLORS = ['#4f8ef7', '#7c5cd8', '#22c55e', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899'];

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    getDashboard()
      .then(setData)
      .catch(() => setError('Failed to load dashboard. Make sure backend is running.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-overlay"><div className="spinner" /><p>Loading dashboard...</p></div>;
  if (error) return <div className="container page"><div className="alert alert-error">{error}</div></div>;
  if (!data) return null;

  const yearlyData = Object.entries(data.yearly_distribution || {})
    .map(([year, count]) => ({ year, count }))
    .sort((a, b) => a.year.localeCompare(b.year));

  const keywordData = Object.entries(data.top_keywords || {})
    .map(([kw, count]) => ({ name: kw, value: count }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 12);

  const topicData = (data.topic_clusters || []).slice(0, 8);

  const STATS = [
    { label: 'Papers Analyzed', value: data.total_papers, icon: '📄', color: '#4f8ef7' },
    { label: 'Research Topics', value: data.total_topics, icon: '🏷️', color: '#7c5cd8' },
    { label: 'Research Queries', value: data.total_queries, icon: '🔍', color: '#22c55e' },
    { label: 'Research Gaps Found', value: data.total_gaps, icon: '🔭', color: '#f59e0b' },
  ];

  const TABS = ['overview', 'trends', 'keywords', 'topics'];

  return (
    <div className="container page">
      <div className="page-header">
        <h1 className="page-title">📊 Research Dashboard</h1>
        <p className="page-subtitle">Insights and analytics from your research library</p>
      </div>

      {/* Stats Row */}
      <div className="stats-grid">
        {STATS.map((s) => (
          <div key={s.label} className="stat-card card">
            <div className="stat-icon" style={{ color: s.color }}>{s.icon}</div>
            <div className="stat-value" style={{ color: s.color }}>{s.value}</div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Highlights */}
      <div className="highlights-row">
        {data.most_cited_paper && (
          <div className="highlight-card card">
            <span className="highlight-label">🏆 Most Cited Paper</span>
            <span className="highlight-value">{data.most_cited_paper}</span>
          </div>
        )}
        {data.most_active_area && (
          <div className="highlight-card card">
            <span className="highlight-label">🔥 Most Active Area</span>
            <span className="highlight-value">{data.most_active_area}</span>
          </div>
        )}
        {data.emerging_topic && (
          <div className="highlight-card card">
            <span className="highlight-label">🌱 Emerging Topic</span>
            <span className="highlight-value">{data.emerging_topic}</span>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="tabs">
        {TABS.map(t => (
          <button key={t} className={`tab ${activeTab === t ? 'active' : ''}`} onClick={() => setActiveTab(t)}>
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && (
        <div className="dashboard-grid">
          {/* Publication Trend */}
          <div className="chart-card card">
            <h3 className="section-title">📈 Publication Trend</h3>
            {yearlyData.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={yearlyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis dataKey="year" stroke="var(--text-muted)" tick={{ fontSize: 11 }} />
                  <YAxis stroke="var(--text-muted)" tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 8 }} />
                  <Line type="monotone" dataKey="count" stroke="#4f8ef7" strokeWidth={2} dot={{ fill: '#4f8ef7', r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : <div className="empty-chart">No publication data yet. Start a research search.</div>}
          </div>

          {/* Top Keywords Pie */}
          <div className="chart-card card">
            <h3 className="section-title">🏷️ Top Keywords</h3>
            {keywordData.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={keywordData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name }) => name}>
                    {keywordData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 8 }} />
                </PieChart>
              </ResponsiveContainer>
            ) : <div className="empty-chart">No keyword data yet.</div>}
          </div>
        </div>
      )}

      {activeTab === 'trends' && (
        <div className="card">
          <h3 className="section-title">📈 Publication Trend by Year</h3>
          {yearlyData.length > 0 ? (
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={yearlyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="year" stroke="var(--text-muted)" tick={{ fontSize: 11 }} />
                <YAxis stroke="var(--text-muted)" tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 8 }} />
                <Bar dataKey="count" fill="#4f8ef7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <div className="empty-chart">No trend data. Search some papers first.</div>}
        </div>
      )}

      {activeTab === 'keywords' && (
        <div className="card">
          <h3 className="section-title">🔤 Keyword Frequency</h3>
          {keywordData.length > 0 ? (
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={keywordData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis type="number" stroke="var(--text-muted)" tick={{ fontSize: 11 }} />
                <YAxis type="category" dataKey="name" stroke="var(--text-muted)" tick={{ fontSize: 11 }} width={120} />
                <Tooltip contentStyle={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 8 }} />
                <Bar dataKey="value" fill="#7c5cd8" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <div className="empty-chart">No keyword data yet.</div>}
        </div>
      )}

      {activeTab === 'topics' && (
        <div>
          <h3 className="section-title">🗂 Topic Clusters</h3>
          {topicData.length > 0 ? (
            <div className="topic-cluster-grid">
              {topicData.map((t, i) => (
                <div key={t.name} className="topic-cluster card">
                  <div className="topic-icon" style={{ color: COLORS[i % COLORS.length] }}>📁</div>
                  <div className="topic-name">{t.name}</div>
                  <div className="topic-count">{t.paper_count} papers</div>
                  <div className="topic-bar">
                    <div
                      className="topic-bar-fill"
                      style={{
                        width: `${Math.min((t.paper_count / (topicData[0]?.paper_count || 1)) * 100, 100)}%`,
                        background: COLORS[i % COLORS.length],
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : <div className="empty-chart">No topic data. Search papers to populate topics.</div>}
        </div>
      )}
    </div>
  );
}
