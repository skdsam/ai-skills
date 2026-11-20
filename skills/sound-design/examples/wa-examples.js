// ============================================================
// Sound Design Skill — Web Audio Examples
// Each patch is self-contained and runnable in a browser console.
// Paste any function then call it to hear the sound.
// ============================================================

// ------------------------------------------------------------
// 1. Subtractive Bass
// Two detuned saws through a resonant LP filter with
// envelope-controlled cutoff. Warm, punchy analog bass.
// ------------------------------------------------------------
function playSubBass(freq = 55, duration = 1.5) {
  const ctx = new AudioContext();
  const now = ctx.currentTime;

  // Oscillator 1: sawtooth at fundamental
  const osc1 = ctx.createOscillator();
  osc1.type = 'sawtooth';
  osc1.frequency.value = freq;

  // Oscillator 2: sawtooth detuned +8 cents for beating
  const osc2 = ctx.createOscillator();
  osc2.type = 'sawtooth';
  osc2.frequency.value = freq;
  osc2.detune.value = 8;

  // Mix oscillators
  const oscMix = ctx.createGain();
  oscMix.gain.value = 0.5;
  osc1.connect(oscMix);
  osc2.connect(oscMix);

  // Resonant low-pass filter
  const filter = ctx.createBiquadFilter();
  filter.type = 'lowpass';
  filter.Q.value = 6;
  // Filter envelope: 2600 Hz → 600 Hz (bright attack, warm sustain)
  filter.frequency.setValueAtTime(2600, now);
  filter.frequency.exponentialRampToValueAtTime(600, now + 0.25);

  // Amp envelope: fast attack, slight decay, full sustain, quick release
  const amp = ctx.createGain();
  amp.gain.setValueAtTime(0.001, now);
  amp.gain.exponentialRampToValueAtTime(0.6, now + 0.005);
  amp.gain.exponentialRampToValueAtTime(0.5, now + 0.15);
  amp.gain.setValueAtTime(0.5, now + duration - 0.05);
  amp.gain.exponentialRampToValueAtTime(0.001, now + duration);

  // Connect chain: oscs → filter → amp → output
  oscMix.connect(filter);
  filter.connect(amp);
  amp.connect(ctx.destination);

  osc1.start(now);
  osc2.start(now);
  osc1.stop(now + duration + 0.1);
  osc2.stop(now + duration + 0.1);

  // Cleanup
  setTimeout(() => ctx.close(), (duration + 0.5) * 1000);
}

// Usage: playSubBass(55, 1.5);


// ------------------------------------------------------------
// 2. FM Bell
// Carrier:Modulator at 1:1.41 (irrational ratio) for
// inharmonic bell partials. Decaying mod index gives
// bright attack that mellows into a near-sine ring.
// ------------------------------------------------------------
function playFMBell(freq = 523.25, duration = 3.0) {
  const ctx = new AudioContext();
  const now = ctx.currentTime;

  const ratio = 1.41;       // Irrational → inharmonic spectrum
  const index = 5;           // High initial mod index → many sidebands
  const modFreq = freq * ratio;

  // Modulator oscillator
  const mod = ctx.createOscillator();
  mod.frequency.value = modFreq;

  // Modulator gain (controls FM depth)
  // Decaying index: modFreq * index → modFreq * 0.1
  const modGain = ctx.createGain();
  modGain.gain.setValueAtTime(modFreq * index, now);
  modGain.gain.exponentialRampToValueAtTime(modFreq * 0.1, now + duration * 0.8);

  // Carrier oscillator
  const carrier = ctx.createOscillator();
  carrier.frequency.value = freq;

  // FM routing: mod → modGain → carrier.frequency
  mod.connect(modGain);
  modGain.connect(carrier.frequency);

  // Amplitude envelope: percussive with long decay
  const amp = ctx.createGain();
  amp.gain.setValueAtTime(0.001, now);
  amp.gain.exponentialRampToValueAtTime(0.4, now + 0.001);
  amp.gain.exponentialRampToValueAtTime(0.001, now + duration);

  carrier.connect(amp);
  amp.connect(ctx.destination);

  mod.start(now);
  carrier.start(now);
  mod.stop(now + duration + 0.1);
  carrier.stop(now + duration + 0.1);

  setTimeout(() => ctx.close(), (duration + 0.5) * 1000);
}

// Usage: playFMBell(523.25, 3.0);


