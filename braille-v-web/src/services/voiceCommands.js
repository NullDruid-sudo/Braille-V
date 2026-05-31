/**
 * Braille-V Voice Commands Service
 * Wraps the Web Speech Recognition API.
 */

/**
 * @typedef {Object} VoiceCommandConfig
 * @property {Object<string, Function>} commands - Map of command words → handlers
 * @property {Function} [onResult]    - Called with every recognised transcript
 * @property {Function} [onError]     - Called on recognition errors
 * @property {boolean}  [continuous]  - Keep listening (default true)
 * @property {string}   [lang]        - BCP 47 language tag (default 'en-US')
 */

class VoiceCommandsService {
  constructor() {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    this._recognition = SpeechRecognition ? new SpeechRecognition() : null;
    this._commands = {};
    this._onResult = null;
    this._onError = null;
    this._listening = false;
  }

  /** Check browser support. */
  get isSupported() {
    return !!this._recognition;
  }

  /** Whether the recogniser is currently listening. */
  get isListening() {
    return this._listening;
  }

  /**
   * Configure and start listening.
   * @param {VoiceCommandConfig} config
   */
  start(config = {}) {
    if (!this.isSupported) {
      console.warn('Speech recognition not supported in this browser');
      return;
    }

    const {
      commands = {},
      onResult = null,
      onError = null,
      continuous = true,
      lang = 'en-US',
    } = config;

    this._commands = commands;
    this._onResult = onResult;
    this._onError = onError;

    const rec = this._recognition;
    rec.continuous = continuous;
    rec.interimResults = false;
    rec.lang = lang;

    rec.onresult = (event) => {
      const last = event.results[event.results.length - 1];
      if (!last.isFinal) return;

      const transcript = last[0].transcript.trim().toLowerCase();

      if (this._onResult) {
        this._onResult(transcript);
      }

      // Match commands
      for (const [keyword, handler] of Object.entries(this._commands)) {
        if (transcript.includes(keyword.toLowerCase())) {
          handler(transcript);
          break;
        }
      }
    };

    rec.onerror = (event) => {
      // 'no-speech' and 'aborted' are common non-fatal errors
      if (event.error === 'no-speech' || event.error === 'aborted') return;
      if (this._onError) this._onError(event);
    };

    rec.onend = () => {
      // Auto-restart if still supposed to be listening
      if (this._listening) {
        try {
          rec.start();
        } catch {
          // Already started — ignore
        }
      }
    };

    try {
      rec.start();
      this._listening = true;
    } catch {
      // Already started
    }
  }

  /** Stop listening. */
  stop() {
    this._listening = false;
    if (this._recognition) {
      try {
        this._recognition.stop();
      } catch {
        // Not started — ignore
      }
    }
  }

  /** Update the command map while running. */
  setCommands(commands) {
    this._commands = commands;
  }
}

// Singleton
const voiceCommands = new VoiceCommandsService();
export default voiceCommands;
