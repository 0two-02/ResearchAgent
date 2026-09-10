import React, { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '../services/api';
import './ChatPanel.css';

const SUGGESTIONS = [
  'Summarize these papers',
  'What are the major research gaps?',
  'Which paper has the best methodology?',
  'What datasets are commonly used?',
  'What methods are becoming popular?',
  'Suggest 5 research topics',
  'Compare the methodologies',
  'Explain the key findings simply',
];

export default function ChatPanel({ paperIds = [], queryId = null }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '👋 Hi! I\'m your AI research assistant. Ask me anything about the papers in your workspace. I\'ll provide evidence-based answers with source references.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (text) => {
    const msg = text || input.trim();
    if (!msg || loading) return;

    const userMsg = { role: 'user', content: msg };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const history = messages.slice(-6).map(m => ({ role: m.role, content: m.content }));
      const response = await sendChatMessage({
        message: msg,
        paper_ids: paperIds,
        query_id: queryId,
        history,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.response,
          sources: response.sources,
          evidence: response.evidence,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: '❌ Sorry, I encountered an error. Please try again.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <span>💬 Research Assistant</span>
        {paperIds.length > 0 && (
          <span className="badge badge-blue">{paperIds.length} papers</span>
        )}
      </div>

      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`chat-message ${msg.role}`}>
            <div className="message-bubble">
              <p className="message-content">{msg.content}</p>
              {msg.sources?.length > 0 && (
                <div className="message-sources">
                  <strong>Sources:</strong>{' '}
                  {msg.sources.map((s, j) => (
                    <span key={j} className="source-tag">{s.title || s.doc_id || `Source ${j+1}`}</span>
                  ))}
                </div>
              )}
              {msg.evidence && (
                <div className="message-evidence">{msg.evidence}</div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="chat-message assistant">
            <div className="message-bubble typing">
              <span /><span /><span />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-suggestions">
        {SUGGESTIONS.slice(0, 4).map((s) => (
          <button key={s} className="suggestion-chip" onClick={() => sendMessage(s)}>
            {s}
          </button>
        ))}
      </div>

      <div className="chat-input-row">
        <input
          className="input chat-input"
          placeholder="Ask about your research..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
          disabled={loading}
        />
        <button className="btn btn-primary chat-send" onClick={() => sendMessage()} disabled={loading || !input.trim()}>
          ➤
        </button>
      </div>
    </div>
  );
}
