/**
 * Settings — User preferences with localStorage persistence.
 */

import React, { useState, useEffect } from 'react';
import { ArrowLeft, Volume2, Vibrate, Globe, RotateCcw, Info } from 'lucide-react';
import settingsService from '../services/settings';
import tts from '../services/tts';

const LANGUAGES = [
  { value: 'en-US', label: 'English (US)' },
  { value: 'en-GB', label: 'English (UK)' },
  { value: 'es-ES', label: 'Spanish' },
  { value: 'fr-FR', label: 'French' },
  { value: 'hi-IN', label: 'Hindi' },
];

export default function Settings({ onBack }) {
  const [voiceRate, setVoiceRate] = useState(settingsService.DEFAULTS.voiceRate);
  const [haptics, setHaptics] = useState(settingsService.DEFAULTS.haptics);
  const [language, setLanguage] = useState(settingsService.DEFAULTS.language);

  // Load saved settings on mount
  useEffect(() => {
    const saved = settingsService.getAll();
    setVoiceRate(saved.voiceRate);
    setHaptics(saved.haptics);
    setLanguage(saved.language);
    tts.speak('Settings');
  }, []);

  // Persist & apply voice rate
  const handleRateChange = (val) => {
    const rate = parseFloat(val);
    setVoiceRate(rate);
    settingsService.setVoiceRate(rate);
    tts.setRate(rate);
  };

  // Preview current voice rate
  const handleRatePreview = () => {
    tts.speak('This is how the voice sounds at this speed.');
  };

  // Persist haptics toggle
  const handleHapticsToggle = () => {
    const next = !haptics;
    setHaptics(next);
    settingsService.setHaptics(next);
    if (next && navigator.vibrate) navigator.vibrate(50);
  };

  // Persist language
  const handleLanguageChange = (val) => {
    setLanguage(val);
    settingsService.setLanguage(val);
    tts.setVoice(val);
  };

  const handleReset = () => {
    settingsService.reset();
    const d = settingsService.DEFAULTS;
    setVoiceRate(d.voiceRate);
    setHaptics(d.haptics);
    setLanguage(d.language);
    tts.setRate(d.voiceRate);
    tts.speak('Settings reset to defaults.');
    if (navigator.vibrate) navigator.vibrate(30);
  };

  return (
    <div className="min-h-screen flex flex-col px-4 py-6">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <button
          id="settings-back-button"
          onClick={onBack}
          className="flex items-center justify-center w-10 h-10 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-600 transition-colors"
          aria-label="Go back to home"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h1 className="text-xl font-bold text-gray-900">Settings</h1>
        <button
          id="settings-reset-button"
          onClick={handleReset}
          className="ml-auto flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-500 hover:bg-gray-100 rounded-lg transition-colors"
          aria-label="Reset to defaults"
          title="Reset to defaults"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Reset
        </button>
      </div>

      <div className="max-w-lg mx-auto w-full space-y-4 animate-fade-in">

        {/* Voice Speed */}
        <section className="p-5 bg-white rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-brand-50 text-brand-500 flex items-center justify-center">
                <Volume2 className="w-5 h-5" />
              </div>
              <div>
                <h2 className="font-semibold text-gray-900 text-sm">Voice Speed</h2>
                <p className="text-xs text-gray-400">Controls text-to-speech rate</p>
              </div>
            </div>
            <span className="text-sm font-mono font-semibold text-brand-500 bg-brand-50 px-2 py-0.5 rounded-lg">
              {voiceRate.toFixed(1)}×
            </span>
          </div>

          <input
            id="voice-rate-slider"
            type="range"
            min="0.3"
            max="0.8"
            step="0.1"
            value={voiceRate}
            onChange={(e) => handleRateChange(e.target.value)}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-brand-500"
            aria-label="Voice speed"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-1.5">
            <span>0.3× Slow</span>
            <span>0.8× Fast</span>
          </div>

          <button
            id="preview-voice-button"
            onClick={handleRatePreview}
            className="mt-4 w-full py-2 text-sm text-brand-500 border border-brand-200 rounded-xl hover:bg-brand-50 transition-colors font-medium"
            aria-label="Preview voice speed"
          >
            Preview Voice
          </button>
        </section>

        {/* Haptic Feedback */}
        <section className="p-5 bg-white rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-brand-50 text-brand-500 flex items-center justify-center">
                <Vibrate className="w-5 h-5" />
              </div>
              <div>
                <h2 className="font-semibold text-gray-900 text-sm">Haptic Feedback</h2>
                <p className="text-xs text-gray-400">Vibration on scans and actions</p>
              </div>
            </div>

            {/* Toggle switch */}
            <button
              id="haptics-toggle"
              role="switch"
              aria-checked={haptics}
              onClick={handleHapticsToggle}
              className={`relative w-12 h-6 rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-brand-300 focus:ring-offset-1 ${
                haptics ? 'bg-brand-500' : 'bg-gray-200'
              }`}
              aria-label={`Haptic feedback ${haptics ? 'on' : 'off'}`}
            >
              <span
                className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform duration-200 ${
                  haptics ? 'translate-x-6' : 'translate-x-0'
                }`}
              />
            </button>
          </div>
        </section>

        {/* Language */}
        <section className="p-5 bg-white rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-9 h-9 rounded-xl bg-brand-50 text-brand-500 flex items-center justify-center">
              <Globe className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-semibold text-gray-900 text-sm">Voice Language</h2>
              <p className="text-xs text-gray-400">Language for text-to-speech output</p>
            </div>
          </div>

          <select
            id="language-select"
            value={language}
            onChange={(e) => handleLanguageChange(e.target.value)}
            className="w-full px-3 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-brand-300 cursor-pointer"
            aria-label="Select language"
          >
            {LANGUAGES.map((l) => (
              <option key={l.value} value={l.value}>
                {l.label}
              </option>
            ))}
          </select>
        </section>

        {/* About */}
        <section className="p-5 bg-gray-50 rounded-2xl border border-gray-100">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-9 h-9 rounded-xl bg-white border border-gray-200 text-gray-400 flex items-center justify-center">
              <Info className="w-5 h-5" />
            </div>
            <h2 className="font-semibold text-gray-900 text-sm">About</h2>
          </div>
          <div className="space-y-1.5 text-xs text-gray-500">
            <p><span className="font-medium text-gray-700">App</span> — Braille-V v1.0</p>
            <p><span className="font-medium text-gray-700">Team</span> — Antigravity</p>
            <p><span className="font-medium text-gray-700">Hackathon</span> — BrailleVision 2026</p>
            <p className="mt-2 text-gray-400 leading-relaxed">
              AI-powered Braille reader using YOLOv8 dot detection, CNN character
              classification, and Grade 2 Braille uncontraction. Fully voice-navigable.
            </p>
          </div>
        </section>

      </div>
    </div>
  );
}
