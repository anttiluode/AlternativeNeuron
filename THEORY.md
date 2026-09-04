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

The first executable toy has three explicit state classes.

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

## The PAC analogy, carefully

Phase-amplitude coupling (PAC) and PCA are unrelated despite the easy acronym
collision. PAC is a cross-frequency phenomenon: the phase of a slower rhythm is
statistically related to the amplitude of a faster rhythm.

The fast/medium/slow split here is **not PAC**. Nothing in the current code is an
oscillator and there is no phase-amplitude statistic. PAC is nevertheless a
useful biological reminder that different timescales can be coupled rather
than independent. A future rhythmic implementation could ask whether a slow
structural or contextual variable gates the gain/budget of fast exploratory
pulses, but that would be a new experiment, not an interpretation of these
gates.

## The qualia / degree-of-freedom thought, fenced

Adding a poke channel changes the machine's epistemic degrees of freedom.
Instead of only receiving `what happened`, it can also acquire
`what happens if I act here`.

That is a legitimate computational distinction and a plausible place to study
self/world, agency, counterfactual sensing, or sensorimotor contingencies.
Nothing in this repository measures subjective experience, phenomenology, or
qualia. The word should not be promoted from philosophical motivation into an
experimental conclusion.

## What Gate 0 deliberately cheats on

The response codebook is supplied to the information-gain policy. The machine
does not yet have to *learn what its pokes mean*.

That is the next serious boundary.

A stronger AlternativeNeuron should begin with an unknown state-dependent
response operator and learn it from scalar consequences while simultaneously
deciding what to probe. Only after that should slow structural adaptation be
allowed to modify the operator itself.

That creates the nontrivial loop:

```text
unknown world
   |
act -> consequence
   |
learn response model
   |
choose better acts
   |
remember useful state
   |
change transport slowly
   |
old response model may become wrong
   |
act again
```

The machine would then have to distinguish **the world changed** from **I
changed the way I touch the world**. That is the next place worth poking.
