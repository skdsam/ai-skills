---
name: ai-music-generation
description: Professional prompt engineering, structural orchestration, and post-production workflows for generative AI music platforms (Suno v3/v4, Udio, ElevenLabs Music, Stable Audio). Covers metatag architecture, lyrical prosody/syllable metering, genre fusion, vocal cueing, stem mastering, and artifact elimination.
---

# Generative AI Music Engineering & Production

A specialized skill for directing, structuring, and polishing musical compositions created with state-of-the-art AI music platforms (such as Suno v3.5/v4, Udio, ElevenLabs Music, and AudioCraft).

## 1. Structural Metatag Architecture

AI music models are steered through bracketed metatags indicating arrangement transitions, instrumentation, and energy shifts:

```text
[Style Prompt]: Melodic Synthwave, 1980s analog synthesizers, driving 4-on-the-floor kick, gated reverb snare, emotional minor lead, warm bassline, arpeggiated synth, nostalgic atmosphere, 120 BPM, Key of D Minor

[Intro]
(Atmospheric vinyl static, subtle low-pass filtered synth pad swells)
[Synth Arpeggio enters]

[Verse 1]
Midnight neon reflects across the street
Static whispers keeping steady beat
Shadows stretching out against the glass
Holding moments that were meant to pass

[Pre-Chorus]
(Snare roll builds, synth filter opens wide)
The frequency is rising high
A distant signal in the sky

[Chorus]
[Explosive Energy, Full Stereo Width, Female Lead Vocals with Harmony]
Run through the fire, illuminate the night
Catching every particle of light
No turning backwards into the cold
This is the story waiting to unfold!

[Post-Chorus]
[Lead Synth Hook, energetic rhythm]

[Verse 2]
Signals pulsing through the wired line
Every second locked in perfect time
Echoes fading down the boulevard
Looking forward, keeping down our guard

[Chorus]
[Maximum Climax, layered octave harmonies]
Run through the fire, illuminate the night
Catching every particle of light
No turning backwards into the cold
This is the story waiting to unfold!

[Bridge]
[Drums Drop Out, Solo Electric Piano & Ambient Reverb]
If the signal breaks away...
We will find another way...

[Drum Fill, High Pass Sweep]
[Drop]

[Guitar / Synth Solo]
[Virtuosic, expressive pitch bends, wide stereo delay]

[Outro]
[Gradual Fade, reverb decay, final synthesizer chord ringout]
Into the dawn...
Just illuminate...
[End]
```

---

## 2. Vocal Prosody & Syllable Matching Rules

One of the most frequent defects in AI-generated songs is awkward vocal cadence caused by mismatched syllable counts.

### Meter Calibration Matrix
- Every rhyming pair MUST have identical or balanced stressed syllable counts:
  - *Line A:* `Mid-night ne-on re-flects a-cross the street` (10 syllables, 4 stresses)
  - *Line B:* `Sta-tic whis-pers keep-ing stea-dy beat` (10 syllables, 4 stresses)
- Avoid cramming 14-syllable prose into an 8-beat measure.
- Punctuation directly affects delivery:
  - Ellipsis (`...`) forces breathing pause or sustained note.
  - Exclamation mark (`!`) prompts dynamic vocal projection and grit.
  - Commas (`,`) prompt micro-rests.

---

## 3. Style Prompt Engineering Taxonomy

Combine four core pillars in your style prompt:

1. **Sub-Genre & Core Groove**: e.g., `Nu-Disco`, `Liquid Drum & Bass`, `Cinematic Post-Rock`, `Progressive Metal`.
2. **Instrumentation Specifications**: e.g., `real live Fender Rhodes, Roland Juno-106, upright acoustic bass, crisp 909 hi-hats`.
3. **Vocal Direction**: e.g., `Soulful female vocal, soaring belting, intimate breathy close-mic, layered choir harmonies`.
4. **Mix & Production Aesthetics**: e.g., `Wide stereo mix, analog tape saturation, warm low-end punch, polished studio master, crisp transients`.

---

## 4. Post-Generation Stem Cleaning & Polishing

When using stem separation tools (Demucs / UVR5 / Lalal.ai):

1. **Vocal De-essing & Phase Alignment**: AI vocals often exhibit harsh sibilance at 6kHz - 8kHz. Apply a dynamic EQ notch of -3dB at 7.2kHz.
2. **High-Frequency Denoising**: Filter out robotic AI artifacts above 18kHz using a steep 24dB/oct low-pass filter.
3. **Bass Mono Lock**: Force all low frequencies below 120Hz to pure mono to prevent muddy phase cancellation in club and headphones.
4. **Master Limiter**: Set True Peak ceiling to `-1.0 dB` with target integrated loudness of `-14 LUFS`.
