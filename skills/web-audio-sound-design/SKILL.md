---
name: web-audio-sound-design
description: Interactive browser audio synthesis, procedural game audio, and UI sound design using the native Web Audio API and Tone.js (inspired by dannyjpwilliams/ui-sound-design-skill and professional game audio engines). Covers chiptune/8-bit synthesis, tactile UI earcons, ADSR envelopes, procedural noise buffers, biquad filters, and spatial 3D audio.
---

# Web Audio API & Interactive Sound Design

An expert sound design and interactive audio skill for generating rich sound effects, dynamic background music, and responsive UI earcons in web applications and browser games without heavy external audio sample downloads.

## 1. Modern AudioContext Lifecycle & Autoplay Policy

Modern browsers strictly block audio until a user gesture (click, tap, keypress). Always initialize lazily and unlock cleanly:

```javascript
class AudioManager {
  constructor() {
    this.ctx = null;
    this.masterGain = null;
    this.isMuted = false;
  }

  ensureContext() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
      this.masterGain = this.ctx.createGain();
      this.masterGain.gain.setValueAtTime(0.5, this.ctx.currentTime);
      this.masterGain.connect(this.ctx.destination);
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
    return this.ctx;
  }
}
```

---

## 2. ADSR Envelopes & Procedural Oscillators

Never cut audio abruptly (causes clicks/pops). Always apply exponential ramp decays:

```javascript
// Generic Sound Generator with ADSR Envelope
function playSynthTone(ctx, dest, { freq = 440, type = 'sine', attack = 0.01, decay = 0.1, sustain = 0.6, release = 0.2, duration = 0.3 }) {
  const osc = ctx.createOscillator();
  const env = ctx.createGain();
  const t = ctx.currentTime;

  osc.type = type;
  osc.frequency.setValueAtTime(freq, t);

  // Attack -> Decay -> Sustain
  env.gain.setValueAtTime(0.0001, t);
  env.gain.exponentialRampToValueAtTime(1.0, t + attack);
  env.gain.exponentialRampToValueAtTime(sustain, t + attack + decay);

  // Release
  const releaseStart = t + duration;
  env.gain.setValueAtTime(sustain, releaseStart);
  env.gain.exponentialRampToValueAtTime(0.0001, releaseStart + release);

  osc.connect(env);
  env.connect(dest);

  osc.start(t);
  osc.stop(releaseStart + release + 0.05);
}
```

---

## 3. Tactile UI Earcons (Click, Confirm, Error, Notification)

Modern UI sound design requires subtle, elegant audio feedback:

```javascript
const UI_SOUNDS = {
  // Soft tactile button tap
  click(ctx, dest) {
    const t = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(180, t);
    osc.frequency.exponentialRampToValueAtTime(60, t + 0.04);
    gain.gain.setValueAtTime(0.12, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + 0.04);
    osc.connect(gain);
    gain.connect(dest);
    osc.start(t);
    osc.stop(t + 0.05);
  },

  // Elegant two-tone success chord
  success(ctx, dest) {
    const t = ctx.currentTime;
    [523.25, 659.25, 783.99].forEach((f, i) => { // C5, E5, G5
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(f, t + i * 0.04);
      gain.gain.setValueAtTime(0.001, t + i * 0.04);
      gain.gain.linearRampToValueAtTime(0.08, t + i * 0.04 + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.0001, t + i * 0.04 + 0.4);
      osc.connect(gain);
      gain.connect(dest);
      osc.start(t + i * 0.04);
      osc.stop(t + i * 0.04 + 0.45);
    });
  },

  // Subtle error blip
  error(ctx, dest) {
    const t = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(140, t);
    osc.frequency.setValueAtTime(110, t + 0.08);
    gain.gain.setValueAtTime(0.15, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + 0.2);
    osc.connect(gain);
    gain.connect(dest);
    osc.start(t);
    osc.stop(t + 0.22);
  }
};
```

---

## 4. Retro 8-Bit Chiptune Sound Effects

Procedural generation of classic arcade and retro console audio:

```javascript
const RETRO_SFX = {
  // Jump: Fast upward frequency sweep
  jump(ctx, dest) {
    const t = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'square';
    osc.frequency.setValueAtTime(150, t);
    osc.frequency.exponentialRampToValueAtTime(600, t + 0.15);
    gain.gain.setValueAtTime(0.15, t);
    gain.gain.linearRampToValueAtTime(0.001, t + 0.15);
    osc.connect(gain);
    gain.connect(dest);
    osc.start(t);
    osc.stop(t + 0.16);
  },

  // Coin / Gem Pickup: Quick arpeggio
  coin(ctx, dest) {
    const t = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'square';
    osc.frequency.setValueAtTime(987.77, t); // B5
    osc.frequency.setValueAtTime(1318.51, t + 0.08); // E6
    gain.gain.setValueAtTime(0.12, t);
    gain.gain.linearRampToValueAtTime(0.001, t + 0.35);
    osc.connect(gain);
    gain.connect(dest);
    osc.start(t);
    osc.stop(t + 0.36);
  },

  // Explosion: Filtered white noise burst with pitch drop
  explosion(ctx, dest) {
    const t = ctx.currentTime;
    const bufferSize = ctx.sampleRate * 0.35;
    const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = Math.random() * 2 - 1;
    }

    const noise = ctx.createBufferSource();
    noise.buffer = buffer;

    const filter = ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(800, t);
    filter.frequency.exponentialRampToValueAtTime(40, t + 0.35);

    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.3, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + 0.35);

    noise.connect(filter);
    filter.connect(gain);
    gain.connect(dest);

    noise.start(t);
    noise.stop(t + 0.36);
  }
};
```
