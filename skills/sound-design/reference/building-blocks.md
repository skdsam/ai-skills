# Building Blocks Reference

## Oscillators

### Waveform Spectra

| Waveform | Harmonics Present | Amplitude Rolloff | Character |
|---|---|---|---|
| Sine | Fundamental only | N/A | Pure, clean, hollow |
| Triangle | Odd harmonics (1, 3, 5...) | 1/n² | Soft, mellow, flute-like |
| Square | Odd harmonics (1, 3, 5...) | 1/n | Hollow, woody, clarinet-like |
| Sawtooth | All harmonics (1, 2, 3...) | 1/n | Bright, buzzy, brass-like |
| Pulse (variable) | Depends on width | Varies | Width modulation = spectral animation |
| White noise | All frequencies, equal energy | Flat | Hiss, percussive transients |
| Pink noise | All frequencies, equal energy/octave | -3 dB/octave | More natural, less harsh than white |

### Detuning Techniques

- **Unison detune** (2-8 cents): Thickens without obvious pitch shift. Creates chorus-like beating.
- **Octave layering**: Reinforces fundamental or adds brightness. Sub-octave adds weight.
- **Fifth layering** (×1.5): Adds power chord character. Use carefully — implies harmony.
- **Slight random drift** (±1-3 cents, slow LFO): Emulates analog oscillator instability. Adds warmth and life.

### Oscillator Sync

Hard sync locks Osc2's phase reset to Osc1's cycle. Sweeping Osc2's pitch creates the classic "sync sweep" — a harmonic series that rises in spectral centroid while the fundamental stays locked. Excellent for aggressive leads.

## Filters

### Filter Types

| Type | Effect | Use Case |
|---|---|---|
| Low-pass (LP) | Removes highs above cutoff | Warmth, darkness, bass shaping |
| High-pass (HP) | Removes lows below cutoff | Thinning, removing mud, clarity |
| Band-pass (BP) | Passes band around cutoff | Vocal/nasal quality, telephone effect |
| Notch/Band-reject | Removes band around cutoff | Phaser-like, removing specific resonances |
| Comb | Series of evenly spaced notches | Metallic, flanging, Karplus-Strong |
| All-pass | Phase shift without amplitude change | Phasers (when modulated), diffusion |

### Filter Slopes

- **6 dB/oct (1-pole)**: Gentle rolloff, natural sounding, good for subtle shaping
- **12 dB/oct (2-pole)**: Moderate, classic synth filter (SEM, Oberheim)
- **24 dB/oct (4-pole)**: Aggressive, classic Moog ladder filter sound
- **36-48 dB/oct**: Very steep, almost brick-wall, surgical

### Resonance

- **0-20%**: Subtle emphasis at cutoff, adds presence
- **20-50%**: Noticeable peak, nasal/vocal quality
- **50-80%**: Strong peak, "watery" quality, approaching self-oscillation
- **80-100%**: Near or at self-oscillation — filter becomes a sine oscillator at cutoff frequency

### Key Tracking

Maps note pitch to filter cutoff so that higher notes have proportionally higher cutoff. Without it, high notes sound duller than low notes.
- **0%**: No tracking — fixed cutoff (useful for consistent dark character)
- **50%**: Partial tracking — slight brightening on higher notes
- **100%**: Full tracking — cutoff moves 1:1 with pitch (maintains timbre across range)

### Filter Drive / Saturation

Overdriving the filter input adds harmonics before filtering, creating a fatter, grittier tone. Different saturation curves (soft clip, hard clip, tanh, tube) impart different harmonic characters.

## Envelopes (ADSR)

### Attack

| Range | Character | Use Case |
|---|---|---|
| 0-5 ms | Instant, percussive click | Drums, plucks, transient emphasis |
| 5-30 ms | Fast but no click | Bass, staccato leads |
| 30-100 ms | Soft attack, slight fade-in | Keys, gentle leads |
| 100-500 ms | Slow swell | Pads, strings, ambient |
| 500 ms-5 s | Very slow swell | Ambient pads, swells, risers |

