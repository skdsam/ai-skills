# Psychoacoustics Reference

## Timbre Perception

Timbre is the quality that distinguishes two sounds of the same pitch and loudness. It is determined by:

1. **Spectral envelope**: The shape of energy distribution across frequencies. A sound with more high-frequency energy is perceived as "bright"; less high-frequency energy as "dark" or "warm."
2. **Temporal envelope**: How the sound's amplitude and spectrum evolve over time. The first 50ms (attack transient) is critical for identification.
3. **Spectral flux**: How rapidly the spectrum changes. Static spectra sound "synthetic"; evolving spectra sound "natural."
4. **Inharmonicity**: Deviation from perfect harmonic ratios. Slight inharmonicity = "warm" or "alive." Strong inharmonicity = "metallic" or "bell-like."

### Spectral Centroid and Brightness

The spectral centroid is the "center of mass" of the spectrum — the average frequency weighted by amplitude. It is the primary correlate of perceived brightness.

- **Low centroid** (200-800 Hz): Dark, warm, muffled — typical of basses, filtered pads
- **Medium centroid** (800-3000 Hz): Balanced, present — typical of voices, many leads
- **High centroid** (3000-8000 Hz): Bright, cutting, brilliant — typical of bells, cymbals, bright leads

### Spectral Tilt

The rate at which harmonic amplitudes decrease with frequency:
- **Steep rolloff** (-12 dB/oct or more): Mellow, soft — flute, sine-like
- **Moderate rolloff** (-6 dB/oct): Natural, balanced — voice, most acoustic instruments
- **Shallow rolloff** (-3 dB/oct or less): Bright, harsh — brass, distorted guitar
- **Rising spectrum**: Harsh, piercing — rarely musical on its own

## Harmonic Series

The harmonic series is the foundation of pitched sound. For a fundamental f₀:

| Harmonic | Frequency | Interval from f₀ | Character Contribution |
|---|---|---|---|
| 1st (f₀) | f₀ | Unison | Fundamental pitch |
| 2nd | 2f₀ | Octave | Fullness, warmth |
| 3rd | 3f₀ | Octave + fifth | Power, clarity |
| 4th | 4f₀ | 2 octaves | Warmth (even harmonic) |
| 5th | 5f₀ | 2 oct + major 3rd | Presence, sweetness |
| 6th | 6f₀ | 2 oct + fifth | Brightness |
| 7th | 7f₀ | ~2 oct + minor 7th | Edge, tension (odd harmonic) |
| 8th | 8f₀ | 3 octaves | Brilliance |
| 9th+ | 9f₀+ | Higher intervals | Increasing brightness/harshness |

### Even vs. Odd Harmonics

- **Even harmonics** (2, 4, 6, 8...): Associated with warmth, fullness. Tube amplifiers and tape saturation emphasize even harmonics, which is why they sound "warm."
- **Odd harmonics** (3, 5, 7, 9...): Associated with hollowness (at low levels) or harshness (at high levels). Square and triangle waves contain only odd harmonics. Transistor clipping emphasizes odd harmonics.

## Formants

Formants are resonant peaks in the spectral envelope that remain at fixed frequencies regardless of the fundamental pitch. They define vowel sounds and give instruments their characteristic "body."

### Vowel Formant Table

| Vowel | F1 (Hz) | F2 (Hz) | F3 (Hz) | Description |
|---|---|---|---|---|
| /a/ (father) | 730 | 1090 | 2440 | Open, bright |
| /e/ (bet) | 530 | 1840 | 2480 | Mid-front |
| /i/ (beet) | 270 | 2290 | 3010 | Closed, nasal |
| /o/ (boat) | 570 | 840 | 2410 | Rounded, dark |
| /u/ (boot) | 300 | 870 | 2240 | Closed, round |
| /æ/ (bat) | 660 | 1720 | 2410 | Open front |
| /ɜ/ (bird) | 500 | 1500 | 2500 | Central |

### Applying Formants in Synthesis

- Use **two or three bandpass filters** (or resonant peaks) at formant frequencies
- Q of ~5-15 for each formant band
- Morphing between vowels: crossfade the filter frequencies between vowel targets
- Parallel BP filters on a harmonically rich source (saw) = vocal-like sounds

