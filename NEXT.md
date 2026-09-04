# NEXT — what is the object if the substrate coordinates move?

Gate 7 separated four questions that had been getting mixed together:

```text
statistics       which generators exist?
timing           how are they coupled?
efference        which side issued the action?
consequence      which generators deserve scarce routing?
```

The next problem is more basic.

A memory or recurring computation should not have to mean "these exact neuron indices have these exact values." Real networks can drift, remap, recruit overlapping cells, and express memories as trajectories as well as static population states.

So Gate 8 asks:

> **What should count as the same internal object when its physical realization changes?**

This is the mathematically cleaner version of the attractor / engram / signal-flow intuition.

## Important terminology fence

Do not use `engram` and `attractor` as synonyms.

- an **engram** is a physical memory trace / ensemble / plastic substrate that helps make later recall possible;
- an **attractor** is a dynamical object: a fixed point, limit cycle, manifold, or other region/trajectory toward which dynamics return;
- an engram can bias a circuit so that a cue drives activity into a familiar attractor or trajectory, but the two words describe different levels.

Likewise, do not call every internal object a `frequency object`. Frequency may be one coordinate of a dynamical fingerprint. Fixed points have no oscillation at all, and two different processes can share the same dominant frequency.

The strongest candidate definition is therefore not a stored vector but an **equivalence class of trajectories and intervention responses** that remains recognizable when implementation coordinates change.

## Gate 8A — a point in time is not always a state

Start with the simplest WidePresent / MovingTarget attack.

Construct trajectories that share the same instantaneous scalar observation but have different hidden dynamical state:

```text
trajectory A: crossing zero while moving upward
trajectory B: crossing zero while moving downward
```

At the crossing:

```text
y(t) = 0
```

for both.

A point observer cannot know which future follows. A short temporal window can:

```text
[y(t-k), ..., y(t)]
```

The gate should compare:

1. instantaneous observation;
2. same number of samples shuffled in time;
3. causal ordered window;
4. active poke plus ordered window;
5. oracle hidden velocity / phase.

This would give `WidePresent` a precise job: **a present can be a trajectory fragment, not a frozen frame.**

Kill the claim if unordered history performs equally well.

## Gate 8B — same dynamics, different physical coordinates

Take several small dynamical systems and embed each one into many regenerated substrate coordinate systems:

```text
latent dynamics z(t)
       ↓ random permutation / orthogonal mix
physical state x(t)
```

The identity test must happen across remappings never seen together during calibration.

Required attackers:

- exact coordinate overlap / nearest stored state;
- PCA subspace similarity;
- dominant-frequency-only fingerprint;
- autocorrelation / power-spectrum fingerprint;
- intervention-response fingerprint;
- combined dynamical fingerprint;
- oracle latent identity.

The desired invariant is not "which neurons fired?" but something closer to:

```text
object address = {
    return dynamics,
    response latency,
    decay / persistence,
    oscillatory modes if present,
    transition probabilities,
    controllability,
    consequence
}
```

If a random permutation of the substrate destroys identity, the object definition is too coordinate-bound.

## Gate 8C — earn the word attractor

Only after 8A/8B should the repo introduce a genuinely nonlinear recurrent system with multiple basins.

Requirements:

- several initial states converge to the same basin / recurring trajectory;
- a cue can reactivate that basin after silence;
- perturbations can measure return time, escape probability, and transitions to other basins;
- the same basin is re-embedded under different substrate permutations;
- identity is judged from dynamics and intervention response, not neuron IDs.

Then a useful statement would be:

> **The persistent object is an equivalence class of recoverable dynamics over a changing substrate, not a frozen population vector.**

That would still not make it a biological engram. It would make the artificial architecture stop confusing implementation coordinates with dynamical identity.

## Frequency attacker

The frequency intuition should be tested, not assumed.

Build at least two objects with the same dominant oscillation frequency but different decay, phase response, nonlinear return map, or causal coupling.

If frequency alone identifies them, the assay is too easy.

A better possibility is:

```text
frequency / spectrum     one part of the lens
causal response          another part
trajectory geometry      another part
history / context         another part
```

The address is therefore multi-coordinate, but every coordinate has to earn its place against an attacker.

## Connection back to the current architecture

If Gate 8 works, the whole AlternativeNeuron loop becomes:

```text
raw mixed activity
    ↓
separate recurring generators
    ↓
recover directed causal relations
    ↓
form dynamical objects invariant to substrate coordinates
    ↓
keep only objects that reduce future sensing / consequence
    ↓
reshape routing toward repeatedly useful objects
    ↓
remapping changes the substrate but not necessarily the object
```

This is where `PresentMoment`, `WidePresent`, `MovingTarget`, the Geometric Neuron work, and the active-poking architecture actually meet in a falsifiable way.

## Later: PAC literally

Only after there are actual dynamical modes and temporal windows should a PAC fork be introduced.

A slow oscillator may gate the gain or admission of faster modes, but it must beat an aperiodic gate with identical duty cycle and energy budget. Otherwise the useful thing was timescale separation, not phase-amplitude coupling.

**Attackers first, claims second.**
