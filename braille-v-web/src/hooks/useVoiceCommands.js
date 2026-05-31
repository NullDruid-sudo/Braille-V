/**
 * useVoiceCommands — React hook wrapping the voice commands service.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import voiceCommands from '../services/voiceCommands';

/**
 * @param {Object<string, Function>} commands - Map of keyword → handler
 * @param {boolean} [autoStart=false]         - Start listening on mount
 * @returns {{ isListening, lastCommand, startListening, stopListening, isSupported }}
 */
export default function useVoiceCommands(commands = {}, autoStart = false) {
  const [isListening, setIsListening] = useState(false);
  const [lastCommand, setLastCommand] = useState('');
  const commandsRef = useRef(commands);

  // Keep the ref in sync so we don't re-init on every render
  useEffect(() => {
    commandsRef.current = commands;
    if (isListening) {
      voiceCommands.setCommands(commands);
    }
  }, [commands, isListening]);

  const startListening = useCallback(() => {
    voiceCommands.start({
      commands: commandsRef.current,
      onResult: (transcript) => setLastCommand(transcript),
      onError: (err) => console.warn('Voice error:', err),
    });
    setIsListening(true);
  }, []);

  const stopListening = useCallback(() => {
    voiceCommands.stop();
    setIsListening(false);
  }, []);

  // Auto-start if requested
  useEffect(() => {
    if (autoStart && voiceCommands.isSupported) {
      startListening();
    }
    return () => stopListening();
  }, [autoStart, startListening, stopListening]);

  return {
    isListening,
    lastCommand,
    startListening,
    stopListening,
    isSupported: voiceCommands.isSupported,
  };
}
