/**
 * App — Root component with simple state-based routing.
 * Pages: home → scanner → results
 */

import React, { useState, useCallback, useMemo } from 'react';
import Home from './components/Home';
import Scanner from './components/Scanner';
import Results from './components/Results';
import useVoiceCommands from './hooks/useVoiceCommands';
import tts from './services/tts';
import { Mic, MicOff } from 'lucide-react';

const PAGES = { HOME: 'home', SCANNER: 'scanner', RESULTS: 'results' };

export default function App() {
  const [page, setPage] = useState(PAGES.HOME);
  const [scanResult, setScanResult] = useState(null);

  // ── Navigation helpers ──────────────────────────────────────────────
  const goHome = useCallback(() => setPage(PAGES.HOME), []);
  const goScanner = useCallback(() => setPage(PAGES.SCANNER), []);
  const goResults = useCallback((result) => {
    setScanResult(result);
    setPage(PAGES.RESULTS);
  }, []);

  // ── Voice commands (global) ─────────────────────────────────────────
  const commands = useMemo(
    () => ({
      scan: () => {
        if (page === PAGES.HOME) goScanner();
        // In scanner page, the WebcamFeed handles "scan" via its own capture
      },
      repeat: () => {
        if (page === PAGES.RESULTS && scanResult?.english_text) {
          tts.speak(scanResult.english_text);
        }
      },
      home: () => goHome(),
      back: () => {
        if (page === PAGES.RESULTS) goScanner();
        else if (page === PAGES.SCANNER) goHome();
      },
      help: () => {
        tts.speak(
          'Available commands: scan, repeat, home, back, help. Tap the large button to capture Braille text.',
        );
      },
    }),
    [page, scanResult, goHome, goScanner],
  );

  const { isListening, isSupported, startListening, stopListening } =
    useVoiceCommands(commands, true);

  // ── Render ──────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-white font-sans text-gray-900 selection:bg-brand-200">
      {/* Page content */}
      {page === PAGES.HOME && <Home onStart={goScanner} />}
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
