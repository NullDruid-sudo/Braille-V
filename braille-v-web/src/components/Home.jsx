/**
 * Home — Landing page with hero section and start button.
 */

import React, { useEffect } from 'react';
import { Eye, Mic, Volume2, Scan } from 'lucide-react';
import tts from '../services/tts';

export default function Home({ onStart }) {
  // Announce page via TTS on mount (voice-first UX)
  useEffect(() => {
    const timer = setTimeout(() => {
      tts.speak('Welcome to Braille V. Tap Start Scanning or say scan to begin.');
    }, 600);
    return () => clearTimeout(timer);
  }, []);

  const features = [
    {
      icon: <Scan className="w-7 h-7" />,
      title: 'Instant Scan',
      desc: 'Point your camera at Braille text and get English translation in seconds',
    },
    {
      icon: <Mic className="w-7 h-7" />,
      title: 'Voice Control',
      desc: 'Navigate hands-free with voice commands — say "scan" to capture',
    },
    {
      icon: <Volume2 className="w-7 h-7" />,
      title: 'Read Aloud',
      desc: 'Results are automatically spoken aloud for accessibility',
    },
    {
      icon: <Eye className="w-7 h-7" />,
      title: 'AI Powered',
      desc: 'YOLOv8 + CNN pipeline with Grade 2 Braille support',
    },
  ];

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12">
      {/* Hero */}
      <div className="text-center mb-12 animate-fade-in">
        {/* Logo mark */}
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-brand-500 to-blue-700 shadow-xl shadow-brand-500/25 mb-6">
          <span className="text-white text-4xl font-extrabold tracking-tight">⠃</span>
        </div>

        <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 tracking-tight mb-3">
          Braille<span className="text-brand-500">-V</span>
        </h1>
        <p className="text-lg text-gray-500 max-w-md mx-auto leading-relaxed">
          AI-powered Braille to English translator.
          <br className="hidden sm:block" />
          Just point your camera and read.
        </p>
      </div>

      {/* Start button */}
      <button
        id="start-scanning-button"
        onClick={onStart}
        className="group relative px-8 py-4 bg-brand-500 text-white text-lg font-semibold rounded-2xl shadow-xl shadow-brand-500/30 hover:bg-brand-700 active:scale-[0.97] transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-brand-300 mb-16"
        aria-label="Start scanning Braille text"
      >
        <span className="flex items-center gap-3">
          <Scan className="w-6 h-6 group-hover:rotate-12 transition-transform" />
          Start Scanning
        </span>
      </button>

      {/* Feature cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 max-w-xl w-full">
        {features.map((f, i) => (
          <div
            key={i}
            className="flex items-start gap-4 p-5 rounded-2xl bg-white border border-gray-100 shadow-sm hover:shadow-md hover:border-brand-200 transition-all duration-200"
          >
            <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-brand-50 text-brand-500 flex items-center justify-center">
              {f.icon}
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-1">{f.title}</h3>
              <p className="text-sm text-gray-500 leading-snug">{f.desc}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Footer hint */}
      <p className="mt-12 text-xs text-gray-400">
        Say <span className="font-medium text-brand-500">"scan"</span> at any time to capture · Works best with embossed Braille
      </p>
    </div>
  );
}
