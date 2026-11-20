# Synthesis Types Reference

## 1. Subtractive Synthesis

**Principle**: Start with a harmonically rich waveform (saw, square, pulse, noise) and remove frequencies with filters.

**Key Parameters**:
- Oscillator waveform (determines initial harmonic content)
- Filter type (LP, HP, BP, notch), cutoff frequency, resonance
- Filter envelope amount and ADSR
- Oscillator mix, detuning, sub-oscillator

**Excels At**: Warm analog basses, classic leads, brass-like sounds, pads with filter sweeps.

**Limitations**: Difficult to produce truly inharmonic spectra (bells, metallic sounds). Fundamentally limited to sculpting existing harmonics — cannot add new frequency content above the source.

**Critical Relationships**:
- Saw wave contains all harmonics at 1/n amplitude — richest starting point for subtractive
- Square wave contains only odd harmonics — hollow character, good for woodwind-like sounds
- Pulse width modulation varies odd/even harmonic balance dynamically
- Filter resonance boosts energy at cutoff, creating formant-like peaks
- Key tracking on filter cutoff maintains timbral consistency across pitch range

## 2. FM Synthesis (Frequency Modulation)

**Principle**: One oscillator (modulator) modulates the frequency of another (carrier). The modulation creates sidebands at carrier ± n*modulator frequencies.

**Key Parameters**:
- Carrier frequency (C) — determines perceived pitch
- Modulator frequency (M) — C:M ratio determines harmonic vs. inharmonic spectrum
- Modulation index (I = mod_depth / mod_freq) — controls number of significant sidebands
- Operator envelopes — time-varying index creates timbral evolution

**Excels At**: Bells, electric pianos (DX7), metallic sounds, plucks, basses with complex overtones, brass.

**Limitations**: Precise timbral control is difficult — small ratio changes produce large spectral shifts. Mapping from parameters to perceptual result is non-intuitive.

**Critical Relationships**:
- Integer C:M ratios → harmonic spectra (1:1 = saw-like, 1:2 = square-like)
- Non-integer ratios → inharmonic/metallic spectra (1:1.41 = bell-like)
- Modulation index controls spectral brightness: I<1 (few sidebands, mellow), I>5 (many sidebands, bright/harsh)
- Time-varying index via envelope → attack brightness that decays to simpler tone (natural instrument behavior)
- Multiple operators in algorithms allow complex spectral structures (stacked, parallel, feedback)

## 3. Additive Synthesis

**Principle**: Build a sound by summing individual sinusoidal partials, each with independent frequency, amplitude, and phase control.

**Key Parameters**:
- Number of partials (typically 16-256)
- Frequency ratios (harmonic series for tonal, arbitrary for inharmonic)
- Individual amplitude envelopes per partial
- Phase relationships (mostly irrelevant perceptually for >3 partials)

**Excels At**: Organ tones, precise spectral control, morphing between timbres, resynthesis of analyzed sounds, vocal formants.

**Limitations**: Computationally expensive for rich timbres. Tedious to program without analysis/resynthesis tools. Static additive sounds lack the micro-variations that make subtractive sound "alive."

**Critical Relationships**:
- Harmonic partials at n*f0 with 1/n amplitude → approximates sawtooth
- Odd harmonics only at (2n-1)*f0 → approximates square wave
- Formants = amplitude peaks across partial groups at fixed frequencies → vowel sounds
- Slight random detuning of partials adds organic quality
- Independent partial envelopes enable spectral evolution impossible with other methods

## 4. Wavetable Synthesis

**Principle**: Store single-cycle waveforms in a table and read through them. Morph between different wavetables for timbral evolution.

**Key Parameters**:
- Wavetable selection (waveform snapshots)
- Table position / morph index (which waveform in the set)
- Modulation of table position (LFO, envelope → creates spectral morphing)
- Standard subtractive post-processing (filter, envelope)

**Excels At**: Evolving pads, complex lead sounds, digital basses, timbres that morph between distinct characters.

**Limitations**: Quality depends on wavetable content. Aliasing can occur at high frequencies without bandlimiting. Less intuitive than subtractive for simple sounds.

**Critical Relationships**:
- Slow LFO on table position → gentle spectral evolution (pads)
- Envelope on table position → attack-bright / sustain-mellow (natural decay modeling)
- Each wavetable frame is effectively an additive spectrum snapshot
- Post-filtering wavetable output combines both synthesis approaches
- Frame count affects morph smoothness — more frames = smoother transitions

