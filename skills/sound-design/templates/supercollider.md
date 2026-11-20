# SuperCollider Template Reference

## Language Essentials

```supercollider
// Boot the server
s.boot;

// SynthDef: define a synthesis recipe
SynthDef(\name, { |out=0, freq=440, amp=0.5, gate=1|
    var sig;
    sig = SinOsc.ar(freq) * amp;
    sig = sig * EnvGen.kr(Env.adsr(0.01, 0.3, 0.5, 0.1), gate, doneAction: 2);
    Out.ar(out, sig ! 2);  // ! 2 = duplicate to stereo
}).add;

// Play it
x = Synth(\name, [\freq, 440, \amp, 0.5]);

// Stop it
x.set(\gate, 0);  // triggers release

// Free immediately
x.free;
```

### Key Conventions

- `.ar` = audio rate, `.kr` = control rate (use for envelopes, LFOs)
- `doneAction: 2` frees the synth when the envelope finishes
- `gate` arg: 1 = note on, 0 = note off (triggers release)
- `Out.ar(out, sig)` writes signal to bus
- `sig ! 2` duplicates mono to stereo
- Use `\symbols` for SynthDef names and args

---

## Oscillator UGens

```supercollider
// Basic waveforms
SinOsc.ar(freq, phase)          // Sine
LFSaw.ar(freq)                  // Sawtooth (non-bandlimited, use for LFO)
Saw.ar(freq)                    // Bandlimited sawtooth
Pulse.ar(freq, width)           // Bandlimited pulse/square (width: 0-1, 0.5=square)
LFTri.ar(freq)                  // Triangle
WhiteNoise.ar                   // White noise
PinkNoise.ar                    // Pink noise (-3dB/oct)
BrownNoise.ar                   // Brown noise (-6dB/oct)

// Detuned pair (common pattern)
var sig = Saw.ar(freq * [0.995, 1.005]).sum;  // Array = multichannel expansion

// Multiple detuned oscillators
var detune = [0.99, 0.995, 1.0, 1.005, 1.01];
var sig = Saw.ar(freq * detune).sum / detune.size;

// Oscillator sync
var master = LFSaw.ar(freq);
var slave = SyncSaw.ar(freq, freq * 2.5);  // slave freq can be modulated
```

---

## Filter UGens

```supercollider
// Low-pass filters
LPF.ar(sig, cutoff)                    // 2nd order (12dB/oct)
RLPF.ar(sig, cutoff, rq)              // Resonant LP (rq = 1/Q, lower = more resonance)
MoogFF.ar(sig, cutoff, gain)           // Moog ladder filter emulation
BLowPass4.ar(sig, cutoff, rq)         // 4th order (24dB/oct)

// High-pass filters
HPF.ar(sig, cutoff)                    // 2nd order
RHPF.ar(sig, cutoff, rq)              // Resonant HP

// Band-pass
BPF.ar(sig, cutoff, rq)               // Band-pass
BBandPass.ar(sig, cutoff, bw)          // Butterworth band-pass

// Notch
BRF.ar(sig, cutoff, rq)               // Band-reject

// Comb filter (for Karplus-Strong, flanging)
CombL.ar(sig, maxDelay, delay, decay) // Linear interpolation
CombC.ar(sig, maxDelay, delay, decay) // Cubic interpolation (better quality)

// rq values: 1.0 = no resonance, 0.01 = extreme resonance
// Typical: 0.3-0.5 moderate, 0.1-0.2 high resonance
```

---

## Envelope UGens

```supercollider
// ADSR envelope (sustaining — needs gate)
EnvGen.kr(Env.adsr(
    attackTime: 0.01,
    decayTime: 0.3,
    sustainLevel: 0.5,
    releaseTime: 0.1,
    peakLevel: 1.0,
    curve: -4         // negative = exponential (natural), 0 = linear
), gate, doneAction: 2)

// Percussive envelope (non-sustaining)
EnvGen.kr(Env.perc(
    attackTime: 0.001,
    releaseTime: 0.5,
    level: 1.0,
    curve: -4
), doneAction: 2)

// Custom envelope
EnvGen.kr(Env(
    levels: [0, 1, 0.5, 0],
    times: [0.01, 0.2, 0.5],
    curve: [-4, -2, -4]
), gate, doneAction: 2)

// Trigger-based envelope (for drums)
EnvGen.kr(Env.perc(0.001, 0.3), doneAction: 2)

// Line for pitch sweep
XLine.kr(startFreq, endFreq, duration)  // Exponential (good for pitch)
Line.kr(startVal, endVal, duration)     // Linear
```

---

## LFO Patterns

```supercollider
// Basic LFO
var lfo = SinOsc.kr(rate) * depth + center;

// Vibrato (pitch modulation)
var vibrato = SinOsc.kr(5) * 0.015;  // ~25 cents
var sig = Saw.ar(freq * (1 + vibrato));

// Tremolo (amplitude modulation)
var tremolo = SinOsc.kr(4).range(0.7, 1.0);
sig = sig * tremolo;

// Filter modulation
var filterLfo = SinOsc.kr(0.3).range(400, 2000);
sig = RLPF.ar(sig, filterLfo, 0.3);

// PWM
var pw = SinOsc.kr(0.5).range(0.2, 0.8);
var sig = Pulse.ar(freq, pw);

// Delayed vibrato (natural technique)
var vibratoDepth = EnvGen.kr(Env([0, 0, 1], [0.3, 0.2]));  // 0 for 300ms, ramp up
var vibrato = SinOsc.kr(5.5) * 0.02 * vibratoDepth;
```

