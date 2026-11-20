---
name: music-composition-producer
description: End-to-end music composition, MIDI arrangement, harmonic theory, multi-track production, sound design, and audio mastering (inspired by owoevan-dev/music-skill and professional DAW practices). Covers note-by-note sequencing, chord progressions, arrangement architecture, soundfont/synth routing, stem mixing, and mastering to -14 LUFS.
---

# Music Composition & Audio Production

An expert music producer and composition engine for creating, arranging, and polishing original multi-track musical pieces across electronic, orchestral, cinematic, ambient, chiptune, and acoustic genres.

## Musical Theory & Harmonic Architecture

### 1. Scales & Emotional Tonality
- **Major (Ionian)**: Uplifting, triumphant, bright (`[0, 2, 4, 5, 7, 9, 11]`)
- **Natural Minor (Aeolian)**: Emotional, serious, narrative (`[0, 2, 3, 5, 7, 8, 10]`)
- **Dorian**: Cyberpunk, medieval, noble melancholic groove (`[0, 2, 3, 5, 7, 9, 10]`)
- **Mixolydian**: Classic rock, heroic quest, energetic triumph (`[0, 2, 4, 5, 7, 9, 10]`)
- **Lydian**: Sci-fi, wonder, ethereal floating (`[0, 2, 4, 6, 7, 9, 11]`)

### 2. S-Tier Chord Progressions
- **Epic / Cinematic Minor**: `i - VI - III - VII` (e.g., Am - F - C - G)
- **Royal Road (J-Pop / Anime / Adventure)**: `IV - V - iii - vi` (e.g., Fmaj7 - G7 - Em7 - Am)
- **Andalusian Cadence**: `i - VII - VI - V` (e.g., Am - G - F - E)
- **Neo-Soul / Lo-Fi**: `ii9 - V13 - Imaj9 - VI7` (e.g., Dm9 - G13 - Cmaj9 - A7)
- **Dark Synthwave**: `i - v - VI - iv` (e.g., Dm - Am - Bb - Gm)

---

## 3. Song Structure & Arrangement Blueprint

```text
Time / Bars:
[00-08] INTRO       Atmosphere, theme motif, filtered drums or pad
[08-24] VERSE 1     Groove enters, bassline, rhythmic foundation established
[24-32] PRE-CHORUS  Harmonic tension builds, snare roll/riser, filter opens
[32-48] CHORUS      Full frequency spectrum, primary melodic hook, kick/bass punch
[48-64] VERSE 2     Variation added: counter-melody, syncopated percussion
[64-72] CHORUS 2    Maximum energy chorus with vocal/lead layers
[72-88] BRIDGE/SOLO Key modulation or breakdown, harmonic departure
[88-104] FINAL DROP Climax, all layers firing with octave accents
[104-112] OUTRO     Theme motif resolves, reverb wash, decay
```

---

## 4. Multi-Track Layering & Voice Leading

1. **Bass / Sub (20Hz - 150Hz)**: Root notes locked to kick drum rhythm. Mono centered. Keep low-end clean.
2. **Harmonic Rhythm (150Hz - 2kHz)**: Piano, electric guitar, synth pads, or string quartet playing 3-to-4 note voicings. Panned slightly stereo (20-40% L/R).
3. **Primary Lead / Vocal Hook (1kHz - 8kHz)**: The memorable earworm. Uses call-and-response phrasing with 1-bar breath pauses.
4. **Counter-Melody & Arpeggios**: Secondary ostinato lines filling rhythmic gaps left by the primary lead.
5. **Drums & Percussion**:
   - Kick (60Hz punch, 3kHz transient click)
   - Snare/Clap (200Hz body, 4-7kHz snap)
   - Hi-Hats / Shakers (staggered velocity 60-110 for humanized groove, high-passed at 500Hz)

---

## 5. Programmatic MIDI & Python Generation

Using `mido` or standard MIDI structures:

```python
import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage

def create_song_project(bpm=120, key_root=60): # 60 = Middle C
    mid = MidiFile()
    tempo_track = MidiTrack()
    mid.tracks.append(tempo_track)
    tempo_track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm)))
    
    # Track 1: Bass
    bass_track = MidiTrack()
    mid.tracks.append(bass_track)
    bass_track.append(MetaMessage('track_name', name='Bass'))
    
    # Track 2: Chords
    chords_track = MidiTrack()
    mid.tracks.append(chords_track)
    chords_track.append(MetaMessage('track_name', name='Chords'))
    
    # Track 3: Lead
    lead_track = MidiTrack()
    mid.tracks.append(lead_track)
    lead_track.append(MetaMessage('track_name', name='Lead Hook'))
    
    return mid
```

---

## 6. Mixing & Mastering Specifications

### Frequency Cleaning Table
- **Low-Cut (High-Pass)**: Filter all non-bass tracks at 80Hz - 100Hz to eliminate mud.
- **200Hz - 400Hz**: Dip by 1.5 - 3dB on pads and guitars to declutter the boxy midrange.
- **3kHz - 5kHz**: Presence boost on lead elements for clarity.
- **10kHz - 16kHz**: High shelf (+1.5dB) for "air" and studio sheen.

### Target Loudness Standards
- **Streaming Platforms (Spotify, Apple, YouTube)**: `-14 LUFS` Integrated, `-1.0 dB True Peak` max ceiling.
- **Club / EDM Masters**: `-9 to -7 LUFS` Integrated.
- **Games & Soundtracks**: `-16 to -18 LUFS` to leave headroom for sound effects (SFX) and voice dialogue.
