# Sound Recipes Reference

Starting-point recipes organized by category. Each recipe specifies synthesis method, key parameters, and the perceptual rationale.

---

## Bass

### Sub Bass
- **Method**: Subtractive (sine or triangle)
- **Osc**: Sine wave or triangle with LP filter at ~200 Hz
- **Envelope**: A: 5ms, D: 100ms, S: 90%, R: 50ms — fast attack, full sustain
- **Filter**: LP 200 Hz, no resonance — remove all harmonics above fundamental
- **Rationale**: Pure low-frequency energy. Sine = cleanest sub; triangle adds slight harmonic warmth
- **Range**: 30-80 Hz fundamentals

### Analog Bass
- **Method**: Subtractive
- **Osc**: Saw + square (mixed ~60/40), detuned 5-8 cents
- **Filter**: LP 24dB/oct, cutoff 400-800 Hz, resonance 20-30%, envelope amount 40-60%
- **Envelope (filter)**: A: 0ms, D: 200-400ms, S: 20%, R: 50ms — plucky filter decay
- **Envelope (amp)**: A: 2ms, D: 150ms, S: 80%, R: 30ms
- **Rationale**: Saw provides full harmonic series; square adds odd-harmonic weight. Detuning creates analog thickness. Filter envelope gives percussive attack brightness.

### Reese Bass
- **Method**: Subtractive
- **Osc**: Two saws, detuned 10-30 cents (wider = more aggressive)
- **Filter**: LP 12dB/oct, cutoff 500-1500 Hz, slight resonance
- **Modulation**: Slow LFO (0.1-0.5 Hz) on detune amount or filter cutoff
- **Rationale**: Wide detuning creates beating/phasing. Slow modulation adds the characteristic Reese "movement." Foundational DnB/dubstep bass.

### FM Bass
- **Method**: FM synthesis
- **Carrier**: Sine at fundamental
- **Modulator**: Sine at 1:1 ratio, index 2-5
- **Mod envelope**: A: 0ms, D: 100-300ms, S: 0.5, R: 50ms — bright attack decaying to purer tone
- **Rationale**: FM adds complex harmonics efficiently. Decaying index mimics natural instrument transients.

### 808 Bass/Kick
- **Method**: Subtractive (sine + pitch envelope)
- **Osc**: Sine wave
- **Pitch envelope**: Start 150-300 Hz, drop to 40-60 Hz in 30-80ms (exponential decay)
- **Amp envelope**: A: 0ms, D: 0ms, S: 100%, R: 500ms-2s (long decay)
- **Optional**: Light saturation/distortion for harmonic content on smaller speakers
- **Rationale**: Pitch sweep creates the characteristic "punch" transient. Long sine tail provides sustained sub-bass.

### Wobble Bass
- **Method**: Subtractive
- **Osc**: Saw or square, often with sub-oscillator
- **Filter**: LP 24dB/oct, cutoff modulated by LFO
- **LFO**: 1/4 to 1/1 note rate (tempo-synced), triangle or sine, full-range cutoff modulation
- **Rationale**: Tempo-synced filter LFO creates rhythmic timbral variation. Foundational dubstep sound.

---

## Leads

### Mono Lead
- **Method**: Subtractive
- **Osc**: Saw wave, monophonic with portamento (20-80ms glide)
- **Filter**: LP 24dB/oct, cutoff 1-3 kHz, resonance 30-40%
- **Envelope (filter)**: A: 0ms, D: 100-200ms, S: 40%, R: 100ms
- **Modulation**: Vibrato LFO 5-6 Hz, ±10-30 cents (delayed onset 200ms)
- **Rationale**: Monophonic forces single-note articulation. Portamento adds expressiveness. Vibrato with delay mimics vocal/string technique.

### Sync Lead
- **Method**: Subtractive with oscillator sync
- **Osc**: Osc1 (master) saw, Osc2 (slave) saw hard-synced to Osc1
- **Modulation**: Osc2 pitch swept by envelope or mod wheel (1-3 octaves above Osc1)
- **Filter**: LP, moderate cutoff, light resonance
- **Rationale**: Sync creates harmonic series that sweeps through resonant peaks as Osc2 pitch changes. Aggressive, cutting lead character.

### Supersaw Lead
- **Method**: Subtractive (unison)
- **Osc**: 5-7 saw oscillators, detuned ±10-40 cents spread
- **Filter**: LP 12dB/oct, cutoff 4-8 kHz, low resonance
- **Stereo**: Unison voices panned across stereo field
- **Rationale**: Multiple detuned saws create dense, chorus-like spectrum. Defines trance/EDM lead and chord sound. More voices = thicker but less defined.

