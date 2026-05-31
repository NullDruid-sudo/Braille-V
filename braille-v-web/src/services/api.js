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
 * @returns {Promise<{status: string, message: string}>}
 */
export async function checkHealth() {
  const { data } = await api.get('/health');
  return data;
}

/**
 * Send a captured image to the backend for Braille scanning.
 * @param {Blob} imageBlob - The image to scan (from canvas.toBlob).
 * @returns {Promise<Object>} Scan result with unicode_braille, english_text, etc.
 */
export async function scanImage(imageBlob) {
  const formData = new FormData();
  formData.append('image', imageBlob, 'capture.png');

  const { data } = await api.post('/scan', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export default api;
