# Web Audio API Template Reference

## AudioContext Fundamentals

```javascript
// Create context (handle browser autoplay policy)
const ctx = new AudioContext();
// If suspended: ctx.resume();

// Master output
const master = ctx.createGain();
master.gain.value = 0.5;
master.connect(ctx.destination);

// Timing: always use ctx.currentTime for scheduling
const now = ctx.currentTime;
```

### Key Principles

- **Never assign `.value` directly for envelopes** — use `setValueAtTime`, `linearRampToValueAtTime`, `exponentialRampToValueAtTime`
- **`exponentialRampToValueAtTime` cannot target 0** — use a very small value like 0.001
- **All scheduling is in absolute seconds** from `ctx.currentTime`
- **Connect nodes in chains**: source → processing → destination
- **Call `.start()` on oscillator/buffer sources** — they are one-shot (create new for each note)

---

## Oscillator Patterns

```javascript
// Basic oscillator
const osc = ctx.createOscillator();
osc.type = 'sawtooth';  // 'sine', 'square', 'triangle', 'sawtooth'
osc.frequency.value = 440;
osc.connect(master);
osc.start(now);
osc.stop(now + 2);

// Detuned pair
const osc1 = ctx.createOscillator();
const osc2 = ctx.createOscillator();
osc1.type = osc2.type = 'sawtooth';
osc1.frequency.value = 440;
osc2.frequency.value = 440;
osc2.detune.value = 8; // cents
const oscMix = ctx.createGain();
oscMix.gain.value = 0.5;
osc1.connect(oscMix);
osc2.connect(oscMix);
oscMix.connect(master);
osc1.start(now);
osc2.start(now);

// Custom waveform (PeriodicWave)
const real = new Float32Array([0, 0, 0, 0]); // cosine coefficients
const imag = new Float32Array([0, 1, 0.5, 0.25]); // sine coefficients (harmonics)
const wave = ctx.createPeriodicWave(real, imag);
osc.setPeriodicWave(wave);
```

---

## Filter Patterns

```javascript
// Biquad filter (all standard types)
const filter = ctx.createBiquadFilter();
filter.type = 'lowpass'; // 'highpass', 'bandpass', 'notch', 'allpass', 'peaking', 'lowshelf', 'highshelf'
filter.frequency.value = 1000;
filter.Q.value = 5;  // resonance (0.001 to 1000)
// For peaking/shelf: filter.gain.value = 6; // dB

osc.connect(filter);
filter.connect(master);

// Steeper filter: chain two biquads (24dB/oct)
const filter1 = ctx.createBiquadFilter();
const filter2 = ctx.createBiquadFilter();
filter1.type = filter2.type = 'lowpass';
filter1.frequency.value = filter2.frequency.value = 1000;
filter1.Q.value = filter2.Q.value = 0.707; // Butterworth Q for cascaded
osc.connect(filter1);
filter1.connect(filter2);
filter2.connect(master);
```

---

## Envelope Patterns (AudioParam Scheduling)

```javascript
// ADSR envelope on gain
function applyADSR(param, now, a, d, s, r, peak = 1.0) {
  param.cancelScheduledValues(now);
  param.setValueAtTime(0.001, now);                          // Start near zero
  param.exponentialRampToValueAtTime(peak, now + a);          // Attack
  param.exponentialRampToValueAtTime(Math.max(s * peak, 0.001), now + a + d); // Decay to sustain
  // Release triggered separately (see noteOff)
}

function noteOff(param, now, r) {
  param.cancelScheduledValues(now);
  param.setValueAtTime(param.value, now);
  param.exponentialRampToValueAtTime(0.001, now + r);
}

// Usage:
const ampEnv = ctx.createGain();
osc.connect(ampEnv);
ampEnv.connect(master);
applyADSR(ampEnv.gain, now, 0.01, 0.3, 0.5, 0.1);

// Percussive envelope (no sustain)
function applyPerc(param, now, attack, decay, peak = 1.0) {
  param.cancelScheduledValues(now);
  param.setValueAtTime(0.001, now);
  param.exponentialRampToValueAtTime(peak, now + attack);
  param.exponentialRampToValueAtTime(0.001, now + attack + decay);
}

// Filter envelope
function applyFilterEnv(filter, now, startFreq, peakFreq, sustainFreq, a, d) {
  filter.frequency.cancelScheduledValues(now);
  filter.frequency.setValueAtTime(startFreq, now);
  filter.frequency.exponentialRampToValueAtTime(peakFreq, now + a);
  filter.frequency.exponentialRampToValueAtTime(sustainFreq, now + a + d);
}

// Pitch envelope (e.g., for kick drum)
function applyPitchDrop(osc, now, startFreq, endFreq, duration) {
  osc.frequency.setValueAtTime(startFreq, now);
  osc.frequency.exponentialRampToValueAtTime(endFreq, now + duration);
}
```

---

## LFO / Modulation Patterns

```javascript
// LFO → filter cutoff
const lfo = ctx.createOscillator();
lfo.type = 'sine';
lfo.frequency.value = 0.3; // Hz
const lfoGain = ctx.createGain();
lfoGain.gain.value = 500; // modulation depth in Hz
lfo.connect(lfoGain);
lfoGain.connect(filter.frequency); // modulates filter cutoff
lfo.start(now);

// LFO → pitch (vibrato)
const vibrato = ctx.createOscillator();
vibrato.type = 'sine';
vibrato.frequency.value = 5.5; // Hz
const vibratoDepth = ctx.createGain();
vibratoDepth.gain.value = 10; // cents of vibrato
vibrato.connect(vibratoDepth);
vibratoDepth.connect(osc.detune); // modulates detune in cents
vibrato.start(now);

// LFO → amplitude (tremolo)
const tremolo = ctx.createOscillator();
tremolo.type = 'sine';
tremolo.frequency.value = 4; // Hz
const tremoloDepth = ctx.createGain();
tremoloDepth.gain.value = 0.3; // 30% depth
const tremoloMix = ctx.createGain();
tremoloMix.gain.value = 1.0;
tremolo.connect(tremoloDepth);
tremoloDepth.connect(tremoloMix.gain);
tremolo.start(now);
// Route audio through tremoloMix
```

