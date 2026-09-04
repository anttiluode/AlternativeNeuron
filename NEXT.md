# NEXT — do not make the next gate easy

The first ladder is now useful precisely because its cheats are visible.

Gate 4 removed the supplied poke-response codebook but still received context
labels during calibration. The next work should not merely replace those labels
with an equally strong hidden lookup table.

## Gate 5 — can recurring surprises earn internal objects?

### Question

A stream contains recurring hidden regimes mixed with many one-off accidents.
No regime has an external name. The only available evidence is:

```text
cheap HOME residual
+ chosen reversible poke
+ one scalar consequence
```

Durable memory has only `K` prototype slots, while more than `K` distinct
response patterns occur.

The machine may keep short-lived temporary evidence outside the durable slots,
but temporary traces must decay. A pattern may become durable only through a
local admission/consolidation rule.

The claim to test is:

> recurring action-response structure can become an internal object because
> storing it reduces future sensing cost.

### Required attackers

Use the exact same `K` durable slots:

1. **LRU / remember recency** — every encountered pattern is equally eligible.
2. **random replacement** — same memory capacity, no selectivity.
3. **frequency/cache attacker** — a boring heavy-hitter or two-hit admission
   policy. If the proposed mechanism cannot beat or at least explain its
   difference from this, do not call the result intelligence.
4. **oracle top-K** — knows future recurrence and gives the ceiling.

### Metrics

- held-out scalar probes per recurring event;
- prediction/identification error;
- fraction of durable slots occupied by genuinely recurring patterns;
- false consolidation of one-offs;
- eviction/relearning cost after the recurrence distribution changes;
- distance to the oracle top-K cache.

### The open-world novelty trap

A serious implementation must not silently assume that the stored prototypes
are the complete set of possible worlds.

If a response is an arbitrary 12-bit signature, exact certification that a new
signature equals a stored prototype can require reading all 12 bits. A
closed-world classifier can stop after enough bits separate the stored
prototypes; an open-world recognizer cannot do that without either:

- a novelty prior / tolerated false-accept probability;
- an additional verification channel;
- structure in the response family;
- or paying the full measurement cost.

That is not an implementation nuisance. It is a real boundary on the slogan
"memory makes sensing cheaper." Gate 5 should report the novelty/error tradeoff
rather than hide it.

A clean positive result would therefore be one of these narrower statements:

```text
under a declared recurrence/novelty prior,
selective durable prototypes reduce expected probes at fixed error
```

or

```text
under a structured response family,
known prototypes can be certified with fewer scalar consequences
```

Anything stronger needs evidence.

## Gate 6 — did the world change, or did I change myself?

Gate 2 lets repeated probe traffic modify slow transport conductance. Eventually
that structural plasticity should modify not only the *cost* of an action but
its actual response operator.

Then the machine faces two experimentally distinguishable causes of surprise:

```text
WORLD CHANGE
    x changed while theta stayed fixed

SELF CHANGE
    theta changed while x stayed fixed
```

The observable can be the same scalar prediction error.

### Assay

Train a response model under `theta_0`, then use paired interventions:

```text
A. freeze theta, switch hidden world
B. freeze hidden world, switch theta
C. switch both
D. switch neither
```

The system must classify the cause and update the correct model component.

### Attackers

- one monolithic adaptive predictor with the same state budget;
- always blame world;
- always blame self/operator;
- reset everything on surprise;
- oracle cause label.

### What would count

The factorized machine must beat the monolithic attacker on held-out recovery
cost after both kinds of change, not merely produce prettier internal labels.

If it passes, the repo has earned a minimal computational **self-model** in a
very narrow sense: it represents that some changes in its sensations are caused
by changes in its own sensing/acting operator.

That still says nothing about consciousness.

## Experimental fork — PAC-style coupled clocks

Only after the non-oscillatory mechanism is understood should we add rhythms.
A future fork can introduce a slow phase variable and ask whether it gates:

- fast poke amplitude;
- surprise threshold;
- probe budget;
- or structural write windows.

Then phase-amplitude coupling can be measured literally rather than used as an
analogy. Compare against an aperiodic slow gate with the same duty cycle. If the
rhythm itself buys nothing, kill the PAC story.

## Longer target

The architecture worth chasing is still:

```text
predict cheaply
   |
surprise?
   |
choose what to read or poke
   |
learn from scalar consequence
   |
form only useful persistent objects
   |
reshape transport from repeated use
   |
know when that self-change invalidates the old response model
```

The next gates should make each arrow earn its place.
