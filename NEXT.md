# NEXT — identity without a known coordinate map

Gate 8 made three things executable:

```text
G8A  a point sample can alias a moving state; ordered history can recover it
G8B  action-response structure can survive complete coordinate relabeling
G8C  a nonlinear recurrent operator can carry stable basins that later reactivate
```

But Gate 8B/C use an easy invariance: the experimenter knows the relabeling and
transforms the whole operator consistently.

That is not yet the interesting version of a memory being "the same thing" while
its physical realization changes.

## Gate 9 — substrate drift

The next question is:

> **Can the machine recognize a recurring dynamical object while its physical
> substrate slowly rewrites itself, without being given an old→new coordinate
> map?**

This is the hard version of the user's `mother` intuition: a richly learned
object can remain behaviorally recognizable even though the active population,
synapses, context, and current trajectory are never exactly the same twice.

It is also the point where the repo must stop using mathematical relabeling as a
proxy for real remapping.

## G9A — gradual operator drift, preserved behavior

Start from several recurrent objects with distinct basin / response profiles.
Then slowly alter their implementation:

```text
old operator A0
    ↓ local weight turnover / redistribution
A1
    ↓
A2
    ↓
...
```

At each drift step, preserve a bounded task-level behavior using only local
homeostatic compensation. Do **not** carry a coordinate correspondence from the
old system into the observer.

Candidate drift operations:

- randomly weaken a fraction of synapses;
- regrow compensating local connections;
- retire a fraction of units and recruit unused units;
- add low-amplitude weight noise;
- enforce fixed total weight / conductance budget;
- optionally allow slow structural homeostasis to restore basin function.

The identity observer is allowed only ordinary probes and trajectories from the
current implementation.

## Required attackers

1. **raw coordinate overlap** — compare active neurons / state vectors directly;
2. **weight-matrix similarity** — compare current operator to stored operator;
3. **best linear alignment** — a stronger coordinate attacker allowed to fit a
   global linear map from calibration data;
4. **frequency / spectrum only**;
5. **passive trajectory statistics only**;
6. **intervention-response fingerprint**;
7. **combined predictive-state fingerprint** — future observation distributions
   under selected actions;
8. **oracle drift map** — ceiling only.

If a fitted coordinate alignment solves the task as cheaply as the proposed
behavioral fingerprint, there is no reason to invoke a deeper object.

## What should remain invariant?

Do not require the exact state vector or weight matrix to remain similar.
Instead measure things like:

```text
return probability after perturbation
return-time distribution
response latency to selected pokes
transition probabilities between basins
partial-cue completion behavior
controllability profile
consequence if ignored
```

This suggests an operational definition very close to predictive-state / behavioral equivalence:

> two implementations count as the same object to the bounded machine when the
> action-conditioned futures relevant to its task remain equivalent enough.

This is established mathematical territory in spirit—system identification,
behavioral equivalence, predictive state representations, bisimulation—so the
repo should not claim invention of that principle. The experiment is about
whether it gives this architecture a better invariant than physical coordinates.

## G9B — identity versus mutation

Drift alone is too easy if every change is forced to preserve behavior.

Create a continuum:

```text
implementation drift              semantics preserved
        ↓
behavioral drift                  ambiguous zone
        ↓
object mutation                   should be called something new
```

The observer must decide when to keep the same persistent object and when to
split / replace it.

Measure:

- false splits: same behavior, new object declared;
- false merges: materially changed behavior, old identity retained;
- probes required to decide;
- recovery after a distribution shift;
- cost relative to oracle drift labels.

This is the open-world version of Gate 5's novelty problem applied to dynamics.

## G9C — memory under turnover

Only after G9A/B pass, close the loop with slow structural adaptation.

Let an object be repeatedly useful. Its traffic earns routing / redundant
support. Then begin substrate turnover.

Ask whether the heavily used object is more robust to turnover **without giving
it extra total resource for free**—for example, it may redistribute the same
budget into redundancy or alternative routes.

Attackers:

- uniform redundancy;
- random redundancy;
- frequency-only allocation;
- consequence-aware allocation;
- oracle future-use allocation.

This would finally test a computational version of:

```text
what matters repeatedly
    ↓
changes slow structure
    ↓
becomes easier to reconstruct
    ↓
can survive more local substrate churn
```

That is much closer to a persistent memory trace in flux than the exact
permutation result of Gate 8.

## Present / trajectory connection

Gate 8A also changes what `present` should mean in this architecture.

A point observation can be insufficient even when no information is missing
from a short local history. So the internal state estimator should be allowed to
use a **causal ordered window** or a learned recurrent summary, not just the
current sample.

The obvious attacker is always the same samples with order destroyed. If that
works equally well, the claimed temporal state was really just extra data.

## Frequency remains a lens, not the ontology

Gate 8C already gives three distinct attractors with the same frequency: zero.
Gate 9 should continue to include frequency/spectral attackers, but not privilege
them.

A richer dynamical address can include:

```text
spectrum
phase / lag
trajectory geometry
return dynamics
causal response
context dependence
consequence
```

Any coordinate that does not improve identity under drift should be removed.

## Later PAC fork

PAC becomes worth testing only after the architecture has actual fast modes and
slow structural/state variables.

Then introduce a slow oscillator that gates fast-mode gain or consolidation and
compare it against an aperiodic slow gate with identical duty cycle and resource
budget. If periodic phase adds nothing, the useful mechanism was timescale
separation rather than phase-amplitude coupling.

**Attackers first, claims second.**
