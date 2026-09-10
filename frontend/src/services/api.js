import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
});

// ── Research ────────────────────────────────────────────────────────────────

export const searchResearch = (data) =>
  api.post('/research/search', data).then((r) => r.data);

export const analyzePapers = (paperIds) =>
  api.post('/research/analyze', { paper_ids: paperIds }).then((r) => r.data);

export const generateLiteratureReview = (data) =>
  api.post('/research/literature-review', data).then((r) => r.data);

export const identifyGaps = (data) =>
  api.post('/research/gaps', data).then((r) => r.data);

export const analyzeTrends = (data) =>
  api.post('/research/trends', data).then((r) => r.data);

export const getRecommendations = (data) =>
  api.post('/research/recommendations', data).then((r) => r.data);

export const comparePapers = (paperIds) =>
  api.post('/research/compare', { paper_ids: paperIds }).then((r) => r.data);

export const getCitationAnalysis = (paperIds) =>
  api.post('/research/citations', { paper_ids: paperIds }).then((r) => r.data);

// ── Papers ───────────────────────────────────────────────────────────────────

export const getPapers = (params) =>
  api.get('/papers', { params }).then((r) => r.data);

export const getPaper = (id) =>
  api.get(`/papers/${id}`).then((r) => r.data);

// ── Documents ─────────────────────────────────────────────────────────────────

export const uploadDocument = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then((r) => r.data);
};

export const analyzeDocument = (documentId) =>
  api.post('/documents/analyze', null, { params: { document_id: documentId } }).then((r) => r.data);

export const getDocuments = () =>
  api.get('/documents').then((r) => r.data);

// ── Chat ──────────────────────────────────────────────────────────────────────

export const sendChatMessage = (data) =>
  api.post('/chat', data).then((r) => r.data);

// ── Dashboard ─────────────────────────────────────────────────────────────────

export const getDashboard = () =>
  api.get('/dashboard').then((r) => r.data);

export const getHealth = () =>
  api.get('/health').then((r) => r.data);

export const getInfo = () =>
  api.get('/info').then((r) => r.data);

export default api;
