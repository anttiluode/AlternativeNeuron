# Gate 7 — signal ecology and causal address

Gate 7 asks what a bounded observer should do when several recurring signal streams compete for scarce memory and routing.

It is split deliberately:

- **G7A** assumes the sources are already separated and tests allocation only.
- **G7B** removes the clean command/response coordinates and asks what static separation, temporal direction, and an efference anchor each contribute.

Neither sub-gate is a biological attractor model.

## G7A — which already-separated sources deserve scarce routing?

Five source streams compete for a fixed conductance budget:

```text
self       recurring command-like events
partner    response-like events
fly        loud, frequent distractor; cheap to ignore
context    quiet contextual signal
alarm      rare but costly to miss
```

The observer may boost at most three sources. The fly has the largest amplitude and frequency but almost no consequence. Context is weak alone but reduces the cost of interpreting partner/alarm, so source value is non-additive.

Across eight regenerated streams:

```text
policy                 mean cost      phase-1 late
oracle                   0.56146          0.65686
joint consequence        0.56965          0.66091
independent value        0.69623          0.88397
frequency                0.74842          0.98231
random                   0.75087          0.91021
LRU                      0.76764          0.99647
variance                 0.81079          1.11732
```

The rolling joint policy reaches the new phase-1 oracle source set in all 8 seeds with mean delay 200 steps.

Classification:

> `JOINT_CONSEQUENCE_ALLOCATION_IGNORES_LOUD_DISTRACTOR_AND_REALLOCATES_FIXED_ROUTING_BUDGET_TO_COMPLEMENTARY_SOURCES`

The useful result is narrow:

> **Under a fixed routing budget, source value can be relational. A weak source can deserve structure because it makes another source interpretable, while a loud persistent source can deserve almost none because it is cheap to ignore.**

## G7B — static separation is not causal direction

G7B generates two latent source trains and one distractor:

```text
command[t]

partner[t] = 0.80 * command[t-5]
           + 0.60 * independent_innovation[t]

fly[t]     = unrelated high-variance activity
```

The command and partner are orthogonally mixed through eight regenerated angles. The fly is exposed as a separate channel at six times standardized amplitude.

The command/partner contemporaneous correlation remains tiny (maximum absolute value **0.01584**), so the defining relationship is temporal rather than a same-time correlation.

### Static result

A tiny fourth-order 2-D ICA audit recovers the two mixed generators almost perfectly:

```text
mean absolute recovery correlation   0.999919
worst recovery correlation           0.999657
```

A variance/PCA-like channel selector picks the loud fly in **8/8** cases.

But static source separation has no time arrow. Reversing every sample in time changes the static ICA contrast by exactly **0.0**.

And ICA still has sign/permutation ambiguity: without an external anchor, attaching the semantic label `command-originating/self` to one of the two recovered components is 50/50 under an equal prior.

### Directed temporal address

The machine is allowed the one privileged fact Gate 6B said was necessary: an efference record of when it issued the command.

That record anchors one recovered component at zero lag. The other component then has a response peak at **+5** steps.

Across all eight mixtures:

```text
command component label accuracy       1.000
partner delay recovery accuracy         1.000
reverse-time delay = -5 accuracy        1.000
mean true partner lag correlation       0.82295
mean shuffled-command peak              0.03498
true / shuffled peak ratio             23.53x
```

Time reversal is the cleanest fence:

```text
FORWARD DATA
command  ───────(+5)──────▶ responder

REVERSED DATA
responder ──────(+5)──────▶ command
```

The static sample cloud is the same; only temporal order changed.

Classification:

> `STATIC_SOURCE_SEPARATION_RECOVERS_GENERATORS_BUT_DIRECTED_EFFERENCE_TIMING_SUPPLIES_CAUSAL_ADDRESS`

### Strong negative: plain lag correlation is enough here

A simple raw lagged-correlation attacker also recovers the +5 delay in **8/8** mixtures, without ICA.

That is an important negative. G7B does **not** establish that sophisticated source separation is needed merely to detect a delayed dependency in this easy synthetic setting.

What separation adds is a reusable source identity. What the efference/lag relation adds is a directed address for that source.

So the decomposition is better written as:

```text
static statistics    -> which generators can be separated?
temporal relation    -> how are the generators coupled?
causal anchor        -> which side issued the action?
resource history     -> which generators deserve cheaper future routing?
```

## Causal address

A recovered source can now be described without neuron IDs by quantities such as:

```text
controllability
response latency
predictability from issued commands
delayed echo / reciprocity
persistence
consequence if ignored
```

This is an operational address, not metaphysical ownership. An external tool can be causally close; an internal autonomous process can be causally distant.

## What Gate 7 does not show

The mixtures are linear. The response law, costs, and source ecology are engineered. G7B still receives a privileged command/efference record. Temporal precedence alone is not proof of causation, and the delayed dependency is intentionally easy enough that ordinary lag correlation detects it.

Gate 7 therefore does not establish cortical-area formation, social organization, attractor memory, consciousness, or a new PCA/ICA result.

The next useful question is different: **what should count as the same internal object when the physical coordinates implementing it change?**

See [`NEXT.md`](NEXT.md).

**Attackers first, claims second.**
