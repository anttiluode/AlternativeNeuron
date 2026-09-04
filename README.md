# AlternativeNeuron

**Antti and teh AI the gang figures it all out once again. Sol thinking repo.**

> A bounded machine need not represent everything centrally. It can spend
> measurements only when prediction fails, use interventions as additional
> senses, write the answer into persistent state, and slowly reshape the
> operator so repeated experience becomes cheaper to handle.

This repo is an attempt to make that sentence executable without pretending it
is already a biological neuron or a new theory of intelligence.

It starts where the recent line converged:

- **GeometricNeuronV24** — scale/address as a question; surprise decides when to
  pay; persistent WRITE changes future sensing; Gate 6C adds the conditional
  same-field write-timescale boundary.
- **ReadWrite** — a state-dependent response to a known write can expose hidden
  state that passive reading cannot distinguish.
- **LentoOrava / PulseTriage** — reversible interventions plus one scalar global
  consequence can localize useful action.
- **Operaattori** — persistent structure compiles a transport operator.
- **OperaattoriJako** — separate direct transport sensitivity from the extra
  effect created when nonlinear state reacts.
- **OutoSynapsi** — repeated traffic under a fixed resource budget can reshape
  an operator and therefore future transport cost.

AlternativeNeuron puts those ingredients in **one tiny falsifiable machine**.

## The object

```text
                   SLOW STRUCTURE theta
               fixed transport budget
                         |
                         v
                 probe cost / routing
                         |
        +----------------+----------------+
        |                                 |
        v                                 |
FAST exploratory state                    |
candidate set -> choose poke              |
        |                                 |
        v                                 |
one scalar consequence                    |
        |                                 |
        v                                 |
resolve hidden context                    |
        |                                 |
        v                                 |
MEDIUM persistent memory                  |
        |                                 |
        +------ repeated useful traffic --+
```

Observation asks:

```text
what happened?
```

A reversible intervention asks:

```text
what happens if I do this?
```

If two states are identical through the passive channel but react differently
to the same poke, the poke is an additional **sense**.

## Run

No third-party dependencies are required.

```bash
python run_gates.py --check
python -m unittest discover -s tests -v
```

The machine-readable receipt is [`results/GATES.json`](results/GATES.json).
GitHub Actions reruns the unit tests and full gate ladder on every push.

## Executed receipt

Gates 0–4 are green in CI.

| gate | question | result |
|---|---|---|
| **G0 intervention-as-sense** | can a state-dependent poke resolve states the passive channel cannot? | passive **12.5%**, active poke **100% in 3 pokes**, state-independent poke **12.5%** |
| **G1 medium memory** | can remembering an identified persistent event avoid paying again? | **1536 -> 192 pokes**, an **8x reduction**, at 100% accuracy on visible event changes |
| **G1 negative** | does that memory work when the cheap surprise channel cannot see the change? | **no**: silent same-group switch falls to **50%** accuracy |
| **G2 slow structure** | can repeated useful probe traffic reshape a fixed-budget transport operator? | mean identification cost **3.000 -> 1.061**; shuffled traffic gives **5.466** |
| **G3 composition** | do fast poke + medium memory + slow structure stack? | 512-step task stays at **100%** accuracy; adapted total probe cost **67.93** vs **192** with frozen structure and **1536** with no memory |
| **G4 learned poke semantics** | can the machine learn what its pokes mean from scalar consequences rather than receive the response codebook? | 192-poke labeled calibration, then **100%** test accuracy in **3 pokes/context**; shuffled calibration **12.5%**; amortized total **3x cheaper** than exhaustive reuse |

The useful picture is not "three kinds of memory." It is three different jobs:

```text
FAST
    resolve the current ambiguity

MEDIUM
    keep the answer while the event remains trustworthy

SLOW
    alter the cost landscape through which future ambiguity is resolved
```

Medium memory stores a fact. Slow memory is closer to **history-made-routing**:
what repeatedly mattered changes the operator through which later evidence is
acquired.

## Gate 0 — poke as an extra sense

There are 16 hidden contexts. The free passive channel reveals only which half
of the context space the machine occupies, leaving eight possibilities.

A reversible poke returns one binary scalar consequence. Seven poke channels
have different state-dependent responses; five are decoys. The fast state is
only the current candidate set. It chooses the next poke by

```text
expected information gain / current transport cost
```

With the real state-dependent response, every context is resolved in exactly
three pokes. Remove state dependence while keeping the scalar channel and the
accuracy falls back to the passive 12.5%.

Classification:

> `STATE_DEPENDENT_INTERVENTION_RESCUES_PASSIVE_AMBIGUITY`

This is the ReadWrite condition in its smallest behavioral form: **the response
to action can carry information absent from passive observation.**

## Gate 1 — remembering changes future sensing

Contexts persist for eight steps. Event boundaries in this positive arm change
the cheap passive group, so HOME can notice that its remembered context should
be questioned.

Without memory, every one of 512 steps buys three pokes: **1536** total.

