#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
import random
from collections import Counter, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from alternative_neuron.prototypes import (
    NoveltyPrior,
    OpenWorldRecognizer,
    PrototypeRecognition,
    Signature,
)


N_ACTIONS = 12
K = 4
ALPHA = 0.01
WINDOW = 128
PHASE_LENGTH = 600
SEEDS = tuple(range(8))

# The novelty model is explicit.  Novel signatures are independent draws from
# these bit marginals.  Rare responses therefore carry more evidence that a
# partial signature is a known prototype.
PRIOR = NoveltyPrior(
    (0.08, 0.12, 0.18, 0.22, 0.28, 0.35, 0.42, 0.50, 0.58, 0.65, 0.75, 0.85)
)

# Six unlabeled recurring response patterns.  Under ALPHA=.01 and a single
# stored prototype they need approximately 2,3,4,6,8,12 scalar consequences to
# certify.  That variation is deliberate: recurrence frequency alone is not
# the same thing as sensing value.
RECURRING: tuple[Signature, ...] = tuple(
    tuple(int(bit) for bit in text)
    for text in (
        "110000101110",
        "100010010011",
        "001100001011",
        "010000011111",
        "000010010111",
        "000000011111",
    )
)

# Each phase reserves 15% probability for one-off accidents.  The second phase
# changes recurrence statistics; notably P5 becomes common despite being hard
# to certify before a full 12-bit scan.
PHASE_PROBABILITIES = (
    (0.10, 0.10, 0.16, 0.20, 0.22, 0.07),
    (0.05, 0.20, 0.07, 0.08, 0.25, 0.20),
)


def signature_name(signature: Signature) -> str:
    if signature in RECURRING:
        return f"P{RECURRING.index(signature)}"
    return "oneoff"


def draw_novel(rng: random.Random, forbidden: set[Signature]) -> Signature:
    while True:
        signature = tuple(
            int(rng.random() < p_one)
            for p_one in PRIOR.bit_one_probability
        )
        if signature not in forbidden:
            return signature


def make_stream(seed: int, phase_length: int = PHASE_LENGTH) -> list[tuple[int, Signature, bool]]:
    rng = random.Random(seed)
    stream: list[tuple[int, Signature, bool]] = []
    used_oneoffs = set(RECURRING)

    for phase, probabilities in enumerate(PHASE_PROBABILITIES):
        cumulative: list[float] = []
        running = 0.0
        for probability in probabilities:
            running += probability
            cumulative.append(running)

        for _ in range(phase_length):
            draw = rng.random()
            signature: Signature | None = None
            for index, threshold in enumerate(cumulative):
                if draw < threshold:
                    signature = RECURRING[index]
                    break
            recurring = signature is not None
            if signature is None:
                signature = draw_novel(rng, used_oneoffs)
                used_oneoffs.add(signature)
            stream.append((phase, signature, recurring))

    return stream


class RecognitionTable:
    """Memoize the deterministic sensing instrument for fast gate sweeps."""

    def __init__(self, alpha: float | None = ALPHA):
        self.alpha = alpha
        self.recognizer = OpenWorldRecognizer(PRIOR, alpha=alpha)
        self._cache: dict[tuple[Signature, tuple[Signature, ...]], PrototypeRecognition] = {}

    @staticmethod
    def _key(prototypes: Iterable[Signature]) -> tuple[Signature, ...]:
        return tuple(sorted(set(prototypes)))

    def recognize(self, signature: Signature, prototypes: Iterable[Signature]) -> PrototypeRecognition:
        prototype_key = self._key(prototypes)
        key = (signature, prototype_key)
        if key not in self._cache:
            self._cache[key] = self.recognizer.recognize(signature, prototype_key)
        return self._cache[key]

    def cost(self, signature: Signature, prototypes: Iterable[Signature]) -> int:
        return self.recognize(signature, prototypes).probes


class Policy:
    name = "policy"

    def __init__(self, table: RecognitionTable, *, k: int = K, seed: int = 0):
        self.table = table
        self.k = k
        self.rng = random.Random(seed)
        self.cache: list[Signature] = []

    def observe(self, perceived_identity: Signature) -> None:
        raise NotImplementedError


class LRUPolicy(Policy):
    name = "lru"

    def observe(self, perceived_identity: Signature) -> None:
        if perceived_identity in self.cache:
            self.cache.remove(perceived_identity)
            self.cache.append(perceived_identity)
            return
        if len(self.cache) >= self.k:
            self.cache.pop(0)
        self.cache.append(perceived_identity)