### Acid Lead (TB-303 style)
- **Method**: Subtractive
- **Osc**: Single saw or square
- **Filter**: LP 24dB/oct (4-pole diode ladder), high resonance (60-80%), cutoff 300-1000 Hz
- **Filter envelope**: A: 0ms, D: 200-600ms, S: 0%, R: 50ms — accent-driven envelope amount
- **Modulation**: Accent controls envelope depth and decay time
- **Sequencer**: Short slides (portamento), accent variation
- **Rationale**: High resonance + short filter envelope = characteristic "squelch." Resonance harmonics create screaming quality at high envelope amounts.

---

## Pads

### Analog Pad
- **Method**: Subtractive
- **Osc**: Two saws, detuned 5-15 cents, or saw + pulse with PWM
- **Filter**: LP 12dB/oct, cutoff 1-3 kHz, resonance 10-20%
- **Envelope (amp)**: A: 300ms-1s, D: 500ms, S: 70-80%, R: 1-3s — slow attack is key
- **Modulation**: Slow LFO (0.2-0.5 Hz) on filter cutoff (subtle, ±200 Hz) and pitch (±3-5 cents)
- **Rationale**: Slow attack blends pad into mix. Detuning adds width. Gentle LFO on cutoff and pitch adds organic movement.

### Digital/Wavetable Pad
- **Method**: Wavetable
- **Osc**: Complex wavetable with slow position modulation
- **Table mod**: LFO 0.05-0.2 Hz sweeping through table positions
- **Filter**: LP, gentle cutoff, minimal resonance
- **Envelope**: Very slow attack (1-3s), long release (3-5s)
- **Effects**: Heavy reverb, subtle chorus
- **Rationale**: Wavetable morphing creates spectral evolution impossible with static waveforms. Very slow modulation = glacial, evolving texture.

### Granular Pad
- **Method**: Granular
- **Source**: Any sustained sound (voice, strings, texture)
- **Grains**: 30-60ms, density 20-40/s, Gaussian envelope
- **Pitch scatter**: ±50-200 cents random per grain
- **Position**: Slow random walk through source
- **Effects**: Long reverb (4-8s decay), delay
- **Rationale**: Granular decomposition of source into micro-events creates ethereal, evolving textures. Pitch scatter blurs tonal definition.

### String Pad
- **Method**: Subtractive or additive
- **Osc**: Multiple saws (4-8 voice unison), narrow detune (3-8 cents)
- **Filter**: LP 12dB/oct, cutoff 2-4 kHz
- **Envelope**: A: 500ms-1s, D: 300ms, S: 70%, R: 1-2s
- **Modulation**: Ensemble chorus effect, subtle vibrato (4-5 Hz, ±5 cents)
- **Rationale**: Emulates string ensemble where many players are slightly detuned. Chorus effect reinforces the multi-source character.

---

## Keys

### Electric Piano (FM)
- **Method**: FM (2-operator minimum, 4 for realism)
- **C:M ratio**: 1:1 (primary), 1:14 for "tine" attack transient
- **Mod index envelope**: High attack (I=3-5), fast decay (50-100ms) to low sustain (I=0.5-1)
- **Velocity → mod index**: Higher velocity = more harmonics = brighter attack
- **Amp envelope**: A: 1ms, D: 1-3s (exponential), S: 0%, R: 500ms
- **Effects**: Tremolo (3-5 Hz), subtle chorus, optional overdrive
- **Rationale**: DX7 piano model. Decaying mod index mimics tine strike → mellow sustain. Velocity mapping essential for expression.

### Organ
- **Method**: Additive
- **Partials**: Drawbar harmonics at 1, 2, 3, 4, 5, 6, 8 (Hammond registration)
- **Envelope**: A: 2ms, D: 0ms, S: 100%, R: 5ms — near-instant on/off (key click = short noise burst at attack)
- **Modulation**: Rotary speaker simulation (Leslie) — slow (chorale) or fast (tremolo)
- **Rationale**: Organ tones are fundamentally additive. Instant envelope mimics tonewheel response. Leslie effect defines the organ character.

### Clavinet
- **Method**: Physical modeling or subtractive
- **Osc**: Pulse wave (25-35% width) or waveguide excitation
- **Filter**: BP centered 1-2 kHz, moderate resonance, or LP + HP combo
- **Envelope**: A: 0ms, D: 300-800ms, S: 0%, R: 100ms — fully percussive
- **Effects**: Phaser, wah (filter envelope or pedal)
- **Rationale**: Clav is a struck string with a narrow-band resonant body. Pulse wave approximates the string's spectrum. Percussive envelope matches the mechanical action.

---

## Plucks

### Karplus-Strong Pluck
- **Method**: Physical modeling (waveguide)
- **Excitation**: Short noise burst (1-5ms), or filtered impulse
- **Delay line**: Length = 1/frequency (in samples)
- **Feedback filter**: LP in feedback loop, cutoff 2-8 kHz — controls decay rate and brightness
- **Rationale**: Noise burst excites all frequencies; delay line selects resonant pitch; LP filter in feedback causes higher harmonics to decay faster than lower (natural string behavior).