With medium memory, only the 64 event onsets buy pokes: **192** total.

But the attack is deliberately kept. Change context `0 -> 1` without changing
the passive group and HOME stays quiet. The machine continues believing `0`
and gets only **50%** accuracy across that sequence.

Classification:

> `MEMORY_AMORTIZES_PERSISTENT_EVENTS_BUT_CHEAP_SURPRISE_HAS_A_BLIND_SPOT`

So "prediction error decides when to look" is only as good as the prediction
error channel.

## Gate 2 — memory becomes operator

Across 1024 identification episodes, three poke channels carry all useful
traffic. Slow consolidation does not store episode identities. It changes the
**transport conductance** of the channels under a fixed total budget.

For channel conductance `g`, poke cost is `1/g`. The first rule uses

```text
g_a proportional to sqrt(traffic_a + background)
```

and exactly preserves `sum(g)`.

Mean cost of a three-poke identification:

```text
frozen uniform operator       3.000
traffic-adapted operator      1.061
shuffled-traffic attacker     5.466
```

Classification:

> `REPEATED_PROBE_TRAFFIC_RESHAPES_FIXED_BUDGET_TRANSPORT_AND_CHANGES_FUTURE_SENSING_COST`

The number of scalar pokes does **not** fall in this gate. Structure makes the
repeatedly useful channels cheaper under the same total conductance budget.
That distinction matters.

## Gate 3 — the three clocks compose

On the 512-step stream:

```text
active, no memory, frozen structure       cost 1536.00
active + medium memory, frozen             cost  192.00
active + medium memory + adapted slow      cost   67.93
same memory + shuffled slow structure      cost  349.84
```

All active arms remain at 100% accuracy on the visible-transition task.

Classification:

> `FAST_POKE_MEDIUM_MEMORY_AND_SLOW_STRUCTURE_COMPOSE`

So the first synthetic loop is closed:

```text
surprise
   -> active poke
   -> resolved state
   -> persistent memory
   -> useful probe traffic
   -> slow operator change
   -> cheaper future probing
```

## Gate 4 — the poke learns a meaning

Gate 0 cheated by handing the active policy the poke-response codebook. Gate 4
hides it.

A new world assigns each hidden context a deterministic random binary response
signature across 12 poke actions. During calibration the machine receives a
context label and can discover that context's signature **only by scalar
interventions**.

Executed result:

```text
labeled scalar calibration             192 pokes
active test phase                      384 pokes / 128 contexts
mean active test cost                  3 pokes/context
active test accuracy                   1.000
shuffled learned response model        0.125 accuracy
active total incl. calibration         576
exhaustive total                       1728
amortized reduction                    3.0x
```

Classification:

> `SCALAR_CALIBRATION_LEARNS_POKE_SEMANTICS_AND_ACTIVE_REUSE_AMORTIZES_IT`

This removes the preloaded-response cheat but **not the ontology cheat**. During
calibration somebody still tells the system "this is context 7." It learns how
context 7 reacts; it does not invent context 7.

That makes the next question much sharper:

> **Can recurring action-response patterns earn their own internal objects
> without supplied labels, when durable memory has fewer slots than the number
> of things the machine encounters?**

A cache-everything/LRU/random-replacement mechanism with the same K slots is the
attacker. The selective system must earn lower held-out probe cost, fewer false
consolidations, and better adaptation after the stream changes.

And after that comes the nastier self/world problem: if slow structure changes
the operator, the same world can produce a different poke response because the
machine changed itself. Can it distinguish **the world changed** from **I changed
how I touch the world**?

See [`THEORY.md`](THEORY.md) for that boundary.

## PAC, not PCA

Phase-amplitude coupling (**PAC**) is a cross-frequency phenomenon in which the
phase of a slower oscillation is related to the amplitude of a faster one.
Principal component analysis (**PCA**) is linear dimensionality reduction.
Easy acronym collision; completely different things.

The fast/medium/slow architecture here is **not PAC**. There are currently no
oscillators. PAC is only an interesting analogy for coupled timescales: a future
version could let a slow contextual/structural rhythm gate the gain, threshold,
or budget of fast exploratory pulses. That would need its own experiment.

## The qualia thought, kept where it belongs

The poke adds a real computational degree of freedom:

```text
receive evidence
```

becomes

```text
choose an act -> receive the consequence of that act
```

That action-conditioned evidence is a legitimate place to study agency,
self/world distinction, counterfactual sensing or sensorimotor contingencies.
Nothing in this repo measures subjective experience or provides evidence for
qualia. The philosophical connection can motivate questions; it cannot be
smuggled into the results.

## Claim boundary

This world is intentionally tiny and partly designed to be answerable. HOME
sees a coarse group; Gate 4 calibration receives context labels; the structural
law is hand chosen; there is no neural training and no claim of general
intelligence. The silent-switch failure is retained because it tells us exactly
where the architecture is currently blind.

**Attackers first, claims second.**
