# Modulation Matrix Reference

## Source / Destination / Amount Paradigm

Every modulation connection is defined by:
- **Source**: The signal that controls the modulation (envelope, LFO, performance input)
- **Destination**: The parameter being modulated (filter cutoff, pitch, amplitude, etc.)
- **Amount**: How much the source affects the destination (bipolar: negative inverts the modulation)

## Modulation Sources

### Envelopes (One-Shot Shapes)

| Source | Output Range | Character |
|---|---|---|
| Amp envelope | 0 → peak → sustain → 0 | Controls volume contour |
| Filter envelope | 0 → peak → sustain → 0 | Controls timbral contour |
| Mod envelope (free) | 0 → peak → sustain → 0 | Assignable to any parameter |
| Pitch envelope | 0 → peak → sustain → 0 | Transient pitch effects |

### LFOs (Repeating Shapes)

| Source | Typical Range | Character |
|---|---|---|
| LFO sine | -1 to +1 | Smooth, natural modulation |
| LFO triangle | -1 to +1 | Linear, slightly brighter than sine |
| LFO square | -1 or +1 | Switching, trills |
| LFO saw up | -1 to +1 ramp | Asymmetric sweep |
| LFO saw down | +1 to -1 ramp | Asymmetric sweep (reversed) |
| LFO S&H | Random steps | Random, electronic |
| LFO smoothed S&H | Random smooth | Organic drift |

### Performance Inputs

| Source | Range | Use |
|---|---|---|
| Velocity | 0-127 (normalized 0-1) | Dynamics, brightness per note |
| Key tracking | Low-C to high-C (normalized) | Pitch-dependent parameter scaling |
| Aftertouch | 0-127 (normalized 0-1) | Pressure-dependent expression |
| Mod wheel (CC1) | 0-127 (normalized 0-1) | Manual real-time control |
| Pitch bend | -1 to +1 | Pitch expression |
| Expression (CC11) | 0-127 | Volume/dynamics control |

### Special Sources

| Source | Character | Use |
|---|---|---|
| Random (per note) | New random value each note-on | Humanization, variation |
| Noise (continuous) | Continuous random | Analog drift emulation |
| Audio follower | Tracks amplitude of a signal | Cross-modulation, ducking |
| Sequencer/arpeggiator | Stepped pattern | Rhythmic parameter sequencing |

---

## Common Routing Patterns

### Essential Routings (Use in Most Patches)

| Source | → Destination | Amount | Purpose |
|---|---|---|---|
| Filter envelope | → Filter cutoff | +20-80% | Timbral contour — bright attack, mellow sustain |
| Velocity | → Filter cutoff | +10-40% | Harder playing = brighter sound |
| Velocity | → Amp envelope attack | -5-20% | Harder = faster attack |
| Key tracking | → Filter cutoff | +50-100% | Maintain timbre across keyboard |
| LFO (5-6 Hz) | → Pitch | ±5-30 cents | Vibrato |

### Character Routings (Shape the Sound's Identity)

| Source | → Destination | Amount | Purpose |
|---|---|---|---|
| LFO (0.2-1 Hz) | → Filter cutoff | ±200-2000 Hz | Timbral motion, "breathing" |
| LFO (0.1-0.3 Hz) | → Pitch (both oscs) | ±2-5 cents | Analog drift, organic feel |
| LFO (3-6 Hz) | → Amplitude | ±10-30% | Tremolo |
| LFO (0.5-2 Hz) | → Pulse width | ±10-30% | PWM — spectral animation |
| LFO (0.1-0.5 Hz) | → Wavetable position | ±20-50% | Spectral morphing |
| Mod envelope | → Pitch | +/- 1-12 semitones | Pitch transient (kicks, drops) |
| Mod envelope | → FM index | +50-100% | Bright attack, mellow sustain |

### Expression Routings (Performance Control)

