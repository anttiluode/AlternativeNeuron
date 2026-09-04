# Gate 5 — when does a recurring response deserve to become an object?

Gate 4 learned the meaning of pokes from scalar consequences, but calibration
still supplied context labels. Gate 5 removes those labels and asks a narrower
question:

> Can recurring action-response structure earn scarce durable memory because
> storing it reduces future sensing cost?

This is **not** a claim that the toy discovers human concepts. It is a bounded
active-sensing/cache experiment in which internal objects are unlabeled response
signatures.

## Assay

The world exposes 12 reversible binary poke channels. Six response signatures
recur; 15% of events are unique one-off signatures. No recurring signature has
an external name during learning.

The machine has:

- a 128-event decaying temporary trace;
- only `K=4` durable prototype slots;
- an explicit open-world novelty model;
- two 600-event phases with changed recurrence frequencies.

The six recurring patterns deliberately differ in **recognition value**. Stored
alone at the declared `alpha=0.01` novelty tolerance, they need roughly
`2, 3, 4, 6, 8, 12` scalar consequences to certify. Thus a frequently recurring
pattern can still be useless to store if remembering it does not shorten the
next interrogation.

## Policies

All non-oracle policies get the same observation stream and the same four
possible durable slots.

| policy | rule |
|---|---|
| LRU | remember what was seen most recently |
| random | replace a random slot |
| frequency | keep recent heavy hitters |
| frequency × solo saving | keep patterns with large recurrence × independent probe saving |
| **probe value** | choose the prototype subset that minimizes recent expected scalar sensing cost |
| oracle | future-aware ceiling |

The probe-value policy is allowed to leave capacity unused. Empty memory is not
a failure if an additional prototype would make the recognition problem worse.

## Gate 5 result

Across eight deterministic seeds, the first audit gave:

| policy | recurring probes/event | false consolidations | durable recurring occupancy |
|---|---:|---:|---:|
| LRU | 10.615 | 181.875 | 0.793 |
| random | 10.656 | 181.625 | 0.750 |
| frequency | 10.245 | 0 | 0.993 |
| **probe value** | **9.355** | **0** | **0.742** |
| oracle | 9.264 | 0 | 0.750 |

The striking part is the occupancy. The value policy uses about three of the
four available slots, almost exactly like the future-aware oracle. In the
representative seed it stores three prototypes and deliberately leaves one slot
empty.

Classification:

> `PROBE_VALUE_SELECTIVE_OBJECTS_BEAT_RECENCY_RANDOM_AND_FREQUENCY_CACHE_UNDER_DECLARED_NOVELTY_PRIOR`

The machine-readable receipt is
[`results/GATE5_SELECTIVE_OBJECTS.json`](results/GATE5_SELECTIVE_OBJECTS.json).

## Gate 5B — stronger boring attacker

Plain frequency is an easy attacker, so the post-result audit adds a stronger
one: rank each pattern by

```text
recent frequency × probe saving when stored alone
```

This attacker already knows that a frequent object that saves zero sensing is
not worth a slot.

It also uses **conservative cost**: any false early recognition is charged as a
full 12-probe scan, so errors can never make a policy look artificially cheap.

| policy | conservative recurring probes/event | mean slot occupancy |
|---|---:|---:|
| frequency × solo saving | 9.909 | 0.992 |
| **joint probe value** | **9.355** | **0.742** |
| oracle | 9.264 | 0.750 |

So the joint policy remains about 5.6% cheaper than the already cost-aware
independent attacker and sits about 1% above the future-aware oracle on this
metric.

Classification:

> `JOINT_PROBE_VALUE_SELECTION_BEATS_FREQUENCY_TIMES_SOLO_SAVING_WITH_ERRORS_CHARGED_AS_FULL_SCANS`

Receipt:
[`results/GATE5B_COST_AWARE_ATTACKER.json`](results/GATE5B_COST_AWARE_ATTACKER.json).

## The unexpected result: memories interact

A durable prototype is not an independent cache line.

Under the oracle three-prototype set, the scalar consequences needed to certify
an object change relative to storing that object alone:

| prototype | stored alone | inside oracle set |
|---|---:|---:|
| P0 | 2 | 3 |
| P1 | 3 | 5 |
| P2 | 4 | 7 |
| P3 | 6 | 12 / unstored |
| P4 | 8 | 12 / unstored |
| P5 | 12 | 12 / unstored |

Adding hypotheses changes which questions are useful and how much evidence is
needed before a cached identity is safe to accept. In this assay, **more durable
memory can make an existing memory more expensive to recognize**.

That is why the best finite memory can rationally leave a slot unused.

This is the piece worth carrying forward: memory is not merely storage
capacity. Under bounded active observation, remembered objects alter the future
**measurement geometry**.

## The open-world novelty tax

There is another unavoidable boundary. If the machine assumes that one of its
cached prototypes *must* be the answer, recognition is wonderfully cheap — and
catastrophically wrong for novelty.

The exact audit enumerates all `2^12` response signatures under the declared
novelty prior:

| novelty rule | known probes | novel false accept |
|---|---:|---:|
| closed world | 1.67 | **1.000** |
| alpha = 0.10 | 3.00 | 0.0413 |
| alpha = 0.03 | 3.67 | 0.0221 |
| **alpha = 0.01** | **5.00** | **0.00568** |
| alpha = 0.003 | 7.00 | 0.00139 |
| alpha = 0.001 | 9.00 | 0.000374 |

So the slogan "memory makes sensing cheaper" needs a qualifier:

> Memory makes recognition cheaper only relative to a declared belief about
> novelty, tolerated error, or structured response family.

Without that, a closed-world recognizer simply calls every unfamiliar thing
something it already knows.

## What Gate 5 earned — and did not earn

It earned a small mechanism:

```text
unlabeled scalar consequences
        -> temporary recurrence evidence
        -> estimate future sensing value
        -> selectively make some patterns durable
        -> those durable patterns change later interrogation cost
```

It did **not** earn claims about general concept formation, biological neurons,
consciousness, or a new caching theorem. The response family and admission rule
are synthetic and hand designed.

The next hard gate is different: once slow structure changes the action-response
operator itself, can the machine tell **the world changed** from **I changed how
I touch the world**?
