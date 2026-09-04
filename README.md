# AlternativeNeuron

**A bounded machine that learns by poking what it cannot fully observe.**

> A bounded machine need not represent everything centrally. It can spend
> measurements only when prediction fails, use interventions as additional
> senses, write useful answers into persistent state, and slowly reshape the
> operator so repeated experience becomes cheaper to handle.

AlternativeNeuron is a small falsifiable synthesis of the recent
`GeometricNeuronV24`, `ReadWrite`, `LentoOrava`, `Operaattori`,
`OperaattoriJako`, and `OutoSynapsi` line. It is **not** presented as a literal
biological neuron or a theory of consciousness.

The core question is simple:

```text
observation:   what happened?
intervention:  what happens if I do this?
```

If two hidden states look identical through the passive channel but react
differently to the same reversible poke, the action-response pair is an
additional **sense**.

## Current receipt

Gates 0–6C are executable in CI.

| gate | question | executed result |
|---|---|---|
| **G0 — intervention as sense** | can a state-dependent poke expose hidden state absent from passive observation? | passive **12.5%**; active **100% in 3 pokes**; state-independent control **12.5%** |
| **G1 — medium memory** | can an identified persistent event avoid being rediscovered? | **1536 → 192 pokes**, 8× fewer; deliberate silent-switch attack falls to **50%** |
| **G2 — slow structure** | can repeated useful traffic reshape a fixed transport budget? | mean identification cost **3.000 → 1.061**; shuffled traffic **5.466** |
| **G3 — composition** | do fast poke + medium memory + slow structure stack? | task stays at **100%**; cost **1536 → 192 → 67.93** |
| **G4 — learned poke semantics** | can the response model be learned from scalar consequences? | labeled calibration then **100% in 3 pokes/context**; shuffled model **12.5%** |
| **G5 — unlabeled internal objects** | can recurring response patterns earn scarce durable slots because they save future sensing? | probe-value memory **9.355** recurring probes/event vs frequency **10.245**, LRU **10.615**, oracle **9.264** |
| **G5B — stronger cache attacker** | does the effect survive frequency × independent sensing value and error penalties? | **9.355** vs attacker **9.909**, oracle **9.264** |
| **G6 — world vs self/operator** | can a factorized response model compose unseen joint states and identify which factor changed? | **132 bits** reconstruct all **32** world/self combinations; cause and pair accuracy **100%**; **3.914** probes for cause, **4.674** for pair |
| **G6B — nonidentifiability** | can poking separate two causal stories that predict the same response to every possible action? | **no**: full adaptive transcripts are identical; best equal-prior attribution **50%**; one efference bit restores **100%** |
| **G6C — PCA / ICA audit** | can statistical source properties separate mixed signals before semantic attribution? | PCA exactly degenerate; fourth-order ICA recovers sources **1.000 correlation**; `self` remains **50/50** until efference timing anchors it |

See [`GATE5.md`](GATE5.md) and [`GATE6.md`](GATE6.md) for the assays, attackers and claim boundaries.

## The three clocks

The current architecture uses three different jobs rather than three copies of
memory:

```text
FAST
    resolve the current ambiguity
    choose the next poke from scalar consequences

MEDIUM
    keep a currently trusted answer
    do not pay to rediscover it every step

SLOW
    change the operator / cost landscape
    make repeatedly useful future questions cheaper
```

This closes the loop:

```text
surprise
   ↓
active poke
   ↓
scalar consequence
   ↓
fast belief
   ↓
medium memory
   ↓
repeated useful traffic
   ↓
slow operator change
   └──────────────→ changes future sensing
```

## Gate 5: memory changes measurement geometry

Gate 5 has 12 reversible binary poke channels, six recurring unlabeled response
patterns, 15% unique one-off accidents, and only `K=4` durable prototype slots.
Temporary evidence decays after 128 events.

A plain heavy-hitter remembers what recurs most. The proposed policy instead
asks which **set of prototypes** minimizes expected future scalar sensing cost.
It may leave capacity unused.

Across eight seeds:

