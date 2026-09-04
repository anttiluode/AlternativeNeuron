# AlternativeNeuron — the architecture we are actually testing

This repo starts after the GeometricNeuronV24 Gate-6 line rather than trying to
rescue the literal biological-neuron claim.

The working object is:

```text
hidden/shared state
      |
cheap residual pulse
      |
expected?
  |        \
 yes        no
  |          \
reuse       choose a question
memory      (address / scale / poke)
              |
        scalar consequence
              |
        update fast belief
              |
        write medium memory
              |
        repeated traffic
              |
      slowly changes structure
              |
      future questions cost less
```

The important move is that **intervention is allowed to be a sense**.
Observation asks what happened. A reversible poke asks what happens if I do
this. If two hidden states look identical through the passive channel but react
differently to the same poke, the action-response pair exposes information the
passive read does not contain.

That idea is not new by itself: active system identification, experimental
design, control, haptics, causal intervention and embodied sensing all live in
nearby territory. The experiment here is the composition with persistent memory
and a slowly changing transport budget.

## Three timescales

The executable toy has three explicit state classes.

### Fast — exploratory state

During one surprise, the machine carries a candidate set and chooses the next
poke by expected information gain divided by current transport cost. This state
can vanish after the ambiguity is resolved.

### Medium — event memory

Once a hidden context is identified, the answer is kept across a persistent
event. If the cheap HOME channel remains compatible with that remembered
context, no paid poke is made again.

This is the sense in which memory changes future sensing: it is not merely a log
of the previous answer. It changes whether another measurement is purchased.

### Slow — structure / operator memory

Across many events, the channels that repeatedly carry useful probes accumulate
traffic. A fixed total conductance budget is then reallocated, so the same
future information-seeking policy has a different cost landscape.

In the first toy, channel cost is `1/g` and consolidation uses

```text
g_a proportional to sqrt(traffic_a + background)
```

under a fixed total `sum(g)`. This square-root allocator is not claimed as a new
learning law; it is a deliberately simple fixed-budget structural rule inherited
from the operator/plasticity experiments. Its role here is to close the loop:

```text
experience -> probe traffic -> structure -> future sampling policy
```

The word "memory" therefore means two different persistent consequences here:
medium memory keeps a resolved fact, while slow memory changes the operator
through which later facts are acquired. The slow state is closer to
**history-made-routing** than to a database.

## The PAC analogy, carefully

Phase-amplitude coupling (PAC) and PCA are unrelated despite the easy acronym
collision. PAC is a cross-frequency phenomenon: the phase of a slower rhythm is
statistically related to the amplitude of a faster rhythm.

The fast/medium/slow split here is **not PAC**. Nothing in the current code is an
oscillator and there is no phase-amplitude statistic. PAC is nevertheless a
useful biological reminder that different timescales can be coupled rather
than independent. A future rhythmic implementation could ask whether a slow
contextual or structural rhythm gates the gain, threshold, or budget of fast
exploratory pulses. That would be a new experiment, not an interpretation of
these gates.

## The qualia / degree-of-freedom thought, fenced

Adding a poke channel changes the machine's epistemic degrees of freedom.
Instead of only receiving

```text
what happened?
```

it can also acquire

```text
what happens if I act here?
```

The second signal is counterfactual and action-conditioned. That is a legitimate
computational distinction and a plausible place to study self/world separation,
agency, active inference, haptic-style sensing, or sensorimotor contingencies.

Nothing in this repository measures subjective experience, phenomenology, or
qualia. The philosophical connection can motivate which degrees of freedom we
test; it cannot be promoted into an empirical conclusion.

## Gate 4 removes one cheat, not all of them

Gate 0 originally supplied the full poke-response codebook to the
information-gain policy. Gate 4 removes that particular support.

The world now hides a random state-dependent response signature. During a
calibration phase the machine is given a context label and may only learn the
signature by issuing scalar pokes. After calibration, the same learned response
model is reused to choose three information-directed pokes per context.

The result is intentionally modest:

```text
labeled scalar calibration       192 pokes
active test phase                384 pokes / 128 contexts
active test accuracy             1.000
shuffled learned codebook        0.125 accuracy
active total incl. calibration   576
exhaustive total                 1728
```

So a poke can acquire **learned semantics** rather than arriving with its
meaning hard-coded. But the calibration labels are still an ontology supplied
from outside. The machine knows that "this is context 7" while it is learning
what context 7 does under each action.

That leaves the more interesting problem untouched:

> **Can recurring patterns of action-conditioned consequence become internal
> objects without anybody naming the objects first?**

## The next boundary: from response model to self-made objects

The next experiment should present a stream containing recurring hidden regimes
and one-off accidents. There are more regimes than durable memory slots.
Initially every surprise may leave only a temporary response trace.

```text
surprise
   |
try informative pokes
   |
temporary response signature
   |
recurs and saves future sensing?
   |                 \
  no                  yes
   |                    \
decay                consolidate
                         |
                  internal prototype
                         |
                changes future probing
```

The attacker must be a boring cache with exactly the same memory budget: LRU,
random replacement, or "remember the most recent K things". A selective
mechanism has earned something only if it uses its K slots for recurring,
future-useful structure and therefore pays fewer later probes on held-out
streams.

This is the old V24 question "which pieces of experience deserve to become part
of the machine?" with the new poke channel included.

## The boundary after that: did the world change, or did I change myself?

Slow structural adaptation makes the problem stranger. If useful traffic alters
the transport operator, then the same external state can later produce a
different action-response relation simply because **the machine changed the
way it touches the state**.

That creates self-induced nonstationarity:

```text
world x
  |
poke through operator T(theta)
  |
scalar consequence
  |
learn response model
  |
experience changes theta
  |
T(theta) changes
  |
old response model becomes stale
```

A serious AlternativeNeuron should eventually distinguish two explanations for
a prediction error:

```text
A. the world changed
B. my own operator changed
```

That is a much sharper self/world problem than attaching a philosophical label
to a pulse. It is also experimentally attackable: freeze the world and change
the internal operator; then freeze the operator and change the world. If the
machine cannot tell those interventions apart, it has no earned self-model.

The longer-term loop is therefore:

```text
unknown world
   |
act -> consequence
   |
learn response model
   |
form useful internal objects
   |
remember selectively
   |
change transport slowly
   |
model own operator change
   |
act again
```

That is where this repo should poke next.
