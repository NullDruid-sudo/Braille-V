/**
 * Braille-V API Service
 * Communicates with the FastAPI backend.
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

/**
 * Check if the backend is running.
 */
export async function checkHealth() {
  const { data } = await api.get('/health');
  return data;
}

/**
 * Send a captured image to the backend for Braille scanning.
 * @param {Blob} imageBlob
 * @returns {Promise<Object>} { success, id, unicode_braille, english_text, ... }
 */
export async function scanImage(imageBlob) {
  const formData = new FormData();
  formData.append('image', imageBlob, 'capture.png');
  const { data } = await api.post('/scan', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

// ── History API ──────────────────────────────────────────────────────────────

/**
 * Fetch scan history (newest first, max 50).
 * @returns {Promise<{ scans: Array, count: number }>}
 */
export async function getHistory() {
  const { data } = await api.get('/history');
  return data;
}

/**
 * Delete a single scan from history by its SQLite row ID.
 * @param {number} id
 */
export async function deleteHistoryItem(id) {
  const { data } = await api.delete(`/history/${id}`);
  return data;
}

/**
 * Delete all history entries.
 */
export async function clearAllHistory() {
  const { data } = await api.delete('/history');
  return data;
}

export default api;

