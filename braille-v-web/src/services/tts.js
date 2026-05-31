/**
 * Braille-V Text-to-Speech Service
 * Wraps the Web Speech Synthesis API.
 */

class TTSService {
  constructor() {
    this.synth = window.speechSynthesis || null;
    this._rate = 0.95;
    this._pitch = 1;
    this._voice = null;
  }

  /** Check browser support. */
  get isSupported() {
    return !!this.synth;
  }

  /** Speak text aloud. Returns a Promise that resolves when done. */
  speak(text) {
    return new Promise((resolve, reject) => {
      if (!this.isSupported) {
        reject(new Error('Speech synthesis not supported'));
        return;
      }

      // Cancel any ongoing speech
      this.stop();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = this._rate;
      utterance.pitch = this._pitch;

      if (this._voice) {
        utterance.voice = this._voice;
      }

      utterance.onend = () => resolve();
      utterance.onerror = (e) => reject(e);

      this.synth.speak(utterance);
    });
  }

  /** Stop any ongoing speech. */
  stop() {
    if (this.isSupported) {
      this.synth.cancel();
    }
  }

  /** Set speech rate (0.1 – 10, default 0.95). */
  setRate(rate) {
    this._rate = Math.max(0.1, Math.min(10, rate));
  }

  /** Set speech pitch (0 – 2, default 1). */
  setPitch(pitch) {
    this._pitch = Math.max(0, Math.min(2, pitch));
  }

  /** Get available voices. */
  getVoices() {
    if (!this.isSupported) return [];
    return this.synth.getVoices();
  }

  /** Set voice by name or language. */
  setVoice(nameOrLang) {
    const voices = this.getVoices();
    this._voice =
      voices.find((v) => v.name === nameOrLang) ||
      voices.find((v) => v.lang.startsWith(nameOrLang)) ||
      null;
  }
}

// Singleton
const tts = new TTSService();
export default tts;