### Instrument Body Resonances

Like vowels, acoustic instrument bodies have characteristic formant regions:
- **Acoustic guitar body**: ~100 Hz, ~200 Hz, ~400 Hz
- **Violin body**: ~280 Hz, ~500 Hz, ~700 Hz
- **Human voice (singer's formant)**: ~2500-3500 Hz — the "ring" that cuts through an orchestra

## Spectral Masking

When two sounds have energy in the same frequency region, the louder one can render the quieter one inaudible.

### Critical Bands

The ear analyzes sound in approximately 24 critical bands (Bark scale). Two tones within the same critical band interact — they can mask each other or create roughness.

| Frequency Region | Critical Bandwidth | Implication |
|---|---|---|
| 100 Hz | ~100 Hz | Low frequencies interact over wide range |
| 500 Hz | ~100 Hz | Moderate bandwidth |
| 1000 Hz | ~160 Hz | |
| 2000 Hz | ~300 Hz | |
| 5000 Hz | ~600 Hz | High frequencies — wider band, less precise pitch |
| 10000 Hz | ~1300 Hz | Very wide — individual tones hard to distinguish |

### Implications for Sound Design

- **Avoid spectral overlap** between layered sounds that must be separately perceived
- **Use filtering** to carve frequency "slots" for each element in a mix
- **Detuned unison** within a critical band creates roughness/warmth
- **Detuning beyond** a critical band creates distinct perceived tones
- A sound can be "masked" by nearby frequencies up to ~10-15 dB louder

## Roughness and Beating

When two frequencies are close together:

| Frequency Difference | Perceptual Effect |
|---|---|
| 0 Hz | Unison — single tone |
| 0.5-4 Hz | Slow beating — pleasant, "warm" |
| 4-15 Hz | Fast beating — "vibrato-like" |
| 15-30 Hz | Roughness — tense, dissonant sensation |
| 30 Hz - critical bandwidth | Maximum roughness — harsh, grating |
| > critical bandwidth | Two separate tones — roughness disappears |

### Design Applications

- **Unison detune** (2-8 cents, ~1-4 Hz beating): Thickening, warmth
- **Wider detune** (10-30 cents, ~5-15 Hz): Chorus effect, broader sound
- **Very wide detune** (30-50+ cents): Aggressive, dissonant tension (industrial, EDM)
- **Consonant intervals** (octave, fifth): Reinforce harmonics without roughness

## Equal-Loudness Contours (Fletcher-Munson)

Human hearing is not equally sensitive to all frequencies:

- **Most sensitive**: 2-5 kHz (ear canal resonance, speech frequencies)
- **Less sensitive**: Below 200 Hz and above 10 kHz
- **At low volumes**: Bass and treble seem to disappear (need boosting)
- **At high volumes**: Response flattens — bass and treble more audible

### Implications for Sound Design

- Bass sounds need more energy to be perceived as "equally loud" as midrange sounds
- Presence/intelligibility peak at 2-5 kHz — sounds with energy here cut through a mix
- The "smiley face" EQ curve (boost bass and treble) compensates for Fletcher-Munson at moderate volumes
- Sub-bass (< 60 Hz) is felt more than heard — often needs harmonics added (saturation) for audibility on small speakers
- Excessive energy at 2-5 kHz causes listening fatigue — use the range carefully

## Spatial Perception

### Frequency and Spatialization

- **Low frequencies** (< 300 Hz): Hard to localize. Spatial processing less effective. Keep centered.
- **Mid frequencies** (300-5000 Hz): Well-localized. Panning and spatial effects most effective.
- **High frequencies** (> 5000 Hz): Localized by amplitude/arrival time. Can create sense of "air" and width.

### Precedence Effect (Haas Effect)

A delayed copy of a sound (1-30ms) fused with the original is perceived as a single wider source located toward the earlier arrival. The delay adds spaciousness without perceived echo.

- **1-5ms delay**: Subtle widening
- **5-15ms delay**: Noticeable spaciousness (without distinct echo)
- **15-30ms delay**: Borderline — may be heard as echo
- **>30ms**: Distinct echo
