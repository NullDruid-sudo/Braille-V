/**
 * App — Root component with simple state-based routing.
 * Pages: home → scanner → results → history → settings
 */

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import Home from './components/Home';
import Scanner from './components/Scanner';
import Results from './components/Results';
import History from './components/History';
import Settings from './components/Settings';
import useVoiceCommands from './hooks/useVoiceCommands';
import tts from './services/tts';
import settingsService from './services/settings';
import { Mic, MicOff } from 'lucide-react';

const PAGES = {
  HOME: 'home',
  SCANNER: 'scanner',
  RESULTS: 'results',
  HISTORY: 'history',
  SETTINGS: 'settings',
};

export default function App() {
  const [page, setPage] = useState(PAGES.HOME);
  const [scanResult, setScanResult] = useState(null);

  // Apply persisted settings on mount
  useEffect(() => {
    const saved = settingsService.getAll();
    tts.setRate(saved.voiceRate);
    if (saved.language) tts.setVoice(saved.language);
  }, []);

  // ── Navigation helpers ──────────────────────────────────────────────
  const goHome     = useCallback(() => setPage(PAGES.HOME),     []);
  const goScanner  = useCallback(() => setPage(PAGES.SCANNER),  []);
  const goHistory  = useCallback(() => setPage(PAGES.HISTORY),  []);
  const goSettings = useCallback(() => setPage(PAGES.SETTINGS), []);
  const goResults  = useCallback((result) => {
    setScanResult(result);
    setPage(PAGES.RESULTS);
  }, []);

  // ── Voice commands (global) ─────────────────────────────────────────
  const commands = useMemo(
    () => ({
      scan:    () => { if (page === PAGES.HOME) goScanner(); },
      start:   () => { if (page === PAGES.HOME) goScanner(); },
      repeat:  () => {
        if (page === PAGES.RESULTS && scanResult?.english_text) {
          tts.speak(scanResult.english_text);
        }
      },
      home:     () => goHome(),
      history:  () => goHistory(),
      settings: () => goSettings(),
      back: () => {
        if (page === PAGES.RESULTS)   goScanner();
        else if (page === PAGES.SCANNER)  goHome();
        else if (page === PAGES.HISTORY)  goHome();
        else if (page === PAGES.SETTINGS) goHome();
      },
      help: () => {
        const msgs = {
          [PAGES.HOME]:     'Say: scan, history, settings, or help.',
          [PAGES.SCANNER]:  'Say: scan or capture to take a photo. Say: back to go home.',
          [PAGES.RESULTS]:  'Say: repeat, home, scan again, or back.',
          [PAGES.HISTORY]:  'Say: home or back.',
          [PAGES.SETTINGS]: 'Say: home or back.',
        };
        tts.speak(msgs[page] || 'Say: home, scan, history, or settings.');
      },
    }),
    [page, scanResult, goHome, goScanner, goHistory, goSettings],
  );

  const { isListening, isSupported, startListening, stopListening } =
    useVoiceCommands(commands, true);

  // ── Render ──────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-white font-sans text-gray-900 selection:bg-brand-200">
      {/* Page content */}
      {page === PAGES.HOME && (
        <Home onStart={goScanner} onHistory={goHistory} onSettings={goSettings} />
      )}
      {page === PAGES.SCANNER && (
        <Scanner onResult={goResults} onBack={goHome} />
      )}
      {page === PAGES.RESULTS && (
        <Results
          result={scanResult}
          onScanAgain={goScanner}
          onBack={goScanner}
        />
      )}
      {page === PAGES.HISTORY && (
        <History onBack={goHome} onScanAgain={goScanner} />
      )}
      {page === PAGES.SETTINGS && (
        <Settings onBack={goHome} />
      )}

      {/* Floating mic indicator */}
      {isSupported && (
        <button
          id="mic-toggle"
          onClick={isListening ? stopListening : startListening}
          className={`fixed bottom-6 right-6 w-12 h-12 rounded-full shadow-lg flex items-center justify-center transition-all duration-200 z-50 ${
            isListening
              ? 'bg-brand-500 text-white shadow-brand-500/30 animate-pulse-slow'
              : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
          }`}
          aria-label={isListening ? 'Voice commands active — tap to mute' : 'Voice commands muted — tap to activate'}
          title={isListening ? 'Listening…' : 'Voice off'}
        >
          {isListening ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
        </button>
      )}
    </div>
  );
}