## 5. Granular Synthesis

**Principle**: Break audio into tiny grains (1-100ms) and recombine them with independent control over each grain's pitch, position, density, duration, and envelope.

**Key Parameters**:
- Grain size (1-100ms) — smaller = more textural, larger = more pitched
- Grain density (grains/second) — sparse = rhythmic, dense = continuous
- Pitch randomization — 0 = tonal, high = textural/noise-like
- Position + position randomization (for sample-based granular)
- Grain envelope shape (Gaussian, Hanning, triangular)

**Excels At**: Atmospheric textures, time-stretching, pitch-shifting, soundscapes, transforming any source into abstract textures.

**Limitations**: Less suited for precise pitched sounds. CPU-intensive at high densities. Requires source material (sample-based) or careful oscillator grain design (synthesis-based).

**Critical Relationships**:
- Grain size < 10ms → frequency domain artifacts, buzzy/harsh
- Grain size 20-50ms → sweet spot for pitched granular
- Grain size > 50ms → more recognizable source character
- Density * grain_size ≈ overlap factor — overlap > 4 for smooth output
- Gaussian grain envelope minimizes spectral artifacts at grain boundaries

## 6. Physical Modeling

**Principle**: Simulate the physics of sound-producing mechanisms using waveguides (traveling waves in tubes/strings) or modal synthesis (resonant modes of vibrating bodies).

**Key Parameters**:
- Excitation signal (impulse, noise burst, bow pressure) — initial energy
- Delay line length (waveguide) — determines pitch
- Damping/absorption — controls decay and timbral evolution
- Body resonance — formant structure of resonating body
- Nonlinear elements — for bowing, lip reed, etc.

**Excels At**: Realistic strings (Karplus-Strong), wind instruments, percussion, bowed sounds, plucked sounds. Naturally responsive to velocity and articulation.

**Limitations**: Difficult to create sounds that don't exist in the physical world. Parameter tuning requires understanding of the physics being modeled.

**Critical Relationships**:
- Karplus-Strong: short noise burst → delay line with LP filter in feedback = plucked string
- Delay line length = 1/frequency (samples = sample_rate / freq)
- Filter in feedback loop controls decay rate and spectral evolution
- Brighter excitation noise → brighter initial attack (like hard pick vs. soft finger)
- Shorter excitation → more percussive; longer → more bowed/sustained

## 7. AM Synthesis (Amplitude Modulation) / Ring Modulation

**Principle**: Multiply two signals together. AM preserves the carrier; ring mod produces only sum and difference frequencies.

**Key Parameters**:
- Carrier frequency
- Modulator frequency
- Modulation depth (0-1 for AM, always ±1 for ring mod)
- Modulator waveform

**Excels At**: Metallic timbres, tremolo (sub-audio rates), robotic/vocoder effects, adding inharmonic content to existing sounds.

**Limitations**: Limited timbral palette on its own. Often used as a modifier rather than primary synthesis. Sum/difference frequencies can sound dissonant.

**Critical Relationships**:
- Modulator < 20 Hz → tremolo (amplitude variation)
- Modulator > 20 Hz → audible sidebands (new frequencies)
- Harmonic ratios (1:2, 2:3) → consonant sidebands
- Inharmonic ratios → metallic/dissonant character
- AM = ring mod + dry carrier; ring mod is more extreme

## 8. Phase Distortion Synthesis

**Principle**: Read through a sine wave lookup table using a non-linear phase function, warping the waveform shape by distorting the readout speed.

**Key Parameters**:
- Phase distortion function shape (cosine window, resonant peak, etc.)
- Distortion amount (0 = pure sine, max = complex waveform)
- Distortion envelope — time-varying distortion mimics filter sweeps
- Multiple PD oscillators for complex timbres

**Excels At**: Bright digital timbres, sounds reminiscent of CZ-series synths, unique timbres not easily achieved with other methods.

**Limitations**: Somewhat obscure — less tooling and preset support. Timbral palette has a distinctive "digital" character that may not suit all contexts.

**Critical Relationships**:
- Cosine distortion function → resonant peak that mimics filter resonance
- Increasing distortion amount → adding harmonics (similar to opening a filter)
- Envelope on distortion amount → time-varying brightness (like filter envelope)
- Two PD oscillators with different functions → rich harmonic interactions
- Related to waveshaping but operates on phase rather than amplitude