---

## FM Synthesis Pattern

```javascript
function fmSynth(ctx, carrierFreq, ratio, index, duration) {
  const now = ctx.currentTime;
  const modFreq = carrierFreq * ratio;

  // Modulator
  const mod = ctx.createOscillator();
  mod.frequency.value = modFreq;
  const modGain = ctx.createGain();
  modGain.gain.value = modFreq * index; // FM depth

  // Carrier
  const carrier = ctx.createOscillator();
  carrier.frequency.value = carrierFreq;

  // FM routing: mod → modGain → carrier.frequency
  mod.connect(modGain);
  modGain.connect(carrier.frequency);

  // Output
  const ampEnv = ctx.createGain();
  carrier.connect(ampEnv);

  // Envelopes
  applyPerc(ampEnv.gain, now, 0.001, duration, 0.5);

  // Decaying mod index
  modGain.gain.setValueAtTime(modFreq * index, now);
  modGain.gain.exponentialRampToValueAtTime(modFreq * 0.1, now + duration * 0.7);

  mod.start(now);
  carrier.start(now);
  mod.stop(now + duration + 0.1);
  carrier.stop(now + duration + 0.1);

  return ampEnv;
}
```

---

## Effects Patterns

```javascript
// Delay with feedback
function createDelay(ctx, time, feedback, wetLevel) {
  const input = ctx.createGain();
  const delay = ctx.createDelay(5.0);
  delay.delayTime.value = time;
  const fb = ctx.createGain();
  fb.gain.value = feedback;
  const wet = ctx.createGain();
  wet.gain.value = wetLevel;

  input.connect(delay);
  delay.connect(fb);
  fb.connect(delay); // feedback loop
  delay.connect(wet);

  return { input, output: wet };
}

// Convolution reverb (using impulse response)
async function createReverb(ctx, seconds, decay) {
  const sampleRate = ctx.sampleRate;
  const length = sampleRate * seconds;
  const impulse = ctx.createBuffer(2, length, sampleRate);
  for (let ch = 0; ch < 2; ch++) {
    const data = impulse.getChannelData(ch);
    for (let i = 0; i < length; i++) {
      data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / length, decay);
    }
  }
  const convolver = ctx.createConvolver();
  convolver.buffer = impulse;
  return convolver;
}

// Waveshaper distortion
function createDistortion(ctx, amount) {
  const shaper = ctx.createWaveShaper();
  const k = amount;
  const samples = 44100;
  const curve = new Float32Array(samples);
  for (let i = 0; i < samples; i++) {
    const x = (i * 2) / samples - 1;
    curve[i] = ((Math.PI + k) * x) / (Math.PI + k * Math.abs(x));
  }
  shaper.curve = curve;
  shaper.oversample = '4x';
  return shaper;
}

// Simple stereo widening via short delay
function createStereoWidth(ctx, delayMs) {
  const splitter = ctx.createChannelSplitter(2);
  const merger = ctx.createChannelMerger(2);
  const delay = ctx.createDelay();
  delay.delayTime.value = delayMs / 1000;

  splitter.connect(merger, 0, 0); // left direct
  splitter.connect(delay);
  delay.connect(merger, 0, 1);    // right delayed

  return { input: splitter, output: merger };
}
```

---

## Complete Patch Skeleton

```javascript
// Self-contained patch — paste into browser console
(async function() {
  const ctx = new AudioContext();
  const now = ctx.currentTime;
  const master = ctx.createGain();
  master.gain.value = 0.4;
  master.connect(ctx.destination);

  // --- Oscillators ---
  const osc = ctx.createOscillator();
  osc.type = 'sawtooth';
  osc.frequency.value = 110;

  // --- Filter ---
  const filter = ctx.createBiquadFilter();
  filter.type = 'lowpass';
  filter.frequency.value = 800;
  filter.Q.value = 5;

  // --- Amp Envelope ---
  const ampEnv = ctx.createGain();
  ampEnv.gain.setValueAtTime(0.001, now);
  ampEnv.gain.exponentialRampToValueAtTime(1.0, now + 0.01);
  ampEnv.gain.exponentialRampToValueAtTime(0.7, now + 0.3);
  // sustain at 0.7 for duration, then release:
  ampEnv.gain.setValueAtTime(0.7, now + 1.5);
  ampEnv.gain.exponentialRampToValueAtTime(0.001, now + 1.8);

  // --- Connect ---
  osc.connect(filter);
  filter.connect(ampEnv);
  ampEnv.connect(master);

  // --- Play ---
  osc.start(now);
  osc.stop(now + 2);
})();
```

---

## Noise Source Pattern

```javascript
// White noise buffer source (Web Audio has no built-in noise node)
function createNoise(ctx, duration) {
  const bufferSize = ctx.sampleRate * duration;
  const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) {
    data[i] = Math.random() * 2 - 1;
  }
  const source = ctx.createBufferSource();
  source.buffer = buffer;
  return source;
}

// For looping noise:
function createLoopingNoise(ctx) {
  const bufferSize = ctx.sampleRate * 2; // 2-second loop
  const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) {
    data[i] = Math.random() * 2 - 1;
  }
  const source = ctx.createBufferSource();
  source.buffer = buffer;
  source.loop = true;
  return source;
}
```