// ------------------------------------------------------------
// 3. Acid Lead (303-style)
// Single sawtooth through high-resonance LP filter with
// short, punchy filter envelope. The "squelch" comes from
// resonance harmonics excited by the fast cutoff sweep.
// ------------------------------------------------------------
function playAcidLead(freq = 130.81, duration = 0.4) {
  const ctx = new AudioContext();
  const now = ctx.currentTime;

  // Single sawtooth oscillator
  const osc = ctx.createOscillator();
  osc.type = 'sawtooth';
  osc.frequency.value = freq;

  // High-resonance low-pass filter — the acid character
  const filter = ctx.createBiquadFilter();
  filter.type = 'lowpass';
  filter.Q.value = 18; // High resonance for squelch
  // Filter envelope: sharp sweep from 4000 Hz → 300 Hz
  filter.frequency.setValueAtTime(4000, now);
  filter.frequency.exponentialRampToValueAtTime(300, now + 0.15);

  // Amp envelope: fast attack, short decay
  const amp = ctx.createGain();
  amp.gain.setValueAtTime(0.001, now);
  amp.gain.exponentialRampToValueAtTime(0.5, now + 0.005);
  amp.gain.exponentialRampToValueAtTime(0.001, now + duration);

  osc.connect(filter);
  filter.connect(amp);
  amp.connect(ctx.destination);

  osc.start(now);
  osc.stop(now + duration + 0.1);

  setTimeout(() => ctx.close(), (duration + 0.5) * 1000);
}

// Usage: playAcidLead(130.81, 0.4);
// Sequence: [130.81, 164.81, 196, 130.81].forEach((f, i) => setTimeout(() => playAcidLead(f, 0.3), i * 200));


// ------------------------------------------------------------
// 4. Warm Analog Pad
// Two detuned saws through gentle LP filter with slow
// attack envelope. LFO modulates filter for movement.
// Convolution reverb adds spaciousness.
// ------------------------------------------------------------
function playPad(freq = 220, duration = 5.0) {
  const ctx = new AudioContext();
  const now = ctx.currentTime;

  // Oscillator 1
  const osc1 = ctx.createOscillator();
  osc1.type = 'sawtooth';
  osc1.frequency.value = freq;

  // Oscillator 2: detuned +7 cents
  const osc2 = ctx.createOscillator();
  osc2.type = 'sawtooth';
  osc2.frequency.value = freq;
  osc2.detune.value = 7;

  const oscMix = ctx.createGain();
  oscMix.gain.value = 0.4;
  osc1.connect(oscMix);
  osc2.connect(oscMix);

  // Gentle low-pass filter
  const filter = ctx.createBiquadFilter();
  filter.type = 'lowpass';
  filter.frequency.value = 1200;
  filter.Q.value = 2;

  // LFO → filter cutoff for slow timbral movement
  const lfo = ctx.createOscillator();
  lfo.type = 'sine';
  lfo.frequency.value = 0.3;
  const lfoGain = ctx.createGain();
  lfoGain.gain.value = 200;
  lfo.connect(lfoGain);
  lfoGain.connect(filter.frequency);

  // Amp envelope: slow attack (800ms), long release (2.5s)
  const amp = ctx.createGain();
  amp.gain.setValueAtTime(0.001, now);
  amp.gain.exponentialRampToValueAtTime(0.35, now + 0.8);
  amp.gain.setValueAtTime(0.35, now + duration - 2.5);
  amp.gain.exponentialRampToValueAtTime(0.001, now + duration);

  // Simple reverb via convolution
  const reverbLength = ctx.sampleRate * 3;
  const reverbBuffer = ctx.createBuffer(2, reverbLength, ctx.sampleRate);
  for (let ch = 0; ch < 2; ch++) {
    const data = reverbBuffer.getChannelData(ch);
    for (let i = 0; i < reverbLength; i++) {
      data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / reverbLength, 2.5);
    }
  }
  const reverb = ctx.createConvolver();
  reverb.buffer = reverbBuffer;

  const dryGain = ctx.createGain();
  dryGain.gain.value = 0.65;
  const wetGain = ctx.createGain();
  wetGain.gain.value = 0.35;

  // Connect: oscs → filter → amp → dry/wet → output
  oscMix.connect(filter);
  filter.connect(amp);
  amp.connect(dryGain);
  amp.connect(reverb);
  reverb.connect(wetGain);
  dryGain.connect(ctx.destination);
  wetGain.connect(ctx.destination);

  lfo.start(now);
  osc1.start(now);
  osc2.start(now);
  osc1.stop(now + duration + 0.1);
  osc2.stop(now + duration + 0.1);
  lfo.stop(now + duration + 0.1);

  setTimeout(() => ctx.close(), (duration + 1) * 1000);
}

// Usage: playPad(220, 5);


