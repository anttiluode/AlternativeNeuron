# NEXT — signal ecology under a fixed budget

Gate 6 is now executed on the `gate6-self-world-attribution` branch.

It produced three linked results:

1. a factorized world/self response model can compress a joint family and compose unseen combinations;
2. intervention cannot distinguish causal stories that predict the same response to every available poke;
3. source statistics can separate some mixed generators even when PCA cannot, but blind separation still cannot attach the semantic label `self` without an anchor such as efference timing.

See [`GATE6.md`](GATE6.md).

The next work should therefore stop treating the world as two clean factors and move to the thing a real bounded observer actually faces: **many overlapping signal trains with different statistics, histories, delays, and values.**

## Gate 7 — which signals deserve structure?

### Question

Suppose the observer receives mixtures of sources with properties such as:

```text
new / transient
old / recurring
fast / delayed
self-anchored / externally driven
high variance / low variance
frequent / rare
predictive / useless
```

Some sources recur enough to deserve durable objects. Some matter often enough to deserve cheaper routing. Some are loud but irrelevant. Some are rare but costly to miss.

The claim to test is deliberately narrow:

> Under a fixed representation and transport budget, a bounded active observer can do better by allocating memory and routing according to **expected future consequence**, not raw variance, recency, or frequency alone.

This is the place where Gate 5 and Gate 2 should finally meet.

## Synthetic signal ecology

Start with a small mixed stream containing at least these source roles:

```text
SELF COMMAND
    sparse events with a privileged efference timestamp

PARTNER / RESPONDER
    delayed response statistically coupled to some self commands

FLY
    frequent high-variance distractor, persistent but task-irrelevant

SLOW CONTEXT
    low-amplitude persistent state that changes how another signal should be interpreted

RARE ALARM
    infrequent source with large consequence if missed
```

The labels above exist only in the generator and evaluation code. The observer should receive mixtures and whatever causal anchors are explicitly declared.

The user-level intuition to test is not that a fly, a person, and a neuron are the same thing. It is that a stream-processing system may have to decide which recurring causes become cheap, durable, and highly routed while others remain weak or transient.

## Three separations

Gate 7 should keep three problems distinct.

### 1. Statistical source separation

Can the system infer recurring generators from mixtures using source properties such as:

- non-Gaussianity;
- autocorrelation / persistence;
- spectral or temporal signature;
- nonstationarity;
- delayed dependence?

PCA and ICA are attackers / tools here, not the final architecture.

### 2. Causal address

For each recovered source, estimate an operational rather than metaphysical notion of distance:

```text
controllability
response latency
predictability from issued commands
reciprocity / delayed echo
persistence after command stops
```

A source tightly locked to an efference marker is causally close to the acting boundary. A delayed responder is farther away. An unrelated distractor is farther still.

This should be called **causal address** or **causal distance**, not proof of selfhood. An external tool can be highly controllable and therefore causally close.

### 3. Resource allocation

Give the system fewer durable object slots and less transport conductance than there are recurring sources.

The system must decide:

```text
what stays transient?
what earns a durable object?
what gets cheaper routing?
what gets suppressed despite being frequent or loud?
```

The primary proposed rule should optimize expected future task/sensing cost jointly, not separately per source.

## Required attackers

At minimum:

1. **PCA / variance allocation** — give resources to the largest-variance components;
2. **frequency** — allocate to what occurs most;
3. **recency / LRU** — allocate to what happened recently;
4. **ICA then frequency** — separate first, but allocate with no consequence model;
5. **prediction-only** — allocate to sources that best predict future observations, regardless of task consequence;
6. **random allocation**;
7. **oracle source labels + future consequences** — ceiling only.

If the proposed architecture only wins because it is given cleaner source identities than the attackers, Gate 7 fails.

## Primary metrics

Measure:

- held-out task loss / missed-consequence cost;
- scalar sensing or reconstruction cost;
- durable slots occupied by useful vs distracting sources;
- conductance / routing budget assigned to each source;
- adaptation after source statistics change;
- false consolidation of one-off or useless events;
- rare-alarm miss rate;
- how quickly a persistent distractor becomes cheap to ignore.

The `FLY` source is specifically useful as an attacker: it should be frequent and high variance enough that PCA/frequency wants to devote resources to it, while a consequence-aware system should learn that it is cheap to suppress unless the task changes.

## The signal-train memory picture

The architecture should expose the user's old/new/transient intuition explicitly:

```text
FAST TRACE
    what is happening now?
    candidate source activity

MEDIUM OBJECT
    have I seen this generator enough that recognizing it again should be cheap?

SLOW ROUTING
    has this generator mattered often enough that future evidence about it deserves more / less transport budget?
```

A source can therefore move through states:

```text
novel pulse
   -> temporary trace
   -> recurring candidate
   -> durable object
   -> structural routing bias
```

But there must also be reverse transitions:

```text
obsolete / useless source
   -> decay durable confidence
   -> release routing budget
```

Otherwise the architecture merely accumulates history and eventually ossifies.

## Mirror / resonance attack

The delayed responder should deliberately violate simple ICA independence by echoing part of the self-command stream after a variable delay.

That gives a clean distinction:

```text
independent source separation
vs
coupled causal system identification
```

If ICA fuses the command and responder, temporal intervention structure should be allowed to rescue the decomposition. Compare against matched correlations with shuffled lag to ensure the system is using direction / timing rather than raw similarity.

This is the mathematically cleaner version of the "poke goes out, response comes back, resonation connects things" intuition: not mystical resonance, but a directed delayed dependency that can be tested.

## Kill conditions

Do not promote Gate 7 if:

- variance or frequency alone performs equally well;
- the source labels leak into the policy;
- the rare alarm is made trivially identifiable by amplitude;
- the fly is too easy to ignore because it never overlaps useful signals;
- the delayed responder can be separated without using temporal direction;
- resource allocation does not improve held-out consequence or sensing cost;
- the system cannot release budget when source statistics change;
- the effect disappears under regenerated mixing matrices / source schedules.

## Longer target

If Gate 7 passes, the next layer is a network of bounded observers rather than one observer: each node sees only local mixtures, sends limited messages, and may reshape routing from repeated traffic.

Only there does the social-network analogy become worth testing mathematically:

```text
local agents
   -> selective message routing
   -> broadcast / hierarchy / neighborhood effects
   -> repeated traffic reshapes routes
   -> macroscopic organization emerges
```

That would be a graph/message-passing experiment, not a claim that society literally is a brain.

## PAC-style fork — later

The fast/medium/slow architecture is still not literal phase-amplitude coupling. A rhythmic fork should come only after Gate 7, when there are actually multiple source timescales worth gating. Compare a slow oscillatory gate against an aperiodic slow gate with the same duty cycle; if phase buys nothing, kill the PAC interpretation.

**Attackers first, claims second.**
