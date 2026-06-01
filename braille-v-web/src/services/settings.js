/**
 * Braille-V Settings Service
 * Persists user preferences in localStorage.
 */

const KEYS = {
  VOICE_RATE: 'bv_voice_rate',
  HAPTICS: 'bv_haptics',
  LANGUAGE: 'bv_language',
};

const DEFAULTS = {
  voiceRate: 0.5,
  haptics: true,
  language: 'en-US',
};

function get(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    if (raw === null) return fallback;
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

function set(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Storage full or unavailable — silently ignore
  }
}

const settingsService = {
  getVoiceRate: () => get(KEYS.VOICE_RATE, DEFAULTS.voiceRate),
  setVoiceRate: (v) => set(KEYS.VOICE_RATE, Math.max(0.3, Math.min(0.8, v))),

  getHaptics: () => get(KEYS.HAPTICS, DEFAULTS.haptics),
  setHaptics: (v) => set(KEYS.HAPTICS, Boolean(v)),

  getLanguage: () => get(KEYS.LANGUAGE, DEFAULTS.language),
  setLanguage: (v) => set(KEYS.LANGUAGE, v),

  /** Load all settings at once. */
  getAll: () => ({
    voiceRate: get(KEYS.VOICE_RATE, DEFAULTS.voiceRate),
    haptics: get(KEYS.HAPTICS, DEFAULTS.haptics),
    language: get(KEYS.LANGUAGE, DEFAULTS.language),
  }),

  /** Reset to defaults. */
  reset: () => {
    Object.values(KEYS).forEach((k) => localStorage.removeItem(k));
  },

  DEFAULTS,
};

export default settingsService;