// ------------------------------------------------------------
// 5. Kick Drum (808 style)
// Sine oscillator with pitch envelope from 200 Hz → 45 Hz.
// Short noise burst for beater transient. Soft saturation
// adds harmonics for small-speaker audibility.
// ------------------------------------------------------------
function playKick() {
  const ctx = new AudioContext();
  const now = ctx.currentTime;

  // Body: sine with pitch envelope
  const body = ctx.createOscillator();
  body.type = 'sine';
  body.frequency.setValueAtTime(200, now);
  body.frequency.exponentialRampToValueAtTime(45, now + 0.04);

  const bodyAmp = ctx.createGain();
  bodyAmp.gain.setValueAtTime(0.9, now);
  bodyAmp.gain.exponentialRampToValueAtTime(0.001, now + 0.6);

  // Click: short noise burst through LP filter
  const noiseLength = ctx.sampleRate * 0.02;
  const noiseBuf = ctx.createBuffer(1, noiseLength, ctx.sampleRate);
  const noiseData = noiseBuf.getChannelData(0);
  for (let i = 0; i < noiseLength; i++) {
    noiseData[i] = Math.random() * 2 - 1;
  }
  const click = ctx.createBufferSource();
  click.buffer = noiseBuf;

  const clickFilter = ctx.createBiquadFilter();
  clickFilter.type = 'lowpass';
  clickFilter.frequency.value = 3000;

  const clickAmp = ctx.createGain();
  clickAmp.gain.setValueAtTime(0.3, now);
  clickAmp.gain.exponentialRampToValueAtTime(0.001, now + 0.01);

  // Soft saturation via waveshaper
  const shaper = ctx.createWaveShaper();
  const curve = new Float32Array(44100);
  for (let i = 0; i < 44100; i++) {
    const x = (i * 2) / 44100 - 1;
    curve[i] = Math.tanh(x * 1.5);
  }
  shaper.curve = curve;

  const master = ctx.createGain();
  master.gain.value = 0.7;

  // Connect
  body.connect(bodyAmp);
  bodyAmp.connect(shaper);

  click.connect(clickFilter);
  clickFilter.connect(clickAmp);
  clickAmp.connect(shaper);

  shaper.connect(master);
  master.connect(ctx.destination);

  body.start(now);
  click.start(now);
  body.stop(now + 0.7);

  setTimeout(() => ctx.close(), 1200);
}

// Usage: playKick();
// Pattern: [0, 0.5, 1.0, 1.5].forEach(t => setTimeout(playKick, t * 1000));


// ------------------------------------------------------------
// 6. Plucked String (Karplus-Strong)
// Noise burst filtered into a delay line with feedback.
// The delay line length sets the pitch. LP filter in the
// feedback path causes high harmonics to decay faster,
// mimicking natural string behavior.
// ------------------------------------------------------------
function playPluck(freq = 330, duration = 2.0) {
  const ctx = new AudioContext();
  const now = ctx.currentTime;
  const delayTime = 1 / freq;

  // Excitation: short filtered noise burst (3ms)
  const noiseLength = ctx.sampleRate * 0.05;
  const noiseBuf = ctx.createBuffer(1, noiseLength, ctx.sampleRate);
  const noiseData = noiseBuf.getChannelData(0);
  for (let i = 0; i < noiseLength; i++) {
    noiseData[i] = Math.random() * 2 - 1;
  }
  const excitation = ctx.createBufferSource();
  excitation.buffer = noiseBuf;

  // Excitation filter: controls "pick brightness"
  const exciteFilter = ctx.createBiquadFilter();
  exciteFilter.type = 'lowpass';
  exciteFilter.frequency.value = 4000;

  // Excitation envelope: 3ms burst
  const exciteEnv = ctx.createGain();
  exciteEnv.gain.setValueAtTime(1.0, now);
  exciteEnv.gain.exponentialRampToValueAtTime(0.001, now + 0.003);

  // Delay line (waveguide)
  const delay = ctx.createDelay(1.0);
  delay.delayTime.value = delayTime;

  // Feedback with LP filter (string damping)
  const feedback = ctx.createGain();
  feedback.gain.value = 0.995; // Very high feedback for sustained ring
  const dampFilter = ctx.createBiquadFilter();
  dampFilter.type = 'lowpass';
  dampFilter.frequency.value = 3000; // Damping — lower = darker, faster decay of highs

  // Feedback loop: delay → dampFilter → feedback → delay
  delay.connect(dampFilter);
  dampFilter.connect(feedback);
  feedback.connect(delay);

  // Output
  const amp = ctx.createGain();
  amp.gain.setValueAtTime(0.5, now);
  amp.gain.setValueAtTime(0.5, now + duration - 0.1);
  amp.gain.exponentialRampToValueAtTime(0.001, now + duration);

  // Connect: excitation → exciteFilter → exciteEnv → delay → amp → output
  excitation.connect(exciteFilter);
  exciteFilter.connect(exciteEnv);
  exciteEnv.connect(delay);
  delay.connect(amp);
  amp.connect(ctx.destination);

  excitation.start(now);
  excitation.stop(now + 0.05);

  setTimeout(() => ctx.close(), (duration + 0.5) * 1000);
}

// Usage: playPluck(330, 2);
// Arpeggio: [330, 440, 554.37, 659.25].forEach((f, i) => setTimeout(() => playPluck(f, 1.5), i * 300));
