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

The core question is simpler:

```text
observation:   what happened?
intervention:  what happens if I do this?
```

If two hidden states look identical through the passive channel but react
differently to the same reversible poke, the action-response pair is an
additional **sense**.

## Current receipt

Gates 0–5B are executable. The newest result removes the supplied object labels
and gives the machine fewer durable memory slots than recurring response
patterns.

| gate | question | executed result |
|---|---|---|
| **G0 — intervention as sense** | can a state-dependent poke expose hidden state absent from passive observation? | passive **12.5%**; active **100% in 3 pokes**; state-independent control **12.5%** |
| **G1 — medium memory** | can an identified persistent event avoid being rediscovered? | **1536 → 192 pokes**, 8× fewer; deliberate silent-switch attack falls to **50%** |
| **G2 — slow structure** | can repeated useful traffic reshape a fixed transport budget? | mean identification cost **3.000 → 1.061**; shuffled traffic **5.466** |
| **G3 — composition** | do fast poke + medium memory + slow structure stack? | task stays at **100%**; cost **1536 → 192 → 67.93** |
| **G4 — learned poke semantics** | can the response model be learned from scalar consequences? | labeled calibration then **100% in 3 pokes/context**; shuffled model **12.5%** |
| **G5 — unlabeled internal objects** | can recurring response patterns earn scarce durable slots because they save future sensing? | probe-value memory **9.355** recurring probes/event vs frequency **10.245**, LRU **10.615**, oracle **9.264** |
| **G5B — stronger attacker** | does the effect survive a frequency × independent sensing-value cache and error penalties? | **9.355** vs cost-aware attacker **9.909**, oracle **9.264** |

CI reruns the gate ladder and tests on every PR.

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

## The newest thing: memory changes measurement geometry

Gate 5 has 12 reversible binary poke channels, six recurring unlabeled response
patterns, 15% unique one-off accidents, and only `K=4` durable prototype slots.
Temporary evidence decays after 128 events.

A plain heavy-hitter remembers what recurs most. The proposed policy instead
asks which **set of prototypes** minimizes expected future scalar sensing cost.
It may leave capacity unused.

That turns out to matter.

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

The probe-value policy ends up using roughly **three of four available slots**,
almost exactly like the future-aware oracle.

Why can an empty memory slot be optimal?

Because remembered objects are **not independent cache lines**. Adding another
stored hypothesis changes the questions and evidence threshold required to
recognize the others. In the oracle set:

```text
prototype       alone       inside the stored set
P0                2                 3 probes
P1                3                 5
P2                4                 7
```

So more memory can make an existing memory more expensive to recognize.

That is the result worth carrying forward:

> **Under bounded active observation, internal objects alter the future
> measurement geometry. Memory capacity and useful memory are not the same
> thing.**

See [`GATE5.md`](GATE5.md) for the assay, attackers, receipts and boundaries.

## The open-world novelty tax

A closed-world cache can recognize familiar things extremely quickly only by
assuming that every future thing must already be in memory.

Gate 5 explicitly audits that assumption over all `2^12` response signatures:

| rule | known probes | false accept on novelty |
|---|---:|---:|
| closed world | 1.67 | **1.000** |
| alpha = 0.10 | 3.00 | 0.0413 |
| alpha = 0.03 | 3.67 | 0.0221 |
| **alpha = 0.01** | **5.00** | **0.00568** |
| alpha = 0.003 | 7.00 | 0.00139 |
| alpha = 0.001 | 9.00 | 0.000374 |

So “memory makes recognition cheap” always carries a price: a novelty prior,
a tolerated false-accept rate, additional verification, or exploitable structure
in the response family.

## Run it

No third-party packages are required for the current gates.

```bash
python run_gates.py --check
python -m experiments.gate5_selective_objects --check
python -m experiments.gate5b_cost_aware_attacker --check
python -m unittest discover -s tests -v
```

Machine-readable receipts:

- [`results/GATES.json`](results/GATES.json) — Gates 0–4
- [`results/GATE5_SELECTIVE_OBJECTS.json`](results/GATE5_SELECTIVE_OBJECTS.json)
- [`results/GATE5B_COST_AWARE_ATTACKER.json`](results/GATE5B_COST_AWARE_ATTACKER.json)

## What the repo does not claim

The current response families are synthetic. The Gate 5 novelty prior is
explicit and hand chosen. The admission rule is engineered. Gate 4 still uses
labels during calibration. There is no claim here of general intelligence,
biological equivalence, subjective experience, or a new caching theorem.

The negative results remain part of the architecture: medium memory fails when
the cheap surprise channel cannot detect the relevant state change; open-world
recognition becomes expensive when novelty must be treated seriously.

## Next gate — world or self?

Slow structure currently changes the **cost** of a poke. The next experiment
will let it change the actual action-response operator.

Then the same scalar surprise can have two causes:

```text
WORLD CHANGE
    hidden state changed; my operator did not

SELF CHANGE
    hidden state stayed fixed; I changed how I touch it
```

The next gate asks whether a factorized machine can tell those causes apart and
update the correct model component, beating a monolithic adaptive predictor
with the same state budget.

That would earn only a narrow computational self-model:

> some changes in my sensations happened because **I changed my own sensing /
> acting operator**.

See [`NEXT.md`](NEXT.md) for the preregistered attack and the later PAC-style
rhythmic fork.

**Attackers first, claims second.**
