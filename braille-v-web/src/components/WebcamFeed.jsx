/**
 * WebcamFeed — Reusable camera preview with canvas overlay.
 */

import React, { useEffect } from 'react';
import useWebcam from '../hooks/useWebcam';
import { Camera, CameraOff } from 'lucide-react';

export default function WebcamFeed({ onCapture, autoStart = true }) {
  const { videoRef, canvasRef, isStreaming, error, startCamera, stopCamera, capture } =
    useWebcam();

  useEffect(() => {
    if (autoStart) startCamera();
  }, [autoStart, startCamera]);

  const handleCapture = async () => {
    try {
      const blob = await capture();
      if (onCapture) onCapture(blob);
      // Vibration feedback
      if (navigator.vibrate) navigator.vibrate(50);
    } catch (err) {
      console.error('Capture failed:', err);
    }
  };

  return (
    <div className="relative w-full max-w-lg mx-auto">
      {/* Video preview */}
      <div className="relative overflow-hidden rounded-2xl shadow-lg bg-gray-900 aspect-[4/3]">
        <video
          ref={videoRef}
          className="w-full h-full object-cover"
          playsInline
          muted
          aria-label="Camera preview"
        />
        {/* Canvas for capturing (hidden) */}
        <canvas ref={canvasRef} className="hidden" />

        {/* Scanning overlay guides */}
        {isStreaming && (
          <div className="absolute inset-0 pointer-events-none">
            {/* Corner brackets */}
            <div className="absolute top-4 left-4 w-10 h-10 border-t-2 border-l-2 border-white/60 rounded-tl-lg" />
            <div className="absolute top-4 right-4 w-10 h-10 border-t-2 border-r-2 border-white/60 rounded-tr-lg" />
            <div className="absolute bottom-4 left-4 w-10 h-10 border-b-2 border-l-2 border-white/60 rounded-bl-lg" />
            <div className="absolute bottom-4 right-4 w-10 h-10 border-b-2 border-r-2 border-white/60 rounded-br-lg" />
            {/* Center guide text */}
            <div className="absolute bottom-6 left-0 right-0 text-center">
              <span className="text-white/70 text-sm font-medium bg-black/30 px-3 py-1 rounded-full">
                Position Braille text in frame
              </span>
            </div>
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
            <div className="text-center px-6">
              <CameraOff className="w-12 h-12 text-red-400 mx-auto mb-3" />
              <p className="text-white/80 text-sm">{error}</p>
              <button
                onClick={startCamera}
                className="mt-4 px-4 py-2 bg-brand-500 text-white rounded-lg text-sm font-medium hover:bg-brand-700 transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {/* Not streaming placeholder */}
        {!isStreaming && !error && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
            <button
              onClick={startCamera}
              className="flex items-center gap-2 px-6 py-3 bg-brand-500 text-white rounded-xl text-base font-semibold hover:bg-brand-700 transition-all hover:scale-105"
              aria-label="Start camera"
            >
              <Camera className="w-5 h-5" />
              Start Camera
            </button>
          </div>
        )}
      </div>

      {/* Capture button */}
      {isStreaming && (
        <div className="flex justify-center mt-6">
          <button
            id="capture-button"
            onClick={handleCapture}
            className="group relative w-20 h-20 bg-brand-500 rounded-full shadow-xl hover:bg-brand-700 active:scale-95 transition-all duration-150 focus:outline-none focus:ring-4 focus:ring-brand-300"
            aria-label="Capture and scan Braille"
          >
            {/* Outer ring */}
            <span className="absolute inset-0 rounded-full border-4 border-white/30 group-hover:border-white/50 transition-colors" />
            {/* Inner circle */}
            <span className="absolute inset-3 rounded-full bg-white/90 group-hover:bg-white transition-colors" />
          </button>
        </div>
      )}
    </div>
  );
}