class RandomReplacementPolicy(Policy):
    name = "random"

    def observe(self, perceived_identity: Signature) -> None:
        if perceived_identity in self.cache:
            return
        if len(self.cache) < self.k:
            self.cache.append(perceived_identity)
            return
        self.cache[self.rng.randrange(self.k)] = perceived_identity


class WindowPolicy(Policy):
    """Shared decaying temporary evidence for selective durable policies."""

    def __init__(self, table: RecognitionTable, *, k: int = K, seed: int = 0, window: int = WINDOW):
        super().__init__(table, k=k, seed=seed)
        self.window = window
        self.trace: deque[Signature] = deque()
        self.counts: Counter[Signature] = Counter()

    def update_trace(self, identity: Signature) -> None:
        self.trace.append(identity)
        self.counts[identity] += 1
        if len(self.trace) > self.window:
            old = self.trace.popleft()
            self.counts[old] -= 1
            if self.counts[old] <= 0:
                del self.counts[old]


class FrequencyPolicy(WindowPolicy):
    """Boring heavy-hitter attacker: recurrence count only, same K slots."""

    name = "frequency"

    def observe(self, perceived_identity: Signature) -> None:
        self.update_trace(perceived_identity)
        eligible = [
            (count, signature)
            for signature, count in self.counts.items()
            if count >= 2
        ]
        eligible.sort(reverse=True)
        self.cache = [signature for _, signature in eligible[: self.k]]


class ProbeValuePolicy(WindowPolicy):
    """Admit prototypes only when they reduce recent expected sensing cost.

    This is deliberately small enough to enumerate subsets of the few patterns
    that recur inside the temporary window.  An unstored identity is priced at
    the full 12-probe open-world scan; a stored identity earns only the scalar
    probes actually saved by the current prototype set.  No external label says
    which patterns are "real" or recurring.
    """

    name = "probe_value"

    def _objective(self, subset: tuple[Signature, ...]) -> float:
        total = max(1, sum(self.counts.values()))
        saved = 0.0
        for signature in subset:
            count = self.counts[signature]
            known_cost = self.table.cost(signature, subset)
            saved += count * (N_ACTIONS - known_cost)
        return N_ACTIONS - saved / total

    def observe(self, perceived_identity: Signature) -> None:
        self.update_trace(perceived_identity)
        candidates = [
            signature
            for signature, count in self.counts.items()
            if count >= 2
        ]
        # One-offs are unique in the assay, so this normally contains only the
        # recurring response patterns.  The cap prevents pathological subset
        # explosion if an attacker changes the stream generator later.
        candidates.sort(key=lambda s: (self.counts[s], s), reverse=True)
        candidates = candidates[:10]

        best_objective = float(N_ACTIONS)
        best_subset: tuple[Signature, ...] = ()
        for size in range(min(self.k, len(candidates)) + 1):
            for subset in itertools.combinations(candidates, size):
                objective = self._objective(subset)
                if (
                    objective < best_objective - 1e-12
                    or (
                        abs(objective - best_objective) <= 1e-12
                        and len(subset) < len(best_subset)
                    )
                ):
                    best_objective = objective
                    best_subset = subset
        self.cache = list(best_subset)


