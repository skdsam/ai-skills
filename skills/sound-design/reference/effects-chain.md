# Effects Chain Reference

## Signal Chain Order

Standard effects chain order, from first to last:

```
Source → EQ (corrective) → Compression → Distortion/Saturation →
Filter (creative) → Modulation FX → Delay → Reverb → EQ (tonal) → Limiter
```

### Why This Order Matters

1. **Corrective EQ first**: Remove problem frequencies before they affect downstream processing
2. **Compression before distortion**: Consistent levels into distortion prevent unpredictable clipping
3. **Distortion before filter**: Generate harmonics, then sculpt them (subtractive approach to distortion harmonics)
4. **Modulation before time-based**: Modulate the dry signal, then add space (avoids smearing modulation in reverb)
5. **Delay before reverb**: Delay repeats feed into reverb for depth (reverb on delay = spacious; delay on reverb = messy)
6. **Reverb last** (before final EQ): Creates spatial context for the processed signal

### Alternative Orders for Specific Effects

- **Reverb → distortion**: "Shoegaze" texture — distorting reverb tails creates massive walls of sound
- **Delay → filter**: Filtered delays darken with each repeat (dub delay)
- **Compression after reverb**: Brings up reverb tails, creates sustained ambience

---

## Reverb

### Reverb Types

| Type | Decay | Character | Use Case |
|---|---|---|---|
| Room | 0.2-0.6s | Tight, intimate | Drums, close sounds, natural placement |
| Chamber | 0.5-1.5s | Warm, smooth | Vocals, keys, general purpose |
| Hall | 1.5-4s | Spacious, grand | Pads, orchestral, cinematic |
| Cathedral | 4-10s | Vast, ethereal | Ambient, atmospheric |
| Plate | 1-3s | Bright, dense, metallic sheen | Vocals, snares, vintage character |
| Spring | 0.5-2s | "Boingy," metallic | Guitar, lo-fi, retro |

### Key Parameters

- **Decay time (RT60)**: Time for reverb to drop 60dB. Longer = larger/more reflective space
- **Pre-delay**: Gap before first reflections. 10-40ms separates dry from wet, maintaining clarity
- **Early reflections**: First bounces — define room shape and size perception
- **Damping (HF decay)**: Higher damping = higher frequencies decay faster = warmer, more natural reverb
- **Diffusion**: How quickly reflections spread. High = smooth wash; Low = discrete echoes
- **Mix (wet/dry)**: 10-30% typical for subtle space; 50-100% for ambient/atmospheric

### Perceptual Effects

- Reverb adds **depth** (distance from listener)
- Pre-delay > 30ms can push a sound "behind" other dry sounds
- LP-filtered reverb = warm, intimate space
- HP-filtered reverb (remove below 200-400 Hz) = prevents reverb from muddying the low end

---

## Delay

### Delay Types

| Type | Time | Character | Use Case |
|---|---|---|---|
| Slapback | 50-120ms | Rockabilly, doubling | Vocals, guitars, retro feel |
| Short | 100-300ms | Rhythmic texture | Leads, percussive elements |
| Quarter note | Tempo-synced | Rhythmic reinforcement | Melodic elements, trance leads |
| Dotted eighth | Tempo-synced | "The Edge" delay, bouncing | Guitar, melodic lines |
| Ping-pong | Any | Stereo bouncing | Width creation, space filling |
| Tape delay | Any | Warm, degrading repeats | Dub, lo-fi, vintage |

### Key Parameters

- **Time**: Delay between repeats. Tempo-synced for rhythmic; free for texture
- **Feedback**: Amount of output fed back to input. 0% = single repeat; 50% = ~6 audible repeats; >90% = infinite buildup (use carefully)
- **Filter in feedback**: LP filter (1-4 kHz) darkens each repeat — dub delay character
- **Mix**: 15-30% typical; higher for ambient/textural

---

## Distortion / Saturation

### Types

| Type | Character | Harmonic Content | Use Case |
|---|---|---|---|
| Soft clipping | Warm, gentle compression | Primarily even harmonics | Warming, thickening |
| Hard clipping | Aggressive, crunchy | Strong odd harmonics | Guitars, aggressive bass |
| Tape saturation | Warm, smooth compression | Even harmonics, gentle HF rolloff | Master warmth, analog feel |
| Tube saturation | Rich, complex | Even harmonics dominant | Vocals, bus warmth |
| Waveshaping | Variable, can be extreme | Depends on transfer function | Sound design, aggressive FX |
| Bitcrushing | Digital, lo-fi, crunchy | Aliasing artifacts | Lo-fi, retro, glitch |
| Foldback | Complex, metallic | Dense overtones | Industrial, aggressive synthesis |