---

## Modulation Patterns

```supercollider
// FM synthesis
var modulator = SinOsc.ar(modFreq) * modIndex * modFreq;
var carrier = SinOsc.ar(freq + modulator);

// FM with decaying index (natural timbre)
var modEnv = EnvGen.kr(Env.perc(0.001, 0.5), doneAction: 0);
var modulator = SinOsc.ar(modFreq) * modIndex * modFreq * modEnv;
var carrier = SinOsc.ar(freq + modulator);

// Ring modulation
var sig = SinOsc.ar(carrierFreq) * SinOsc.ar(modFreq);

// Key tracking for filter
var cutoff = freq * keyTrackRatio;  // keyTrackRatio of 4 = cutoff at 4th harmonic

// Velocity mapping
var velAmp = vel.linlin(0, 127, 0.1, 1.0);
var velFilter = vel.linlin(0, 127, 500, 4000);
```

---

## Complete SynthDef Skeleton: Subtractive

```supercollider
SynthDef(\subtractiveTemplate, {
    |out=0, freq=440, amp=0.5, gate=1,
     cutoff=2000, res=0.3, fenvAmt=3000, fenvDec=0.3,
     atkTime=0.01, decTime=0.3, susLevel=0.7, relTime=0.3,
     lfoRate=0.3, lfoDepth=200, detune=0.005|

    var sig, env, fenv, filt, lfo;

    // Oscillators (detuned pair)
    sig = Saw.ar(freq * [1 - detune, 1 + detune]).sum;

    // Filter envelope
    fenv = EnvGen.kr(Env.adsr(0.001, fenvDec, 0.1, relTime), gate) * fenvAmt;

    // LFO for filter
    lfo = SinOsc.kr(lfoRate) * lfoDepth;

    // Filter
    filt = RLPF.ar(sig, (cutoff + fenv + lfo).clip(20, 20000), res);

    // Amplitude envelope
    env = EnvGen.kr(Env.adsr(atkTime, decTime, susLevel, relTime), gate, doneAction: 2);

    // Output
    Out.ar(out, (filt * env * amp) ! 2);
}).add;

// Test
x = Synth(\subtractiveTemplate, [\freq, 110, \cutoff, 800]);
// Stop: x.set(\gate, 0);
```

---

## Complete SynthDef Skeleton: FM

```supercollider
SynthDef(\fmTemplate, {
    |out=0, freq=440, amp=0.5, gate=1,
     ratio=1, index=3, indexDecay=0.5,
     atkTime=0.001, decTime=1.0, susLevel=0, relTime=0.5|

    var modFreq, modAmp, modulator, carrier, env, modEnv;

    // Modulator
    modFreq = freq * ratio;
    modEnv = EnvGen.kr(Env.adsr(0.001, indexDecay, 0.2, relTime), gate);
    modAmp = modFreq * index * modEnv;
    modulator = SinOsc.ar(modFreq) * modAmp;

    // Carrier
    carrier = SinOsc.ar(freq + modulator);

    // Amplitude envelope
    env = EnvGen.kr(Env.adsr(atkTime, decTime, susLevel, relTime), gate, doneAction: 2);

    Out.ar(out, (carrier * env * amp) ! 2);
}).add;

// Test: FM bell
x = Synth(\fmTemplate, [\freq, 440, \ratio, 1.41, \index, 5, \indexDecay, 2]);
```

---

## Effects Patterns

```supercollider
// Reverb (using FreeVerb)
sig = FreeVerb.ar(sig, mix: 0.3, room: 0.7, damp: 0.5);

// Reverb (using FreeVerb2 for stereo input)
sig = FreeVerb2.ar(sig[0], sig[1], mix: 0.3, room: 0.7, damp: 0.5);

// Simple delay
sig = sig + CombC.ar(sig, 0.5, 0.375, 3);  // 375ms delay, 3s decay

// Distortion (soft clip)
sig = (sig * drive).tanh;

// Saturation (gentle)
sig = (sig * 1.5).clip2(1.0);

// Chorus (simple)
var chorusDelay = SinOsc.kr(0.5).range(0.005, 0.015);
sig = sig + DelayC.ar(sig, 0.03, chorusDelay);

// Pan
sig = Pan2.ar(sig, pan);  // pan: -1 (left) to +1 (right)
```

---

## Karplus-Strong Pattern

```supercollider
SynthDef(\karplusStrong, {
    |out=0, freq=440, amp=0.5, decay=3, brightness=2000|
    var excitation, sig;

    // Excitation: short noise burst
    excitation = WhiteNoise.ar * EnvGen.kr(Env.perc(0.001, 0.005));

    // Delay line with filtered feedback
    sig = CombC.ar(excitation, 0.05, freq.reciprocal, decay);
    sig = LPF.ar(sig, brightness);

    // Amplitude envelope (just to clean up)
    sig = sig * EnvGen.kr(Env.linen(0, decay, 0.01), doneAction: 2);

    Out.ar(out, (sig * amp) ! 2);
}).add;
```
