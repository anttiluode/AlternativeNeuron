# AlternativeNeuron

**A bounded machine that learns by poking what it cannot fully observe.**

> A bounded machine need not represent everything centrally. It can spend
> measurements only when prediction fails, use interventions as additional
> senses, write useful answers into persistent state, and slowly reshape the
> operator so repeated experience becomes cheaper to handle.

AlternativeNeuron is a small falsifiable synthesis of the recent
`GeometricNeuronV24`, `ReadWrite`, `LentoOrava`, `Operaattori`,
`OperaattoriJako`, and `OutoSynapsi` line. It is **not** presented as a literal
biological neuron, an engram model, or a theory of consciousness.

The core distinction is:

```text
observation:   what happened?
intervention:  what happens if I do this?
```

If two hidden states look identical passively but react differently to the same
reversible poke, the action-response pair is an additional sense.

## Executed gate ladder

| gate | question | result |
|---|---|---|
| **G0 — intervention as sense** | can state-dependent pokes resolve passive ambiguity? | passive **12.5%**; active **100% in 3 pokes**; state-independent control **12.5%** |
| **G1 — medium memory** | can a persistent event avoid rediscovery? | **1536 → 192 pokes**, 8× fewer; deliberate silent-switch attack falls to **50%** |
| **G2 — slow structure** | can repeated useful traffic reshape fixed transport? | mean cost **3.000 → 1.061**; shuffled traffic **5.466** |
| **G3 — composition** | do fast poke + memory + structure stack? | task stays **100%**; cost **1536 → 192 → 67.93** |
| **G4 — learned poke semantics** | can the poke-response model be learned from scalar consequences? | **100% in 3 pokes/context** after calibration; shuffled model **12.5%** |
| **G5 — selective internal objects** | can unlabeled recurring patterns earn scarce memory slots? | probe-value memory **9.355** recurring probes vs frequency **10.245**, LRU **10.615**, oracle **9.264** |
| **G5B — stronger cache attacker** | does joint value survive frequency × solo saving? | **9.355** vs attacker **9.909**, oracle **9.264** |
| **G6 — world vs self/operator** | can a factorized response model compose unseen joint states and attribute change? | **132 bits** reconstruct all **32** combinations; cause/pair accuracy **100%** |
| **G6B — nonidentifiability** | can poking separate causally different stories with identical intervention consequences? | **no**: adaptive transcripts identical; equal-prior attribution **50%**; one efference bit restores **100%** |
| **G6C — PCA / ICA audit** | can source statistics separate mixed generators before semantic naming? | PCA degenerate; ICA recovery **1.000**; `self` stays **50/50** until efference timing anchors it |
| **G7A — signal ecology** | under fixed routing, which already-separated signals deserve structure? | joint consequence cost **0.56965** vs independent-value **0.69623**, variance **0.81079**, oracle **0.56146** |
| **G7B — temporal causal address** | what do static separation, timing, and efference each add? | ICA recovery **0.99992**; +5 response lag recovered **8/8**; time reversal flips it to −5; shuffled timing collapses the peak |

CI reruns the full ladder on every PR.

## The three clocks

```text
FAST
    resolve the current ambiguity
    choose what to read / poke

MEDIUM
    keep currently useful objects
    do not pay to rediscover them every step

SLOW
    change the operator / routing budget
    make repeatedly useful future questions cheaper
```

The intended loop is:

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

Gate 5 found that memory entries are not independent cache lines. Adding a
stored hypothesis can make the others harder to certify, because the future
measurement problem now has more alternatives to distinguish.

That is why the best policy can leave capacity unused: it averages roughly
three useful prototypes despite four available slots, close to the
future-aware oracle.

> **Under bounded active observation, internal objects alter future measurement
> geometry. Memory capacity and useful memory are not the same thing.**

The same gate also exposes an open-world novelty tax: a closed-world cache is
cheap on known things only by assuming novelty away.

See [`GATE5.md`](GATE5.md).

## Gate 6: separation is not ownership

Gate 6 makes both external state and internal operator state affect poke
consequences. A factorized model compresses the joint family and attributes
change correctly in the synthetic assay.

But Gate 6B constructs world-change and self-change stories that predict the
same answer to every available action. No adaptive probing strategy can solve
that because the transcript itself is identical.

Gate 6C then makes the distinction mathematical:

```text
PCA        where is the second-order variance?
ICA        which non-Gaussian generators can be separated?
efference  which recovered generator was tied to my issued action?
```

Blind separation can discover distinct components without supplying semantic
ownership.

See [`GATE6.md`](GATE6.md).

## Gate 7: from sources to causal address

Gate 7A gives every policy the same clean source identities and asks only where
to spend a fixed conductance budget. A loud, frequent fly is deliberately cheap
to ignore; a quiet context stream becomes valuable only together with
partner/alarm streams. Joint consequence allocation nearly matches the oracle
and reallocates after the ecology changes.

Gate 7B removes the clean command/partner coordinates. A command source and a
delayed responder are mixed through regenerated rotations, while an unrelated
fly channel dominates raw variance.

Static ICA recovers the two generators almost perfectly, but static statistics
have no time arrow. Time-reversing the whole dataset changes ICA contrast by
exactly zero while flipping the discovered temporal relation from +5 to −5.
With an efference record, the machine can anchor the command component at zero
lag and give the responder a directed causal address.

The shuffled-timing control reduces the mean command-linked peak from **0.823**
to **0.035** (~23.5×). A plain raw lag-correlation attacker also recovers the
delay perfectly, which is an explicit negative: this easy gate does not require
a fancy architecture merely to detect coupling.

> **Static statistics can tell us which generators exist. Temporal structure
> can tell us how they are related. A causal anchor is what tells the machine
> which side issued the action.**

See [`GATE7.md`](GATE7.md).

## Run it

No third-party packages are required.

```bash
python run_gates.py --check
python -m experiments.gate5_selective_objects --check
python -m experiments.gate5b_cost_aware_attacker --check
python -m experiments.gate6_self_world_attribution --check
python -m experiments.gate6b_self_world_nonidentifiability --check
python -m experiments.gate6c_blind_source_separation --check
python -m experiments.gate7a_signal_ecology_allocation --check
python -m experiments.gate7b_temporal_causal_separation --check
python -m unittest discover -s tests -v
```

## What this repo does not claim

The current worlds are synthetic. Several response laws, novelty priors,
allocation costs, and causal anchors are engineered. Gate 4 still uses labels
during calibration. Gate 7B is a linear mixture with a hand-built delayed
responder. There is no claim here of general intelligence, biological
equivalence, subjective experience, an engram model, or a new PCA/ICA/caching
theorem.

Negative results are part of the architecture: medium memory fails when cheap
surprise cannot detect the relevant change; novelty makes recognition costly;
intervention-equivalent hypotheses remain indistinguishable; and simple lagged
correlation is already enough for the easy delayed-response assay.

## Next — dynamical objects

The next gate asks what should count as the **same internal object** when the
physical coordinates implementing it change.

That is where the attractor / engram / frequency intuition gets a stricter
form:

```text
instantaneous state      may be ambiguous
ordered trajectory       may reveal hidden dynamical state
frequency / spectrum     may be one useful coordinate
causal response          may be another
substrate neuron IDs     should not be the identity if dynamics remap
```

See [`NEXT.md`](NEXT.md) for the preregistered `WidePresent` / substrate-remap
attack.

**Attackers first, claims second.**