@dataclass
class Metrics:
    events: int = 0
    probes: int = 0
    errors: int = 0
    recurring_events: int = 0
    recurring_probes: int = 0
    oneoff_events: int = 0
    oneoff_probes: int = 0
    oneoff_false_accepts: int = 0
    false_consolidations: int = 0
    admissions: int = 0
    recurring_slot_sum: float = 0.0
    slot_precision_sum: float = 0.0
    phase_recurring_probes: list[list[int]] = field(default_factory=lambda: [[], []])

    def add(
        self,
        *,
        phase: int,
        recurring: bool,
        recognition: PrototypeRecognition,
        old_cache: set[Signature],
        new_cache: set[Signature],
    ) -> None:
        self.events += 1
        self.probes += recognition.probes
        self.errors += int(not recognition.correct)
        if recurring:
            self.recurring_events += 1
            self.recurring_probes += recognition.probes
            self.phase_recurring_probes[phase].append(recognition.probes)
        else:
            self.oneoff_events += 1
            self.oneoff_probes += recognition.probes
            self.oneoff_false_accepts += int(not recognition.correct)

        admitted = new_cache - old_cache
        self.admissions += len(admitted)
        self.false_consolidations += sum(signature not in RECURRING for signature in admitted)
        recurring_slots = sum(signature in RECURRING for signature in new_cache)
        self.recurring_slot_sum += recurring_slots / K
        if new_cache:
            self.slot_precision_sum += recurring_slots / len(new_cache)

    def receipt(self) -> dict:
        phase0 = self.phase_recurring_probes[0]
        phase1 = self.phase_recurring_probes[1]
        early = phase1[: min(80, len(phase1))]
        late = phase1[-min(80, len(phase1)) :] if phase1 else []
        return {
            "mean_probes": self.probes / self.events,
            "recurring_mean_probes": self.recurring_probes / self.recurring_events,
            "oneoff_mean_probes": self.oneoff_probes / self.oneoff_events,
            "error_rate": self.errors / self.events,
            "oneoff_false_accept_rate": self.oneoff_false_accepts / self.oneoff_events,
            "false_consolidations": self.false_consolidations,
            "admissions": self.admissions,
            "mean_recurring_slot_occupancy": self.recurring_slot_sum / self.events,
            "mean_cache_precision": self.slot_precision_sum / self.events,
            "phase0_recurring_mean_probes": sum(phase0) / len(phase0),
            "phase1_recurring_mean_probes": sum(phase1) / len(phase1),
            "phase1_early_recurring_mean_probes": sum(early) / len(early),
            "phase1_late_recurring_mean_probes": sum(late) / len(late),
        }


def oracle_cache(probabilities: tuple[float, ...], table: RecognitionTable) -> list[Signature]:
    """Future-aware static ceiling for one phase; it may leave slots unused."""
    total_recurring_probability = sum(probabilities)
    best_cost = float("inf")
    best: tuple[Signature, ...] = ()
    for size in range(K + 1):
        for subset in itertools.combinations(RECURRING, size):
            expected = 0.0
            for signature, probability in zip(RECURRING, probabilities):
                # Unstored signatures are open-world unknowns and must be fully scanned.
                cost = table.cost(signature, subset) if signature in subset else N_ACTIONS
                expected += probability * cost
            expected /= total_recurring_probability
            if expected < best_cost - 1e-12:
                best_cost = expected
                best = subset
    return list(best)


def run_seed(seed: int) -> tuple[dict[str, dict], dict]:
    table = RecognitionTable(ALPHA)
    stream = make_stream(seed)
    policies: list[Policy] = [
        LRUPolicy(table, seed=seed + 10),
        RandomReplacementPolicy(table, seed=seed + 20),
        FrequencyPolicy(table, seed=seed + 30),
        ProbeValuePolicy(table, seed=seed + 40),
    ]
    metrics = {policy.name: Metrics() for policy in policies}

    phase_oracles = [
        oracle_cache(probabilities, table)
        for probabilities in PHASE_PROBABILITIES
    ]
    oracle_metrics = Metrics()

    for phase, signature, recurring in stream:
        for policy in policies:
            old_cache = set(policy.cache)
            recognition = table.recognize(signature, policy.cache)
            policy.observe(recognition.identity)
            new_cache = set(policy.cache)
            metrics[policy.name].add(
                phase=phase,
                recurring=recurring,
                recognition=recognition,
                old_cache=old_cache,
                new_cache=new_cache,
            )

        oracle = phase_oracles[phase]
        oracle_recognition = table.recognize(signature, oracle)
        oracle_metrics.add(
            phase=phase,
            recurring=recurring,
            recognition=oracle_recognition,
            old_cache=set(oracle),
            new_cache=set(oracle),
        )

    result = {name: value.receipt() for name, value in metrics.items()}
    result["oracle"] = oracle_metrics.receipt()
    representative = {
        "final_caches": {
            policy.name: [signature_name(signature) for signature in policy.cache]
            for policy in policies
        },
        "oracle_phase_caches": [
            [signature_name(signature) for signature in cache]
            for cache in phase_oracles
        ],
    }
    return result, representative


def mean_receipts(receipts: list[dict[str, dict]]) -> dict[str, dict]:
    names = receipts[0].keys()
    result: dict[str, dict] = {}
    for name in names:
        keys = receipts[0][name].keys()
        result[name] = {
            key: sum(receipt[name][key] for receipt in receipts) / len(receipts)
            for key in keys
        }
    return result


