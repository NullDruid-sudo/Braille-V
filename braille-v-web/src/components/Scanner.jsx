/**
 * Scanner — Camera view with scan workflow.
 */

import React, { useState, useEffect } from 'react';
import { ArrowLeft, Loader2, AlertCircle } from 'lucide-react';
import WebcamFeed from './WebcamFeed';
import { scanImage } from '../services/api';
import tts from '../services/tts';

export default function Scanner({ onResult, onBack }) {
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    tts.speak('Scanner ready. Point your camera at Braille text and tap the capture button, or say scan.');
  }, []);

  const handleCapture = async (blob) => {
    setScanning(true);
    setError(null);

    try {
      tts.speak('Scanning');
      if (navigator.vibrate) navigator.vibrate(100);

      const result = await scanImage(blob);

      if (result.success) {
        if (navigator.vibrate) navigator.vibrate([50, 50, 50]);
        onResult(result);
      } else {
        const errMsg = result.error || 'No Braille detected. Try adjusting the angle.';
        setError(errMsg);
        tts.speak(errMsg);
      }
    } catch (err) {
      const errMsg = err.response?.data?.detail || err.message || 'Scan failed. Is the backend running?';
      setError(errMsg);
      tts.speak('Scan failed. Please try again.');
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col px-4 py-6">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <button
          id="scanner-back-button"
          onClick={onBack}
          className="flex items-center justify-center w-10 h-10 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-600 transition-colors"
          aria-label="Go back to home"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h2 className="text-xl font-bold text-gray-900">Scanner</h2>

        {/* Scanning indicator */}
        {scanning && (
          <div className="ml-auto flex items-center gap-2 px-3 py-1.5 bg-brand-50 text-brand-600 rounded-full text-sm font-medium animate-pulse">
            <Loader2 className="w-4 h-4 animate-spin" />
            Scanning…
          </div>
        )}
      </div>

      {/* Camera feed */}
      <div className="flex-1 flex flex-col items-center justify-center">
        <WebcamFeed onCapture={handleCapture} autoStart />

        {/* Error banner */}
        {error && (
          <div className="mt-6 w-full max-w-lg flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 animate-fade-in">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-sm">Scan failed</p>
              <p className="text-sm text-red-600 mt-0.5">{error}</p>
            </div>
          </div>
        )}

        {/* Tips */}
        <div className="mt-6 text-center text-sm text-gray-400">
          <p>Hold camera 6–10 inches from the Braille text</p>
          <p className="mt-1">Ensure even lighting with no glare</p>
        </div>
      </div>
    </div>
  );
}
