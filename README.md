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
| **G8A — WidePresent** | can a frozen point miss hidden moving state that ordered history recovers? | point **50%**, unordered same samples **50%**, ordered window **100%**, reversible probe **100%** |
| **G8B — coordinate-invariant object** | can an object survive complete physical relabeling? | raw coordinate / frequency / passive graph each **25%**; intrinsic intervention-response signature **100%** over 384 remappings |
| **G8C — nonlinear attractors** | can a persistent operator later reactivate distinct basins, and does frequency identify them? | 3 stable basins; half-cue reactivation **96%**; 3-bit return **94%**, 10-bit return **13%**; frequency-only identity **33.3%** |

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

Gate 7A asks where to spend a fixed conductance budget. A loud, frequent fly is
deliberately cheap to ignore; a quiet context stream becomes valuable only
together with partner/alarm streams. Joint consequence allocation nearly
matches the oracle and reallocates after the ecology changes.

Gate 7B removes clean command/partner coordinates. Static ICA recovers the two
generators almost perfectly, but static statistics have no time arrow. Time
reversal leaves ICA contrast unchanged while flipping the discovered relation
from +5 to −5. An efference record anchors the command side.

A plain raw lag-correlation attacker also recovers the delay perfectly, an
explicit negative: the easy dependency itself does not require fancy source
separation.

> **Static statistics can tell us which generators exist. Temporal structure
> can tell us how they are related. A causal anchor tells the machine which side
> issued the action.**

See [`GATE7.md`](GATE7.md).

## Gate 8: the object is not the coordinate

Gate 8 begins from the attractor / engram / frequency intuition but keeps the
terms separate.

`G8A` gives `WidePresent` a precise role. Two moving states can have the same
instantaneous observation and even the same unordered recent samples, while the
**ordered** recent trajectory identifies the future perfectly.

`G8B` then embeds four synthetic objects under every permutation of their
physical coordinates. Frequency, passive graph shape, and raw coordinate
matching all fall to chance. An intrinsic action-response signature survives
all remappings.

`G8C` finally introduces a nonlinear Hopfield-style recurrent system and earns
the word `attractor` in the narrow dynamical sense. Three supplied patterns are
stable fixed points; nearby perturbations return, distant perturbations escape,
and a half-pattern cue reactivates the correct state **96%** of the time after
activity has otherwise been absent.

All three attractors are fixed points, so their oscillation frequency is the
same: zero. Frequency-only identity is therefore **1/3**.

> **Frequency can be one coordinate of a dynamical fingerprint. It is not the
> identity of a memory object. A stronger object is an equivalence class of
> recoverable dynamics and action-response relations over changing
> implementation coordinates.**

See [`GATE8.md`](GATE8.md).

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
python -m experiments.gate8a_wide_present --check
python -m experiments.gate8b_coordinate_invariant_object --check
python -m experiments.gate8c_nonlinear_attractor_basins --check
python -m unittest discover -s tests -v
```

## What this repo does not claim

The worlds are synthetic. Several response laws, novelty priors, allocation
costs, interventions, and causal anchors are engineered. Gate 4 still uses
labels during calibration. Gate 7B is a linear mixture with a hand-built
delayed responder. Gate 8B uses exact coordinate relabeling; Gate 8C uses a
small engineered Hopfield-style network with supplied patterns.

There is no claim here of general intelligence, biological equivalence,
subjective experience, a biological engram model, or a new PCA/ICA/caching/
attractor theorem.

Negative results are part of the architecture: cheap surprise can be blind;
novelty makes recognition costly; intervention-equivalent hypotheses remain
indistinguishable; simple lagged correlation is enough for the easy delayed
response; and distinct attractors can have exactly the same frequency.

## Next — identity under real drift

Exact coordinate permutation is the easy invariance because the map is known to
the experimenter and the whole operator is relabeled consistently.

The next gate removes that crutch:

> **Can a useful dynamical object remain identifiable while the substrate
> slowly rewrites itself and no explicit old→new coordinate map is supplied?**

This is the harder version of a memory being persistent while its physical
realization remains in flux.

See [`NEXT.md`](NEXT.md).

**Attackers first, claims second.**