def exact_novelty_tradeoff(cache: list[Signature]) -> dict[str, dict]:
    """Enumerate all 2^12 signatures under the declared novelty distribution."""
    alphas: tuple[float | None, ...] = (None, 0.10, 0.03, 0.01, 0.003, 0.001)
    result: dict[str, dict] = {}
    all_probability = 0.0
    weighted: dict[str, list[float]] = {}
    for alpha in alphas:
        label = "closed_world" if alpha is None else f"alpha_{alpha:g}"
        weighted[label] = [0.0, 0.0]

    for integer in range(1 << N_ACTIONS):
        signature = tuple((integer >> action) & 1 for action in range(N_ACTIONS))
        if signature in cache:
            continue
        probability = 1.0
        for action, response in enumerate(signature):
            probability *= PRIOR.probability(action, response)
        all_probability += probability

        for alpha in alphas:
            label = "closed_world" if alpha is None else f"alpha_{alpha:g}"
            recognition = OpenWorldRecognizer(PRIOR, alpha=alpha).recognize(signature, cache)
            weighted[label][0] += probability * recognition.probes
            weighted[label][1] += probability * int(not recognition.correct)

    for alpha in alphas:
        label = "closed_world" if alpha is None else f"alpha_{alpha:g}"
        recognizer = OpenWorldRecognizer(PRIOR, alpha=alpha)
        known_mean = sum(recognizer.probe_cost(signature, cache) for signature in cache) / len(cache)
        result[label] = {
            "novel_expected_probes": weighted[label][0] / all_probability,
            "novel_false_accept_probability": weighted[label][1] / all_probability,
            "known_mean_probes": known_mean,
        }
    return result


def run_all() -> dict:
    seed_receipts: list[dict[str, dict]] = []
    representative: dict = {}
    for seed in SEEDS:
        receipt, rep = run_seed(seed)
        seed_receipts.append(receipt)
        if seed == 0:
            representative = rep

    policies = mean_receipts(seed_receipts)
    table = RecognitionTable(ALPHA)
    oracle_a = oracle_cache(PHASE_PROBABILITIES[0], table)
    novelty = exact_novelty_tradeoff(oracle_a)

    value = policies["probe_value"]
    frequency = policies["frequency"]
    lru = policies["lru"]
    oracle = policies["oracle"]
    open_safe = novelty["alpha_0.01"]
    closed = novelty["closed_world"]

    passed = (
        value["recurring_mean_probes"] <= 0.97 * frequency["recurring_mean_probes"]
        and value["recurring_mean_probes"] <= 0.95 * lru["recurring_mean_probes"]
        and value["recurring_mean_probes"] <= 1.15 * oracle["recurring_mean_probes"]
        and value["error_rate"] <= 0.02
        and value["false_consolidations"] <= 1.0
        and open_safe["novel_false_accept_probability"] <= 0.011
        and closed["known_mean_probes"] < open_safe["known_mean_probes"]
        and closed["novel_false_accept_probability"] > open_safe["novel_false_accept_probability"]
    )

    return {
        "schema": "alternative-neuron-gate5-v1",
        "gate": "G5_SELECTIVE_INTERNAL_OBJECTS",
        "pass": passed,
        "classification": (
            "PROBE_VALUE_SELECTIVE_OBJECTS_BEAT_RECENCY_RANDOM_AND_FREQUENCY_CACHE_UNDER_DECLARED_NOVELTY_PRIOR"
            if passed
            else "GATE5_FAILED"
        ),
        "setup": {
            "actions": N_ACTIONS,
            "durable_slots_K": K,
            "temporary_trace_window": WINDOW,
            "phase_length": PHASE_LENGTH,
            "seeds": list(SEEDS),
            "oneoff_probability": 0.15,
            "alpha": ALPHA,
            "recurring_signatures": ["".join(map(str, signature)) for signature in RECURRING],
            "phase_probabilities": PHASE_PROBABILITIES,
        },
        "policies": policies,
        "representative_seed0": representative,
        "open_world_novelty_tradeoff": novelty,
        "claim_boundary": (
            "Synthetic deterministic 12-bit action-response family under an explicit independent-bit novelty prior. "
            "The probe-value admission rule is hand designed and optimizes recent scalar sensing cost; it is not a "
            "claim of general concept formation, biological equivalence, consciousness, or a new caching theorem."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/GATE5_SELECTIVE_OBJECTS.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = run_all()
    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")
    return 1 if args.check and not result["pass"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
