// ============================================================
// Sound Design Skill — SuperCollider Examples
// Each SynthDef is complete and runnable after s.boot
// ============================================================

s.boot;

// ------------------------------------------------------------
// 1. Subtractive Bass
// Two detuned saws through a resonant low-pass filter with
// envelope-controlled cutoff. Classic analog bass tone.
// ------------------------------------------------------------
(
SynthDef(\subBass, {
	|out=0, freq=55, amp=0.5, gate=1,
	 cutoff=600, res=0.2, fenvAmt=2000, fenvDec=0.25,
	 detune=0.008|

	var sig, fenv, env;

	// Two detuned sawtooths — beating creates analog thickness
	sig = Saw.ar(freq * [1 - detune, 1 + detune]).sum * 0.5;

	// Filter envelope: bright attack decaying to warm sustain
	fenv = EnvGen.kr(Env.adsr(0.001, fenvDec, 0.15, 0.1), gate) * fenvAmt;
	sig = RLPF.ar(sig, (cutoff + fenv).clip(20, 20000), res);

	// Amplitude envelope: fast attack, full sustain, quick release
	env = EnvGen.kr(Env.adsr(0.005, 0.15, 0.85, 0.05), gate, doneAction: 2);

	Out.ar(out, (sig * env * amp) ! 2);
}).add;
)

// Test: play a low A bass note
x = Synth(\subBass, [\freq, 55, \amp, 0.5]);
// Stop:
x.set(\gate, 0);


// ------------------------------------------------------------
// 2. FM Bell
// Carrier:Modulator ratio 1:1.41 (irrational) produces
// inharmonic partials characteristic of struck metal.
// Decaying mod index mimics natural spectral simplification.
// ------------------------------------------------------------
(
SynthDef(\fmBell, {
	|out=0, freq=440, amp=0.3, gate=1,
	 ratio=1.41, index=5, indexDecay=3.0|

	var modFreq, modEnv, modulator, carrier, env;

	modFreq = freq * ratio;

	// Mod index envelope: bright attack, long decay to near-sine
	modEnv = EnvGen.kr(Env.perc(0.001, indexDecay, 1, -6));
	modulator = SinOsc.ar(modFreq) * modFreq * index * modEnv;

	// Carrier at fundamental, frequency-modulated
	carrier = SinOsc.ar(freq + modulator);

	// Amplitude: percussive with long ring
	env = EnvGen.kr(Env.perc(0.001, indexDecay * 1.2, 1, -6), doneAction: 2);

	Out.ar(out, (carrier * env * amp) ! 2);
}).add;
)

// Test: bell at C5
Synth(\fmBell, [\freq, 523.25, \amp, 0.3]);


// ------------------------------------------------------------
// 3. Karplus-Strong Plucked String
// Short noise excitation into a filtered delay line.
// Delay length sets pitch; LP filter in feedback causes
// higher harmonics to decay faster (natural string behavior).
// ------------------------------------------------------------
(
SynthDef(\karplusPluck, {
	|out=0, freq=330, amp=0.5, decay=2.5, brightness=3000, exciteColor=5000|

	var excitation, sig;

	// Excitation: filtered noise burst (2ms) — "pick" brightness
	excitation = LPF.ar(WhiteNoise.ar, exciteColor);
	excitation = excitation * EnvGen.kr(Env.perc(0.001, 0.002));

	// Waveguide: comb filter with LP in feedback path
	sig = CombC.ar(excitation, 0.05, freq.reciprocal, decay);
	sig = LPF.ar(sig, brightness);

	// Clean amplitude envelope to avoid clicks at end
	sig = sig * EnvGen.kr(Env.linen(0, decay * 0.9, decay * 0.1), doneAction: 2);

	Out.ar(out, (sig * amp) ! 2);
}).add;
)

// Test: plucked E4
Synth(\karplusPluck, [\freq, 329.63, \brightness, 4000, \decay, 3]);


