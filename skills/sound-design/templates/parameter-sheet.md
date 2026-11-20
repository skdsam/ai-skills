# Parameter Sheet Template

Use this format for synth-agnostic patch documentation. Every value must have a paired rationale.

---

## Format

```markdown
## [Sound Name] — Parameter Sheet

### Signal Flow
[source] → [processing] → [processing] → [output]

### Oscillator Section

| Parameter | Value | Rationale |
|---|---|---|
| Waveform | | |
| Frequency / Note | | |
| Detune | | |
| Mix / Level | | |

### Filter Section

| Parameter | Value | Rationale |
|---|---|---|
| Type | | |
| Slope | | |
| Cutoff | | |
| Resonance (Q) | | |
| Key tracking | | |
| Envelope amount | | |

### Amplitude Envelope

| Stage | Time | Level | Rationale |
|---|---|---|---|
| Attack | | | |
| Decay | | | |
| Sustain | | | |
| Release | | | |

### Filter Envelope

| Stage | Time | Level | Rationale |
|---|---|---|---|
| Attack | | | |
| Decay | | | |
| Sustain | | | |
| Release | | | |

### Modulation

| Source | Destination | Amount | Rationale |
|---|---|---|---|
| | | | |

### Effects

| Effect | Parameter | Value | Rationale |
|---|---|---|---|
| | | | |
```

---

## Example: Warm Analog Pad

```markdown
## Warm Analog Pad — Parameter Sheet

### Signal Flow
Saw Osc × 2 (detuned) → LP Filter (12dB) → Amp Envelope → Chorus → Reverb → Output

### Oscillator Section

| Parameter | Value | Rationale |
|---|---|---|
| Osc 1 waveform | Sawtooth | Full harmonic series — richest starting material for subtractive |
| Osc 2 waveform | Sawtooth | Matched waveform for detuning thickness |
| Osc 1 frequency | As played | Tracks MIDI note |
| Osc 2 detune | +7 cents | Slow beating (~3 Hz at A440) creates warmth without pitch ambiguity |
| Osc mix | 50/50 | Equal blend maximizes beating effect |

### Filter Section

| Parameter | Value | Rationale |
|---|---|---|
| Type | Low-pass | Remove upper harmonics for warmth |
| Slope | 12 dB/oct | Gentle slope retains some brightness — softer than 24dB |
| Cutoff | 1200 Hz | Passes first ~3 harmonics at A220 — warm but not muffled |
| Resonance (Q) | 15% | Subtle emphasis at cutoff adds slight nasal character |
| Key tracking | 60% | Higher notes open filter slightly — prevents dullness in upper register |
| Envelope amount | +400 Hz | Gentle brightness swell during attack |

### Amplitude Envelope

| Stage | Time | Level | Rationale |
|---|---|---|---|
| Attack | 600 ms | → 1.0 | Slow fade-in — defines pad character, blends into mix |
| Decay | 400 ms | → 0.75 | Slight volume reduction after swell peak |
| Sustain | — | 0.75 | Sustained held notes at moderate level |
| Release | 2.0 s | → 0.0 | Long tail — pad lingers after release, fills harmonic gaps |

### Filter Envelope

| Stage | Time | Level | Rationale |
|---|---|---|---|
| Attack | 800 ms | → +400 Hz | Slower than amp attack — brightness follows volume swell |
| Decay | 1.0 s | → +100 Hz | Gradual return to base cutoff |
| Sustain | — | +100 Hz | Slight brightness above base in sustained notes |
| Release | 2.5 s | → 0 Hz | Filter closes during release — darkens as sound fades |

### Modulation

| Source | Destination | Amount | Rationale |
|---|---|---|---|
| LFO sine 0.3 Hz | Filter cutoff | ±200 Hz | Slow timbral breathing — adds organic movement |
| LFO sine 0.15 Hz | Osc 2 detune | ±3 cents | Drift in detuning amount — evolving character |
| Velocity | Filter cutoff | +0-300 Hz | Harder playing opens filter slightly — natural expression |

### Effects

| Effect | Parameter | Value | Rationale |
|---|---|---|---|
| Chorus | Rate | 0.8 Hz | Slow rate for subtle ensemble thickening |
| Chorus | Depth | 4 ms | Moderate depth — audible but not seasick |
| Chorus | Mix | 40% | Blended well with dry for width without excess |
| Reverb | Type | Hall | Large space suits pad's sustained character |
| Reverb | Decay | 3.0 s | Long tail extends pad into ambient space |
| Reverb | Pre-delay | 30 ms | Separates dry from wet — maintains definition |
| Reverb | Damping | 60% | Darker reverb tail — prevents harshness |
| Reverb | Mix | 35% | Spacious but source remains identifiable |
```

---

## Guidelines

1. **Every value needs a rationale** — never leave the rationale column empty
2. **Use absolute units** — Hz for frequency, ms/s for time, % for levels/amounts, cents for detuning
3. **Signal flow diagram first** — reader should understand architecture before details
4. **Group by function** — oscillators, filters, envelopes, modulation, effects
5. **Note key tracking and velocity** — these are often overlooked but critical for playability
6. **Mention what's NOT used** — if no effects, say "None — dry signal" with rationale