### Decay

| Range | Character | Use Case |
|---|---|---|
| 10-50 ms | Snappy | Percussive sounds, plucks |
| 50-200 ms | Short decay | Keys, staccato sounds |
| 200-500 ms | Medium | General purpose |
| 500 ms-2 s | Long | Pads, sustained evolving sounds |

### Sustain Level

| Level | Character | Use Case |
|---|---|---|
| 0% | No sustain — fully percussive | Drums, plucks, bells |
| 20-40% | Low sustain — mostly percussive with tail | Keys, mallets |
| 50-70% | Medium — good balance | Leads, basses |
| 80-100% | Full sustain — organ-like | Pads, sustained leads, organ |

### Release

| Range | Character | Use Case |
|---|---|---|
| 5-30 ms | Abrupt cutoff | Staccato, tight bass |
| 30-100 ms | Quick fade, no click | Clean stops |
| 100-500 ms | Natural decay | Most melodic sounds |
| 500 ms-3 s | Long tail | Pads, ambient, reverb-like |

## LFOs (Low-Frequency Oscillators)

### Rate Ranges

| Rate | Perceptual Effect |
|---|---|
| 0.1-0.5 Hz | Slow drift, evolving texture, breathing |
| 0.5-2 Hz | Gentle motion, subtle wobble |
| 2-6 Hz | Vibrato range (pitch), tremolo (amplitude), classic modulation |
| 6-20 Hz | Fast modulation, flutter, agitation |
| 20+ Hz | Audio-rate — creates sidebands (becomes AM/FM synthesis) |

### LFO Shapes

- **Sine**: Smooth, natural modulation. Best for vibrato and tremolo.
- **Triangle**: Similar to sine but with linear segments. Slightly brighter modulation character.
- **Square**: Abrupt switching between two states. Trills, hard panning, gating.
- **Saw (up/down)**: Asymmetric sweep. Ramp up for filter sweeps, ramp down for rhythmic patterns.
- **Sample & Hold (S&H)**: Random steps — classic sci-fi "bleep-bloop," random filter movement.
- **Smoothed S&H**: Interpolated random — organic, drifting modulation.

### Common LFO Destinations

| Destination | Effect | Typical Depth |
|---|---|---|
| Pitch | Vibrato | ±5-50 cents (subtle), ±semitone+ (effect) |
| Filter cutoff | Timbral motion, wah | ±100-2000 Hz depending on base cutoff |
| Amplitude | Tremolo | ±10-50% of full amplitude |
| Pulse width | PWM — spectral animation | ±10-40% of pulse width |
| Pan | Auto-pan | ±full stereo width |
| Wavetable position | Spectral morphing | ±10-50% of table range |

## Modulation Routing Paradigm

Every modulation connection has three elements:
1. **Source** — what generates the control signal (envelope, LFO, velocity, key position, aftertouch, mod wheel)
2. **Destination** — what parameter is being modulated (cutoff, pitch, amplitude, effect parameter)
3. **Amount** — how much the source affects the destination (can be positive or negative)

### Key Modulation Sources

- **Envelope**: One-shot shape — attack brightness, decay behavior
- **LFO**: Repeating shape — vibrato, tremolo, cyclic modulation
- **Velocity**: Note-on intensity — dynamics, brightness response
- **Key tracking**: Note position — pitch-dependent timbral scaling
- **Aftertouch/pressure**: Performance expression — vibrato depth, filter opening
- **Mod wheel**: Manual real-time control — vibrato, filter, effect intensity
- **Random/noise**: Per-note variation — humanization, analog character

### Modulation Amount Calibration

Think in perceptual terms:
- **Subtle** (listener may not consciously notice): ±2-5% of parameter range
- **Noticeable** (adds character without dominating): ±5-15% of parameter range
- **Prominent** (key part of the sound): ±15-40% of parameter range
- **Extreme** (special effect): ±40%+ of parameter range
