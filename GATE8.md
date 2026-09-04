# Gate 8 — dynamical objects over changing coordinates

Gate 8 asks a stricter version of the memory question:

> **What is the internal object if its physical coordinates are not its identity?**

This gate separates three ideas that are easy to collapse into one another.

- An **engram** is a persistent physical trace / ensemble / plastic substrate that helps make later recall possible.
- An **attractor** is a dynamical object: a fixed point, cycle, manifold, basin, or recurring trajectory selected by the dynamics.
- A **frequency** is one possible observable coordinate of a dynamical object. It is not a general definition of the object.

The artificial system below is not a biological engram model. Only Gate 8C earns the word `attractor`, and only in the standard dynamical-systems sense.

## G8A — WidePresent: a point can alias two moving states

A three-position ring has hidden direction `+1` or `-1`, while the observer sees position only.

At position `0`, the two hidden states have the same present observation but different futures:

```text
direction -1: recent ordered window [2, 1, 0] -> next 2
direction +1: recent ordered window [1, 2, 0] -> next 1
```

The same three observed values are present in both cases. Throw away temporal order and both become the multiset `{0,1,2}`.

Executed result:

```text
instantaneous point                50%
same samples, temporal order lost  50%
ordered three-sample window       100%
one reversible trial-step poke    100%
hidden-direction oracle           100%
```

Classification:

> `ORDERED_TRAJECTORY_FRAGMENT_OR_REVERSIBLE_PROBE_RESOLVES_AN_INSTANTANEOUSLY_ALIASED_MOVING_STATE`

This gives `WidePresent` a precise minimal job:

> **For a moving system, the useful present can be an ordered trajectory fragment rather than a frozen sample.**

It is a state-aliasing toy, not an attractor.

## G8B — same object under complete coordinate relabeling

The next assay creates four synthetic dynamical objects. Every object has exactly the same passive four-cycle, so period/frequency and passive transition-graph shape contain no identity information.

The objects differ only in where two reversible interventions land relative to the passive cycle:

```text
O0 -> (1, 2)
O1 -> (2, 1)
O2 -> (1, 3)
O3 -> (3, 1)
```

Each object is then embedded under **all `4!` permutations of physical state labels** and all four start phases:

```text
96 embeddings / object
384 total trials
```

Executed result:

```text
frequency / period only                 25%
passive graph only                      25%
raw coordinate nearest template        25%
coordinate-invariant poke signature   100%
```

The successful observer uses the observed passive orbit itself as an intrinsic coordinate chart. It asks where the pokes land **relative to that orbit**, rather than remembering physical labels.

Classification:

> `INTERVENTION_RESPONSE_DYNAMICS_IDENTIFY_OBJECTS_ACROSS_COMPLETE_SUBSTRATE_RELABELING_WHILE_COORDINATE_AND_FREQUENCY_TEMPLATES_FAIL`

This is the finite-state version of a familiar dynamical-systems idea: identity can live in structure preserved under a change of coordinates. The correct word here is closer to **isomorphism / conjugacy** than `same vector`.

It is still engineered. The interventions were chosen to distinguish the four objects.

## G8C — now earn the word attractor

Gate 8C finally introduces a nonlinear recurrent system: a 24-unit Hopfield-style network with three supplied random memories, off-diagonal Hebbian coupling, and synchronous sign updates.

All three supplied memories are stable fixed points.

The perturbation assay gives an actual basin-return curve:

| flipped bits | return to original basin | escape |
|---:|---:|---:|
| 1 | 1.000 | 0.000 |
| 2 | 0.994 | 0.006 |
| 3 | 0.940 | 0.060 |
| 4 | 0.892 | 0.108 |
| 6 | 0.770 | 0.230 |
| 8 | 0.482 | 0.518 |
| 10 | 0.130 | 0.870 |
| 12 | 0.0356 | 0.9644 |

So nearby perturbed states usually return; sufficiently distant states usually leave the basin.

### Quiet substrate, later reactivation

The activation can be completely absent between episodes. The persistent information is carried by the recurrent operator.

Later, showing only half of a stored pattern reactivates the correct fixed point with **96% accuracy**.

That gives the artificial system the abstract separation the user was circling:

```text
persistent substrate / operator
        !=
currently active memory state
```

A cue can reconstruct the active state from the persistent substrate.

This is engram-*like* only at that abstract level. It is not evidence that a biological engram is a Hopfield weight matrix or that a human memory is one fixed point.

### Coordinate relabeling

Permuting every neuron index together with the recurrent operator gives dynamically conjugate systems. Across eight complete permutations, perturbation recovery remains exactly equivalent:

```text
coordinate-permutation dynamical conjugacy = 1.000
```

Again, this is a mathematical relabeling, not biological representational drift.

### Frequency attacker

All three memories are fixed points.

Their oscillation frequency is therefore the same: **zero**.

So a frequency-only classifier gets only:

```text
1 / 3 = 33.3%
```

while the recurrent dynamics support three distinct basins.

This directly fences the tempting slogan `attractor = frequency object`:

> **Frequency can be one coordinate of a dynamical fingerprint, but distinct attractors need not have distinct frequencies at all.**

Classification:

> `NONLINEAR_RECURRENT_BASINS_REACTIVATE_FROM_PARTIAL_CUES_AND_SURVIVE_COORDINATE_RELABELING_WHILE_FREQUENCY_ALONE_CANNOT_IDENTIFY_THE_MEMORY`

## The stronger object definition

Gate 8 suggests a better operational object than `these neurons are on` or `this frequency is present`:

```text
object address = {
    ordered trajectory,
    return / escape dynamics,
    intervention response,
    response latency,
    transition structure,
    persistence,
    controllability,
    consequence
}
```

Not every coordinate is needed for every object. Each one has to earn its place against attackers.

A compact mathematical slogan is:

> **The object is an equivalence class of recoverable dynamics and action-response relations, not a frozen implementation vector.**

That is close in spirit to behavioral equivalence / predictive-state ideas: define state by the futures and action-conditioned observations it supports rather than by privileged hidden coordinates.

## What Gate 8 does not claim

- G8A is a deterministic state-aliasing construction.
- G8B is an exactly solvable finite-state coordinate-isomorphism toy.
- G8C is a small engineered Hopfield-style network with supplied patterns.
- G8C coordinate permutation is an exact mathematical relabeling, not biological neural drift.
- No gate shows that a human memory is a fixed point, that an engram is coordinate-free, or that consciousness follows from attractor dynamics.
- No gate establishes `frequency` as the ontology of cognition; G8C explicitly gives a counterexample.

The next attack should therefore remove the easiest invariance: **can identity survive gradual substrate drift when we do not know the coordinate map in advance?**

See [`NEXT.md`](NEXT.md).

**Attackers first, claims second.**
