# Gate 6 — world, self, and source identifiability

Gate 6 is a three-part audit of the question:

> When the consequence of a poke changes, did the world change, did my own operator change, or are those explanations not identifiable from the available evidence?

The three parts deliberately separate a positive result from two necessary boundaries.

## G6 — a factorized world/self model can compose unseen joint states

Synthetic response law:

```text
R(x, theta, a) = W(x,a) XOR S(theta,a)
```

There are 8 external world states, 4 internal operator states, and 12 reversible scalar poke channels.

A controlled calibration star observes all world states at `self=0` plus all self states at `world=0`. That is 11 joint signatures, or 132 stored bits. The full 8×4 joint lookup would require 32 signatures, or 384 bits.

Executed CI result:

```text
factorized stored bits                 132
full joint stored bits                 384
exact reconstruction of all 32 pairs   1.0
world/self cause accuracy               1.0
exact pair accuracy                     1.0
mean probes to identify cause           3.914
mean probes to identify exact pair      4.674
random diagnostic poke order            6.032
safe monolithic open-world scan        12.000
```

The equal-bit monolithic closed-world attacker is cheaper at 3.53 probes only because it assumes the current state must be one of its cached joint signatures; it reaches only 75% overall accuracy and 0% on the `both changed` arm.

Classification:

> `FACTORIZED_WORLD_SELF_MODEL_COMPOSES_UNSEEN_JOINT_RESPONSES_AND_ATTRIBUTES_CHANGE_WITH_FEWER_SCALAR_POKES`

This is a compositional representation result, not spontaneous discovery of a self/world ontology. The factorization is anchored by the calibration design.

## G6B — poking cannot break a true observational equivalence

Construct two causal stories:

```text
WORLD story:  (W XOR delta) XOR S
SELF story:    W XOR (S XOR delta)
```

They produce the same response for every possible action. Therefore any adaptive probing policy receives the same complete transcript in both stories.

Across 64 generated pairs:

```text
post-change signature equivalence              1.0
adaptive full-transcript equivalence           1.0
best transcript-only attribution, equal prior  0.5
one privileged efference bit control           1.0
```

Classification:

> `POKING_ALONE_CANNOT_IDENTIFY_SELF_VS_WORLD_WHEN_CAUSAL_STORIES_ARE_OBSERVATIONALLY_EQUIVALENT`

This is the clean fence around the earlier slogan. Interventions add information only when the competing hypotheses predict different intervention consequences. Efference copy, proprioception, known self-update dynamics, or another causal asymmetry can break the equivalence; intelligence alone cannot.

## G6C — PCA can miss source axes; ICA can separate them but cannot name `self`

The next audit connects the self/world problem to blind source separation.

Two exactly independent, equal-variance, sparse non-Gaussian sources are orthogonally mixed into two observed channels. Because the covariance is exactly isotropic, PCA sees equal eigenvalues and has no preferred source axis.

A tiny dependency-free 2-D ICA audit then scans whitened rotations using fourth-order non-Gaussianity (absolute excess kurtosis).

Executed CI result across eight mixing angles:

```text
max PCA eigenvalue ratio                         1.0
PCA preferred axis                               false
mean ICA source recovery |correlation|           1.0
worst ICA source recovery |correlation|          1.0
max ICA angle error                              0.0 deg
self-label accuracy without anchor, equal prior  0.5
self-label accuracy with efference timing        1.0
```

Classification:

> `HIGHER_ORDER_SOURCE_STATISTICS_SEPARATE_MIXED_SIGNALS_BUT_EFFERENCE_IS_NEEDED_TO_NAME_SELF`

The important distinction is:

```text
source separation      tells us distinct generators exist
semantic attribution   tells us which generator is "mine"
```

ICA recovers independent non-Gaussian sources only up to sign and permutation, so blind separation alone cannot attach the semantic label `self`. The efference timing marker anchors that label.

There is also a hard counterexample: if the latent vector is isotropic Gaussian, every orthogonal rotation has the same distribution. PCA remains degenerate and ICA has no higher-order non-Gaussian structure with which to prefer the original axes.

## What this earns

The combined Gate 6 result is narrower and more useful than "the machine has a self."

It earns these statements:

1. A correct factorization can compress a joint response family and generalize to unseen combinations.
2. Active pokes can cheaply determine which factor changed when the factors make distinguishable predictions.
3. No probing policy can distinguish exactly intervention-equivalent causal stories.
4. Statistical source properties can break some mixing symmetries before intervention enters.
5. Statistical separation does not by itself provide semantic ownership; a causal anchor is still required.

## What it does not earn

This is not a biological neuron model, a theory of consciousness, a new PCA/ICA result, or evidence that brains literally implement this XOR construction. The source families and calibration are engineered to isolate identifiability.

The next useful question is temporal and ecological rather than philosophical: many mixed signal trains arrive with different recurrence, latency, controllability, persistence, novelty, and task value. Under a limited representation/transport budget, which ones should become durable objects, which should remain transient, and which should reshape the routing operator?
