/**
 * History — List of saved scans from SQLite via backend API.
 */

import React, { useEffect, useState, useCallback } from 'react';
import { ArrowLeft, Volume2, Trash2, Clock, AlertCircle, ScanLine, Loader2 } from 'lucide-react';
import { getHistory, deleteHistoryItem, clearAllHistory } from '../services/api';
import tts from '../services/tts';

/** Format a Unix timestamp → "May 31, 7:45 PM" */
function formatTime(ts) {
  return new Date(ts * 1000).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
}

export default function History({ onBack, onScanAgain }) {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleting, setDeleting] = useState(null); // id being deleted
  const [clearing, setClearing] = useState(false);

  const loadHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getHistory();
      setScans(data.scans || []);
    } catch {
      setError('Could not load history. Is the backend running?');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHistory();
    tts.speak('History. Your recent scans are listed below.');
  }, [loadHistory]);

  const handleReplay = (scan) => {
    if (scan.english_text) {
      tts.speak(scan.english_text);
    }
    if (navigator.vibrate) navigator.vibrate(10);
  };

  const handleDelete = async (id) => {
    setDeleting(id);
    try {
      await deleteHistoryItem(id);
      setScans((prev) => prev.filter((s) => s.id !== id));
      if (navigator.vibrate) navigator.vibrate(30);
    } catch {
      // Silently ignore
    } finally {
      setDeleting(null);
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm('Delete all scan history? This cannot be undone.')) return;
    setClearing(true);
    try {
      await clearAllHistory();
      setScans([]);
      tts.speak('History cleared.');
    } catch {
      // Silently ignore
    } finally {
      setClearing(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col px-4 py-6">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <button
          id="history-back-button"
          onClick={onBack}
          className="flex items-center justify-center w-10 h-10 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-600 transition-colors"
          aria-label="Go back to home"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h1 className="text-xl font-bold text-gray-900">Scan History</h1>

        {scans.length > 0 && (
          <button
            id="clear-history-button"
            onClick={handleClearAll}
            disabled={clearing}
            className="ml-auto flex items-center gap-1.5 px-3 py-1.5 text-sm text-red-500 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
            aria-label="Clear all history"
          >
            {clearing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Trash2 className="w-3.5 h-3.5" />}
            Clear all
          </button>
        )}
      </div>

      {/* Content */}
      <div className="max-w-lg mx-auto w-full flex-1">
        {/* Loading */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20 text-gray-400">
            <Loader2 className="w-8 h-8 animate-spin mb-3" />
            <p className="text-sm">Loading history…</p>
          </div>
        )}

        {/* Error */}
        {error && !loading && (
          <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* Empty state */}
        {!loading && !error && scans.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-gray-100 flex items-center justify-center mb-4">
              <Clock className="w-8 h-8 text-gray-300" />
            </div>
            <h2 className="text-lg font-semibold text-gray-700 mb-1">No scans yet</h2>
            <p className="text-sm text-gray-400 text-center max-w-xs mb-6">
              Your scan history will appear here after you scan Braille text.
            </p>
            <button
              id="history-scan-button"
              onClick={onScanAgain}
              className="flex items-center gap-2 px-6 py-3 bg-brand-500 text-white rounded-xl font-semibold hover:bg-brand-700 transition-all shadow-md shadow-brand-500/20 active:scale-[0.98]"
              aria-label="Start scanning"
            >
              <ScanLine className="w-5 h-5" />
              Start Scanning
            </button>
          </div>
        )}

        {/* Scan list */}
        {!loading && !error && scans.length > 0 && (
          <ul className="space-y-3 animate-fade-in" role="list" aria-label="Scan history">
            {scans.map((scan) => (
              <li
                key={scan.id}
                className="flex items-start gap-3 p-4 bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md hover:border-brand-200 transition-all duration-200"
              >
                {/* Text content */}
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-gray-900 text-base truncate">
                    {scan.english_text || '(empty)'}
                  </p>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-xs text-gray-400">{formatTime(scan.timestamp)}</span>
                    {scan.unicode_braille && (
                      <span className="text-xs text-gray-400 font-mono truncate max-w-[100px]">
                        {scan.unicode_braille}
                      </span>
                    )}
                    <span className="text-xs text-gray-300">
                      {scan.num_cells} cell{scan.num_cells !== 1 ? 's' : ''}
                    </span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-1 flex-shrink-0">
                  <button
                    onClick={() => handleReplay(scan)}
                    className="p-2 rounded-lg hover:bg-brand-50 text-gray-400 hover:text-brand-500 transition-colors"
                    aria-label={`Replay: ${scan.english_text}`}
                    title="Replay"
                  >
                    <Volume2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(scan.id)}
                    disabled={deleting === scan.id}
                    className="p-2 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-400 transition-colors disabled:opacity-40"
                    aria-label={`Delete scan: ${scan.english_text}`}
                    title="Delete"
                  >
                    {deleting === scan.id
                      ? <Loader2 className="w-4 h-4 animate-spin" />
                      : <Trash2 className="w-4 h-4" />
                    }
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}

        {/* Count footer */}
        {!loading && scans.length > 0 && (
          <p className="text-center text-xs text-gray-400 mt-6">
            {scans.length} scan{scans.length !== 1 ? 's' : ''} · stored locally on this device
          </p>
        )}
      </div>
    </div>
  );
}
