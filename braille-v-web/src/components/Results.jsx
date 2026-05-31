/**
 * Results — Display scan output with TTS and repeat functionality.
 */

import React, { useEffect, useState } from 'react';
import { ArrowLeft, RotateCcw, Volume2, VolumeX, Copy, Check, ScanLine } from 'lucide-react';
import tts from '../services/tts';

export default function Results({ result, onScanAgain, onBack }) {
  const [speaking, setSpeaking] = useState(false);
  const [copied, setCopied] = useState(false);

  const { unicode_braille = '', english_text = '', num_cells = 0, num_dots = 0, processing_ms = 0 } = result || {};

  // Auto-speak on mount
  useEffect(() => {
    if (english_text) {
      handleSpeak();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSpeak = async () => {
    if (!english_text) return;
    try {
      setSpeaking(true);
      await tts.speak(english_text);
    } finally {
      setSpeaking(false);
    }
  };

  const handleStop = () => {
    tts.stop();
    setSpeaking(false);
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(english_text);
      setCopied(true);
      if (navigator.vibrate) navigator.vibrate(30);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
      const ta = document.createElement('textarea');
      ta.value = english_text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="min-h-screen flex flex-col px-4 py-6">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <button
          id="results-back-button"
          onClick={onBack}
          className="flex items-center justify-center w-10 h-10 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-600 transition-colors"
          aria-label="Go back"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h2 className="text-xl font-bold text-gray-900">Results</h2>
      </div>

      {/* Main result card */}
      <div className="max-w-lg mx-auto w-full space-y-6 animate-fade-in">
        {/* English text */}
        <div className="p-6 bg-white rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">English Translation</h3>
            <div className="flex items-center gap-1">
              <button
                id="copy-button"
                onClick={handleCopy}
                className="p-2 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors"
                aria-label="Copy text"
                title="Copy to clipboard"
              >
                {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
              </button>
              <button
                id="speak-button"
                onClick={speaking ? handleStop : handleSpeak}
                className={`p-2 rounded-lg transition-colors ${
                  speaking
                    ? 'bg-brand-50 text-brand-600 hover:bg-brand-100'
                    : 'hover:bg-gray-100 text-gray-400 hover:text-gray-600'
                }`}
                aria-label={speaking ? 'Stop reading' : 'Read aloud'}
                title={speaking ? 'Stop' : 'Read aloud'}
              >
                {speaking ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
              </button>
            </div>
          </div>
          <p className="text-2xl font-semibold text-gray-900 leading-relaxed">
            {english_text || '—'}
          </p>
        </div>

        {/* Unicode Braille */}
        <div className="p-5 bg-gray-50 rounded-2xl border border-gray-100">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Unicode Braille</h3>
          <p className="text-3xl tracking-widest text-gray-700 font-mono">
            {unicode_braille || '—'}
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: 'Dots', value: num_dots },
            { label: 'Cells', value: num_cells },
            { label: 'Speed', value: `${Math.round(processing_ms)}ms` },
          ].map((stat) => (
            <div
              key={stat.label}
              className="text-center p-3 bg-white rounded-xl border border-gray-100 shadow-sm"
            >
              <p className="text-2xl font-bold text-brand-500">{stat.value}</p>
              <p className="text-xs text-gray-400 mt-0.5">{stat.label}</p>
            </div>
          ))}
        </div>

        {/* Action buttons */}
        <div className="flex gap-3">
          <button
            id="repeat-button"
            onClick={handleSpeak}
            className="flex-1 flex items-center justify-center gap-2 py-3.5 bg-white border border-gray-200 rounded-xl text-gray-700 font-semibold hover:bg-gray-50 hover:border-gray-300 transition-all active:scale-[0.98]"
            aria-label="Repeat reading"
          >
            <RotateCcw className="w-5 h-5" />
            Repeat
          </button>
          <button
            id="scan-again-button"
            onClick={onScanAgain}
            className="flex-1 flex items-center justify-center gap-2 py-3.5 bg-brand-500 text-white rounded-xl font-semibold hover:bg-brand-700 transition-all active:scale-[0.98] shadow-md shadow-brand-500/20"
            aria-label="Scan again"
          >
            <ScanLine className="w-5 h-5" />
            Scan Again
          </button>
        </div>
      </div>
    </div>
  );
}