// ------------------------------------------------------------
// 4. Supersaw Pad
// Seven detuned sawtooths spread in stereo through a gentle
// low-pass filter with slow attack. Chorus-like density from
// the detuned stack. Long reverb for spaciousness.
// ------------------------------------------------------------
(
SynthDef(\supersawPad, {
	|out=0, freq=220, amp=0.3, gate=1,
	 cutoff=2000, detune=0.015, reverbMix=0.4|

	var detuneFactors, sig, env, lfo;

	// Seven detuned saws — spread from -detune to +detune
	detuneFactors = Array.linrand(7, 1 - detune, 1 + detune);
	sig = Saw.ar(freq * detuneFactors);

	// Stereo spread: pan voices across the stereo field
	sig = Splay.ar(sig, spread: 0.8);

	// Slow LFO on filter for gentle timbral movement
	lfo = SinOsc.kr(0.25) * 300;
	sig = RLPF.ar(sig, (cutoff + lfo).clip(20, 20000), 0.4);

	// Pad envelope: slow attack, long release
	env = EnvGen.kr(Env.adsr(0.8, 0.5, 0.7, 2.5, curve: 2), gate, doneAction: 2);

	// Reverb
	sig = FreeVerb2.ar(sig[0], sig[1], mix: reverbMix, room: 0.85, damp: 0.6);

	Out.ar(out, sig * env * amp);
}).add;
)

// Test: pad chord (play multiple)
x = Synth(\supersawPad, [\freq, 220, \amp, 0.25]);
y = Synth(\supersawPad, [\freq, 277.18, \amp, 0.25]);
z = Synth(\supersawPad, [\freq, 329.63, \amp, 0.25]);
// Stop all:
[x, y, z].do(_.set(\gate, 0));


// ------------------------------------------------------------
// 5. 808 Kick
// Sine oscillator with pitch envelope (click → boom).
// Pitch starts high and sweeps down exponentially.
// Optional noise burst for beater transient.
// Optional distortion for audibility on small speakers.
// ------------------------------------------------------------
(
SynthDef(\kick808, {
	|out=0, amp=0.7,
	 startFreq=300, endFreq=45, pitchDecay=0.04,
	 clickLevel=0.3, clickFreq=3000,
	 decayTime=0.8, drive=1.5|

	var body, click, sig, pitchEnv, ampEnv;

	// Pitch envelope: exponential drop from startFreq to endFreq
	pitchEnv = XLine.kr(startFreq, endFreq, pitchDecay);
	body = SinOsc.ar(pitchEnv);

	// Beater click: short filtered noise
	click = LPF.ar(WhiteNoise.ar, clickFreq);
	click = click * EnvGen.kr(Env.perc(0.001, 0.008)) * clickLevel;

	sig = body + click;

	// Soft saturation for harmonic content
	sig = (sig * drive).tanh;

	// Amplitude envelope: punchy attack, controlled decay
	ampEnv = EnvGen.kr(Env.perc(0.001, decayTime, 1, -6), doneAction: 2);

	Out.ar(out, (sig * ampEnv * amp) ! 2);
}).add;
)

// Test: 808 kick
Synth(\kick808);
// Boomy variant:
Synth(\kick808, [\startFreq, 200, \endFreq, 35, \decayTime, 1.5]);


// ------------------------------------------------------------
// 6. Granular Texture
// Granular synthesis using GrainBuf with a noise buffer.
// Randomized grain parameters create evolving, atmospheric
// texture. Dense grains with pitch scatter produce clouds.
// ------------------------------------------------------------
(
SynthDef(\granularTexture, {
	|out=0, amp=0.3, gate=1,
	 grainRate=20, grainDur=0.04, pitchCenter=1.0, pitchSpread=0.3,
	 reverbMix=0.6|

	var buf, trig, sig, env, pan;

	// Create noise buffer for granulation source
	buf = LocalBuf(SampleRate.ir * 0.5, 1);
	BufWr.ar(WhiteNoise.ar, buf, Phasor.ar(0, 1, 0, BufFrames.kr(buf)));

	// Grain trigger and randomized parameters
	trig = Impulse.kr(grainRate);
	pan = TRand.kr(-0.8, 0.8, trig);         // random pan per grain
	sig = GrainBuf.ar(
		numChannels: 2,
		trigger: trig,
		dur: grainDur,
		sndbuf: buf,
		rate: pitchCenter + TRand.kr(pitchSpread.neg, pitchSpread, trig),
		pos: TRand.kr(0, 1, trig),             // random buffer position
		pan: pan
	);

	// Slow amplitude envelope
	env = EnvGen.kr(Env.adsr(2.0, 1.0, 0.6, 3.0), gate, doneAction: 2);

	// Reverb for spaciousness
	sig = FreeVerb2.ar(sig[0], sig[1], mix: reverbMix, room: 0.9, damp: 0.7);

	Out.ar(out, sig * env * amp);
}).add;
)

// Test: evolving texture
x = Synth(\granularTexture, [\grainRate, 25, \grainDur, 0.05, \pitchSpread, 0.4]);
// Stop:
x.set(\gate, 0);