| Source | → Destination | Amount | Purpose |
|---|---|---|---|
| Mod wheel | → LFO depth (vibrato) | 0-100% | Manual vibrato control |
| Mod wheel | → Filter cutoff | +20-60% | Manual brightness control |
| Aftertouch | → LFO depth (vibrato) | 0-50% | Pressure-sensitive vibrato |
| Aftertouch | → Filter cutoff | +10-30% | Pressure opens filter |
| Velocity | → Mod envelope amount | +20-80% | Harder = more dramatic transient |
| Pitch bend | → Pitch | ±2-12 semitones | Standard pitch expression |

---

## Advanced Modulation Techniques

### Cross-Modulation (Modulating Modulators)

- **LFO rate modulation**: Envelope → LFO rate = accelerating/decelerating modulation
- **LFO depth modulation**: Mod wheel → LFO depth = performance-controlled intensity
- **Envelope amount modulation**: Velocity → envelope mod amount = dynamic responsiveness

### Multi-Destination Modulation

Route a single source to multiple destinations for cohesive timbral changes:

```
Mod wheel →
  ├── Filter cutoff (+40%)     // Brighter
  ├── Resonance (+20%)         // More resonant peak
  ├── Distortion drive (+30%)  // Grittier
  └── LFO depth (+50%)         // More movement
```

This creates a single "intensity" control that coherently transforms the sound.

### Envelope Followers

Track the amplitude of one signal and use it to modulate another:

- **Sidechain**: Kick amplitude → pad volume (negative) = ducking
- **Spectral following**: Bass amplitude → reverb mix (negative) = clean bass, spacious sustain
- **Cross-synthesis**: Vocal amplitude → synth filter = synth responds to vocal dynamics

### Macro Controls

Map a single knob to multiple parameters with different amounts and polarities:

```
"Darkness" macro →
  ├── Filter cutoff (-60%)     // Lower cutoff
  ├── Resonance (+15%)         // Slight peak emphasis
  ├── HF damping (+30%)        // Reverb gets darker
  └── LFO rate (-20%)          // Slower modulation
```

### Randomization for Organic Character

- **Per-note random → pitch**: ±3-8 cents per note = analog oscillator instability
- **Per-note random → attack time**: ±5-20ms = natural articulation variation
- **Per-note random → filter cutoff**: ±5-10% = timbral variation
- **Per-note random → pan**: ±10-20% = natural spatial spread in ensemble

### Step Sequencer as Modulation Source

- **Filter cutoff sequence**: Rhythmic timbral pattern (acid bass)
- **Pitch sequence**: Arpeggio-like patterns without note input
- **Amplitude sequence**: Rhythmic gating patterns (trance gates)
- **Combined sequences**: Multiple parameters sequenced in parallel for complex rhythmic timbral patterns

---

## Amount Calibration Guide

### By Destination Type

**Pitch modulation amounts**:
- Subtle vibrato: ±5-15 cents
- Wide vibrato: ±20-50 cents
- Musical interval: ±100 cents (semitone), ±700 cents (fifth)
- Sound design: ±1200 cents+ (octave+)
- Pitch envelope transients: typically +200-1200 cents, fast decay

**Filter cutoff modulation amounts** (relative to base cutoff):
- Subtle motion: ±100-300 Hz
- Noticeable sweep: ±500-2000 Hz
- Dramatic sweep: ±2000-8000 Hz
- Full range: 20 Hz - 20 kHz

**Amplitude modulation amounts**:
- Subtle tremolo: ±10-20%
- Obvious tremolo: ±30-50%
- Gating: ±80-100%

**Pan modulation amounts**:
- Subtle widening: ±10-20%
- Auto-pan: ±50-100%

### By Context

- **Subtle/background sounds** (pads, ambient): Use lower amounts — modulation should be felt, not heard
- **Lead/foreground sounds**: Can use more obvious modulation — listener is focused on the sound
- **Rhythmic contexts**: Tempo-synced modulation should be pronounced enough to be rhythmically perceived
- **Sound design/FX**: Extreme amounts are appropriate — the modulation IS the sound