```text
                         recurring probes     durable occupancy
LRU                           10.615                 0.793
random                        10.656                 0.750
frequency                     10.245                 0.993
frequency × solo saving        9.909                 0.992
probe-value                    9.355                 0.742
oracle                         9.264                 0.750
```

The probe-value policy uses roughly **three of four available slots**, almost
exactly like the future-aware oracle. The reason is non-additivity: adding a
stored hypothesis changes the questions and evidence threshold needed to
recognize the others.

> **Under bounded active observation, internal objects alter the future
> measurement geometry. Memory capacity and useful memory are not the same
> thing.**

A separate exhaustive audit over all `2^12` signatures shows the open-world
price: a closed-world cache recognizes familiar things in 1.67 probes but false
accepts genuinely novel signatures with probability 1.0. At the declared
`alpha=0.01`, known recognition costs 5 probes and novel false acceptance falls
to about 0.00568.

## Gate 6: separation is not ownership

Gate 6 lets both an external world state `x` and an internal operator state
`theta` affect poke consequences:

```text
R(x, theta, a) = W(x,a) XOR S(theta,a)
```

A factorized calibration stores 132 bits instead of a 384-bit full joint table
and reconstructs every one of the 32 world/self combinations exactly. It then
identifies whether the world, self/operator, both, or neither changed with 100%
accuracy in the synthetic family.

But Gate 6B constructs two stories that are exactly equivalent under **every**
available intervention:

```text
(W XOR delta) XOR S
W XOR (S XOR delta)
```

No adaptive intelligence can distinguish them from the poke transcript because
the transcript itself is identical. A privileged causal asymmetry such as an
efference record breaks the tie.

Gate 6C then connects that fence to blind source separation. Two independent,
equal-variance non-Gaussian sources are orthogonally mixed. Their covariance is
exactly isotropic, so PCA has no preferred axis. A tiny dependency-free 2-D ICA
audit uses fourth-order statistics to recover both generators perfectly across
eight mixing angles.

Yet ICA still returns the sources only up to sign and permutation:

```text
source separation      distinct generators exist
semantic attribution   which generator is mine?
```

Without an anchor, the `self` label remains 50/50 under a balanced prior. With
efference timing, it becomes 100% in this construction. If the latent sources
were isotropic Gaussian, even ICA would lose the original axes because every
orthogonal rotation has the same distribution.

So the current boundary is:

> **Statistics can separate some mixed generators. Intervention can separate
> some causal hypotheses. Neither automatically supplies semantic ownership.**

## Run it

No third-party packages are required.

```bash
python run_gates.py --check
python -m experiments.gate5_selective_objects --check
python -m experiments.gate5b_cost_aware_attacker --check
python -m experiments.gate6_self_world_attribution --check
python -m experiments.gate6b_self_world_nonidentifiability --check
python -m experiments.gate6c_blind_source_separation --check
python -m unittest discover -s tests -v
```

Machine-readable Gate 0–5B receipts live under [`results/`](results/). Gates
6–6C also print deterministic JSON receipts and are checked directly in CI.

## What the repo does not claim

The response families are synthetic. The Gate 5 novelty prior is explicit and
hand chosen. The Gate 6 factorization and causal anchor are engineered. Gate 4
still uses labels during calibration. There is no claim here of general
intelligence, biological equivalence, subjective experience, or a new
PCA/ICA/caching theorem.

Negative results remain part of the architecture: medium memory fails when the
cheap surprise channel cannot detect the relevant state change; open-world
recognition becomes expensive when novelty must be treated seriously; exact
intervention-equivalence cannot be solved by additional clever probing.

## Next — signal ecology

The next experiment moves from two clean sources to many mixed **signal trains**
with different properties:

```text
new / transient
old / recurring
fast / delayed
self-anchored / externally driven
high variance / low variance
frequent / rare
useful / distracting
```

The question is no longer merely "can I separate sources?" It is:

> **Under a fixed representation and transport budget, which sources deserve
> durable objects, which should remain transient, and which repeated traffic
> should reshape the operator?**

That is where Gate 5 memory selection, Gate 2 structural allocation, and Gate 6
source/causal identifiability finally meet.

See [`NEXT.md`](NEXT.md) for the preregistered attack.

**Attackers first, claims second.**
