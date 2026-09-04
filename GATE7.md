# Gate 7 — signal ecology under a fixed routing budget

Gate 7 moves from clean two-source identifiability to a bounded observer facing several recurring signal streams with different statistics and consequences.

The first sub-gate deliberately isolates **allocation after source separation**. Every policy receives the same source identities. Gate 7B will remove that convenience and test mixed delayed signals.

## G7A — which already-separated sources deserve scarce routing?

Five synthetic source streams compete for a fixed conductance budget:

```text
self       recurring command-like events
partner    recurring response-like events
fly        loud, frequent distractor; cheap to ignore
context    quiet, slow contextual signal
alarm      rare but costly to miss
```

The observer may boost at most three sources. Total conductance is fixed.

The important trap is that observation amplitude and consequence are deliberately decoupled:

```text
source      amplitude      ignore loss
self          1.0            1.5
partner       1.5            2.0
fly           5.0            0.08
context       0.3            0.10
alarm         2.0            4.0
```

So the fly dominates raw variance and frequency while being nearly irrelevant to the task.

Partner and alarm interpretation additionally require access to context. This makes resource value **non-additive**: context can look weak by itself but become valuable when another source depends on it.

## Phase shift

Two phases change source rates:

```text
phase 0
self 0.25, partner 0.15, fly 0.58, context 0.03, alarm 0.02

phase 1
self 0.15, partner 0.35, fly 0.45, context 0.025, alarm 0.05
```

The future-aware optimal boosted set changes from:

```text
phase 0: self + partner + context
phase 1: partner + context + alarm
```

A successful online policy must therefore not only allocate well; it must also **release old routing budget** when the ecology changes.

## Attackers

All policies see the same already-separated source identities.

- `variance` — PCA-like resource allocation to largest empirical variance;
- `frequency` — allocate to the most frequent streams;
- `lru` — allocate to recently active streams;
- `random` — equal-budget random subset;
- `independent_value` — strong attacker: each source is ranked by the expected consequence reduction it provides when boosted alone, then the selected set is allowed a jointly optimized conductance split;
- `oracle` — future-aware phase distribution, ceiling only;
- `joint_consequence` — proposed policy: estimate recent source rates and jointly search over source subsets and conductance allocation.

The `independent_value` attacker matters because it has the same consequence model. The only thing it lacks is the ability to value **combinations before selecting the slots**.

## Executed CI receipt

Across eight regenerated streams:

```text
policy                 mean cost      phase-1 late cost
oracle                   0.56146          0.65686
joint consequence        0.56965          0.66091
independent value        0.69623          0.88397
frequency                0.74842          0.98231
random                   0.75087          0.91021
LRU                      0.76764          0.99647
variance                 0.81079          1.11732
```

The rolling joint policy reaches the new phase-1 oracle source set in every seed, with a mean delay of **200 steps** under a 256-event memory window and 64-step reoptimization interval.

Classification:

> `JOINT_CONSEQUENCE_ALLOCATION_IGNORES_LOUD_DISTRACTOR_AND_REALLOCATES_FIXED_ROUTING_BUDGET_TO_COMPLEMENTARY_SOURCES`

The useful result is not merely that a hand-designed utility function beats PCA. It is the narrower structural point:

> **Under a fixed routing budget, source value can be relational. A weak source can deserve structure because it makes another source interpretable, while a loud persistent source can deserve almost none because it is cheap to ignore.**

That is the same non-additivity Gate 5 found in memory, now appearing in routing allocation.

## What G7A does not test

The source identities are given to every policy. Therefore G7A does **not** show that the machine can discover a fly, partner, context, alarm, or self-command inside a raw mixture.

The interaction law and loss values are engineered. This is not a cortical-area model, a social model, or a claim that biological brains use this exact allocation rule.

## G7B — remove the clean source labels

The next sub-gate should mix the source trains through regenerated linear mixtures and add one deliberate dependency:

```text
self command
    ↓ variable delay
partner response
```

That delayed responder violates the independence assumption behind ordinary ICA.

Required comparison:

```text
PCA / variance decomposition
ICA / independent-source decomposition
lagged correlation
shuffled-lag control
intervention-aware temporal decomposition
oracle source labels
```

The central question is whether directed timing plus an efference marker can separate a command-linked responder from unrelated high-variance activity when ordinary ICA wants independent components.

A successful result must use **direction / delay**, not merely correlation. Shuffling the lag while preserving marginal amplitudes and source frequencies must destroy the advantage.

## Causal address

If G7B works, each recovered source can be assigned an operational address using quantities such as:

```text
controllability
response latency
predictability from issued commands
reciprocity / delayed echo
persistence after commands stop
```

This is a useful notion of **causal distance**, not metaphysical selfhood. An external tool can be highly controllable and causally close; an internal autonomous process can be causally distant.

## Signal-train lifecycle

The longer architecture is now explicit:

```text
novel pulse
   ↓
FAST transient trace
   ↓ recurrence / consequence
MEDIUM durable object
   ↓ repeated useful traffic
SLOW routing bias
```

and, equally important:

```text
obsolete / irrelevant source
   ↓
confidence decay
   ↓
release routing budget
```

Without the reverse path the machine merely ossifies.

**Attackers first, claims second.**