### Filtered Pluck
- **Method**: Subtractive
- **Osc**: Saw wave
- **Filter**: LP 24dB/oct, high cutoff (4-8 kHz), resonance 15-25%
- **Filter envelope**: A: 0ms, D: 100-400ms, S: 0%, R: 100ms — percussive filter sweep
- **Amp envelope**: A: 0ms, D: 300-800ms, S: 0%, R: 200ms
- **Rationale**: Fast filter decay mimics the natural spectral decay of plucked strings where highs die faster than lows.

### FM Pluck
- **Method**: FM
- **C:M ratio**: 1:1 or 1:3
- **Mod index**: Envelope-controlled, fast decay (50-200ms) from high (I=5-8) to low (I=0.5)
- **Amp envelope**: Short to medium decay (200-600ms), no sustain
- **Rationale**: Rapid index decay = bright attack that quickly simplifies. At ratio 1:3, creates xylophone/marimba character.

---

## Drums

### Kick Drum
- **Method**: Subtractive (sine + pitch envelope)
- **Osc**: Sine wave
- **Pitch**: Start 150-400 Hz, sweep to 40-80 Hz in 20-60ms
- **Amp envelope**: A: 0ms, D: 5ms, S: 100%, R: 200-500ms
- **Optional**: Noise burst at attack (1-3ms) for beater click, light saturation
- **Rationale**: Pitch sweep creates percussive "thump." Sine provides clean sub energy. Noise burst adds realistic beater transient.

### Snare Drum
- **Method**: Subtractive (tone + noise)
- **Tone osc**: Sine or triangle at 150-250 Hz, short decay (50-100ms)
- **Noise**: White noise, BP filtered 1-5 kHz, decay 100-200ms
- **Mix**: 40-60% tone, 40-60% noise
- **Amp envelope**: A: 0ms, D: 100-200ms, S: 0%, R: 100ms
- **Rationale**: Snare = pitched membrane (tone) + snare wires (filtered noise). Mixing ratio sets "tuned" vs "noisy" character.

### Hi-Hat
- **Method**: Subtractive or FM
- **Subtractive**: White noise → HP filter at 6-10 kHz, or BP at 8-12 kHz
- **FM**: 6 operators at inharmonic ratios (e.g., 1:1.41, 1:1.73) → HP filter
- **Closed**: Decay 20-60ms. Open: Decay 200-500ms
- **Rationale**: Hi-hats are spectrally dense metallic sounds. HP-filtered noise approximates this. FM with irrational ratios more accurately models vibrating metal.

### Clap
- **Method**: Subtractive
- **Source**: Short white noise bursts (3-5 bursts, each 5-10ms, spaced 10-20ms apart)
- **Filter**: BP 800-2000 Hz
- **Reverb**: Short, bright room reverb (100-200ms)
- **Rationale**: Clap = multiple hands hitting slightly out of sync. Multiple noise bursts + room reverb recreates this micro-timing.

### Toms
- **Method**: Subtractive (sine + pitch envelope)
- **Osc**: Sine wave
- **Pitch**: Start at 2× target, sweep to target (100-300 Hz) in 30-60ms
- **Amp envelope**: A: 0ms, D: 200-500ms, S: 0%, R: 200ms
- **Rationale**: Similar to kick but higher pitch target and shorter pitch sweep. Tom character defined by pitch range: high (~300 Hz), mid (~200 Hz), low (~100 Hz).

---

## FX / Textures

### Riser
- **Method**: Any — white noise with rising HP filter, or saw with rising pitch
- **Noise riser**: White noise → HP filter sweeping from 200 Hz to 10 kHz over 2-8 bars
- **Pitch riser**: Saw oscillator, pitch sweeping up 1-2 octaves over 2-8 bars
- **Additions**: Increasing reverb, delay feedback, layered noise
- **Rationale**: Rising spectral content or pitch creates tension and anticipation.

### Impact
- **Method**: Subtractive
- **Source**: Layered noise burst + low sine with pitch drop
- **Noise**: Wide-band, very short (10-30ms)
- **Sub**: Sine starting 100-200 Hz, drop to 30-50 Hz in 50ms, long release (1-3s)
- **Effects**: Heavy reverb (large space, 3-5s decay)
- **Rationale**: Combines transient energy (noise) with sustained sub weight. Reverb fills the space after the impact.

### Drone / Atmosphere
- **Method**: Granular, wavetable, or layered subtractive
- **Sources**: Multiple slow-evolving layers at different pitches (fifths, octaves)
- **Modulation**: Very slow LFOs (0.01-0.1 Hz) on everything — filter, pitch, pan, level
- **Effects**: Long reverb (5-10s), delay with high feedback, chorus
- **Rationale**: Drones exist in slow time. Glacial modulation rates create evolving texture without obvious repetition. Multiple layers at consonant intervals add harmonic richness.
