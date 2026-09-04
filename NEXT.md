# NEXT — world changed, or I changed myself?

Gate 5 is now executed on the `gate5-selective-objects` branch. It removed the
supplied object labels and found a narrower result than the original slogan:
selective durable prototypes can reduce expected scalar sensing cost, but only
under an explicit novelty/error model, and remembered prototypes interact with
one another. The best finite cache can rationally leave capacity unused.

See [`GATE5.md`](GATE5.md) and the machine-readable Gate 5 / 5B receipts.

The next work should therefore move to the other unresolved arrow in the
architecture: **slow self-change can invalidate the meaning of a poke**.

## Gate 6 — did the world change, or did I change myself?

### Question

So far slow structure changes only the cost of an action. Gate 6 will make
structure alter the actual action-response operator.

Then the machine can receive the same kind of scalar prediction error from two
causally different events:

```text
WORLD CHANGE
    hidden state x changed
    self/operator theta stayed fixed

SELF CHANGE
    hidden state x stayed fixed
    self/operator theta changed
```

The machine is not given the cause label.

The claim to test is deliberately narrow:

> A bounded active observer that factorizes world state from its own
> sensing/acting operator can recover from both kinds of change more cheaply
> than an equal-budget monolithic adaptive predictor.

Passing this would earn a minimal computational **self-model** only in the sense
that the machine represents that some changes in its sensory consequences are
caused by changes in itself.

It would not imply consciousness or subjective experience.

## Assay

Start with a learned scalar response model

```text
y = R(x, theta, a)
```

where:

- `x` is hidden external context;
- `theta` is slow internal structure/operator state;
- `a` is a chosen reversible poke;
- `y` is the one scalar consequence.

Calibrate under `(x0, theta0)`, then create balanced episodes:

```text
A. WORLD ONLY   : switch x, freeze theta
B. SELF ONLY    : freeze x, switch theta
C. BOTH         : switch x and theta
D. NEITHER      : freeze both
```

The observer sees only its ordinary cheap channel plus chosen poke consequences.
No hidden cause bit is exposed.

## Required factorization

The proposed machine keeps two hypotheses that can be updated separately:

```text
world model      W
self/operator    S

predicted consequence = R_hat(W, S, action)
```

On surprise it should choose interventions that are maximally diagnostic of
which component became stale, not simply gather more generic evidence.

The first implementation should keep this discrete and exactly auditable before
adding learned neural models.

## Required attackers

Use the same total state / parameter budget where possible:

1. **monolithic adaptive predictor** — one model of action → consequence with no
   world/self factorization;
2. **always blame world** — only W may update;
3. **always blame self** — only S may update;
4. **reset everything** — discard both models on surprise;
5. **random diagnostic pokes** — same number/cost of interventions, no
   information-directed attribution;
6. **oracle cause label** — ceiling, not a competitor.

If factorization only gives prettier labels but no cheaper recovery, Gate 6
fails.

## Metrics

Primary:

- scalar probes required to regain target prediction accuracy after each change
  type;
- action-response prediction error during recovery;
- world-vs-self attribution accuracy;
- unnecessary updates to the component that did not change.

Secondary:

- held-out transfer to combinations of world and self states not paired during
  calibration;
- whether attribution-directed pokes beat random pokes at equal cost;
- catastrophic reset / forgetting cost;
- distance to oracle cause labels.

## Kill conditions

Do not promote a self-model interpretation if any of these happen:

- a monolithic equal-budget predictor recovers just as cheaply;
- cause attribution is possible only because one arm has a trivial amplitude or
  timing cue;
- the factorized model was secretly given the true world/self coordinates;
- shuffled world/self labels perform equally well;
- diagnostic interventions do not improve over random equal-cost pokes;
- success disappears when the response tables are regenerated.

## The deeper test after Gate 6

If Gate 6 passes, close the full loop:

```text
experience
   -> useful interventions
   -> medium memory
   -> slow structural change
   -> changed action-response operator
   -> old self-model becomes stale
   -> intervention identifies that the change was self-caused
   -> update self model, not world model
```

That is much more interesting than merely saying "the network has plastic
weights." The machine would have to model consequences of its **own previous
learning**.

## PAC-style fork — later, and literally

The current fast/medium/slow architecture is not phase-amplitude coupling (PAC):
there are no oscillators yet.

Only after the non-oscillatory causal mechanism is understood should a rhythmic
fork introduce a slow phase variable and test whether it gates:

- fast poke amplitude;
- surprise threshold;
- probe budget;
- medium-to-slow consolidation windows;
- or structural rewrite gain.

Then measure PAC literally and compare against an **aperiodic slow gate with the
same duty cycle**. If phase buys nothing beyond generic slow gating, kill the
PAC story.

## Longer target

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

Gate 5 made the "persistent objects" arrow earn its place in a synthetic assay.
Gate 6 now has to make the final arrow earn its place.