### Key Parameters

- **Drive/amount**: How hard the signal hits the nonlinearity. More drive = more harmonics = more distortion
- **Tone/mix**: Post-distortion filtering and dry/wet blend
- **Input level**: Critical — distortion character changes dramatically with input level

### Perceptual Effects

- Light saturation adds warmth and presence without obvious distortion
- Saturation on sub-bass adds upper harmonics, making bass audible on small speakers
- Distortion compresses dynamics as a side effect

---

## Modulation Effects

### Chorus

- **Mechanism**: Short delay (5-30ms) modulated by slow LFO (0.5-3 Hz)
- **Depth**: Amount of delay time modulation (1-10ms variation)
- **Rate**: LFO speed — slower = gentler, faster = more obvious
- **Character**: Thickening, widening, ensemble-like
- **Use**: Pads, clean guitars, bass (subtle), string sounds

### Flanger

- **Mechanism**: Very short delay (0.5-5ms) modulated by LFO, with feedback
- **Feedback**: Creates resonant comb filter sweeps — "jet engine" character
- **Rate**: Typically 0.1-1 Hz for classic flanging
- **Character**: Metallic, sweeping, jet-like
- **Use**: Guitars, drums, sound design, transitions

### Phaser

- **Mechanism**: All-pass filters (4-12 stages) modulated by LFO, creating moving notches
- **Stages**: More stages = more notches = richer effect
- **Rate**: 0.1-2 Hz for classic phaser sweep
- **Feedback**: Deepens the notches, makes effect more pronounced
- **Character**: Sweeping, watery, organic
- **Use**: Keys (Rhodes phaser is classic), pads, guitars

### Tremolo

- **Mechanism**: LFO modulating amplitude
- **Rate**: 2-8 Hz for musical tremolo; tempo-synced for rhythmic
- **Depth**: 20-50% for subtle; 100% for full volume gating
- **Shape**: Sine = smooth; square = rhythmic gate; triangle = pulsing

### Ring Modulation (as effect)

- **Mechanism**: Multiplying signal with a carrier oscillator
- **Carrier frequency**: Fixed or slowly modulated
- **Character**: Metallic, robotic, bell-like sidebands
- **Use**: Sound design, sci-fi effects, metallic textures

---

## Dynamics

### Compression

| Setting | Character | Use Case |
|---|---|---|
| Ratio 2:1, slow attack/release | Gentle leveling | Bus compression, master |
| Ratio 4:1, medium attack/release | Moderate control | Vocals, bass, keys |
| Ratio 8:1+, fast attack | Heavy squashing | Parallel compression, drums |
| Ratio ∞:1 | Limiting | Peak control, loudness |

**Key Parameters**:
- **Threshold**: Level above which compression engages
- **Ratio**: Amount of gain reduction (2:1 = for every 2dB over threshold, output increases 1dB)
- **Attack**: How quickly compression engages. Fast (0.1-5ms) catches transients; slow (10-50ms) lets transients through
- **Release**: How quickly compression disengages. Fast (50-100ms) for transparent; slow (200-500ms) for pumping
- **Makeup gain**: Compensate for level reduction

### Sidechain Compression

- **External sidechain**: Compress one signal based on another's level (e.g., bass ducking to kick)
- **Filtered sidechain**: Compress based on specific frequency range (de-essing = sidechain on 4-8 kHz)
- **Rhythmic pumping**: Aggressive sidechain from kick drum → pad/bass creates EDM pumping effect

---

## EQ (as Effect)

### Creative EQ Applications

- **Telephone effect**: BP filter 300 Hz - 3 kHz, with resonant peaks
- **Radio effect**: Similar to telephone but slightly wider, with slight distortion
- **Lo-fi**: Aggressive LP at 4-6 kHz + HP at 200 Hz, with bit reduction
- **Presence boost**: +3-6 dB wide bell at 2-5 kHz for clarity and cut-through
- **Air**: +2-4 dB shelf above 10 kHz for sparkle and openness
- **Warmth**: +2-4 dB shelf below 300 Hz, with gentle LP rolloff above 8 kHz
- **Scoop**: Cut 400-800 Hz for "scooped" metal guitar/bass tone
