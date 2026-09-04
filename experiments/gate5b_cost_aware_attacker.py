#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path

from alternative_neuron.prototypes import PrototypeRecognition, Signature
from experiments.gate5_selective_objects import (
    ALPHA,
    K,
    N_ACTIONS,
    PHASE_PROBABILITIES,
    RECURRING,
    SEEDS,
    WINDOW,
    ProbeValuePolicy,
    RecognitionTable,
    WindowPolicy,
    make_stream,
    oracle_cache,
    signature_name,
)


class FrequencyTimesSoloSavingPolicy(WindowPolicy):
    """Stronger boring attacker: frequency times independent sensing benefit.

    Unlike the plain heavy-hitter, this attacker already knows that a prototype
    which saves zero scalar probes is pointless to cache.  It still scores each
    object independently and therefore ignores that stored prototypes change
    one another's disambiguation and open-world evidence burden.
    """

    name = "frequency_x_solo_saving"

    def observe(self, perceived_identity: Signature) -> None:
        self.update_trace(perceived_identity)
        scored: list[tuple[float, int, Signature]] = []
        for signature, count in self.counts.items():
            if count < 2:
                continue
            solo_cost = self.table.cost(signature, [signature])
            saving = N_ACTIONS - solo_cost
            if saving <= 0:
                continue
            scored.append((count * saving, count, signature))
        scored.sort(reverse=True)
        self.cache = [signature for _, _, signature in scored[: self.k]]


@dataclass
class SafeMetrics:
    events: int = 0
    errors: int = 0
    conservative_probes: int = 0
    recurring_events: int = 0
    recurring_conservative_probes: int = 0
    recurring_slot_sum: float = 0.0
    phase_recurring_safe: list[list[int]] = field(default_factory=lambda: [[], []])

    def add(
        self,
        *,
        phase: int,
        recurring: bool,
        recognition: PrototypeRecognition,
        cache: list[Signature],
    ) -> None:
        # Never reward a false accept for stopping early.  An error is charged
        # as if the machine had paid for the full 12-action signature.
        safe = recognition.probes if recognition.correct else N_ACTIONS
        self.events += 1
        self.errors += int(not recognition.correct)
        self.conservative_probes += safe
        self.recurring_slot_sum += sum(signature in RECURRING for signature in cache) / K
        if recurring:
            self.recurring_events += 1
            self.recurring_conservative_probes += safe
            self.phase_recurring_safe[phase].append(safe)

    def receipt(self) -> dict:
        phase0, phase1 = self.phase_recurring_safe
        return {
            "error_rate": self.errors / self.events,
            "conservative_mean_probes": self.conservative_probes / self.events,
            "conservative_recurring_mean_probes": (
                self.recurring_conservative_probes / self.recurring_events
            ),
            "phase0_conservative_recurring_mean_probes": sum(phase0) / len(phase0),
            "phase1_conservative_recurring_mean_probes": sum(phase1) / len(phase1),
            "mean_recurring_slot_occupancy": self.recurring_slot_sum / self.events,
        }


def run_seed(seed: int) -> tuple[dict[str, dict], dict]:
    table = RecognitionTable(ALPHA)
    value = ProbeValuePolicy(table, seed=seed + 100, window=WINDOW)
    independent = FrequencyTimesSoloSavingPolicy(table, seed=seed + 200, window=WINDOW)
    policies = [value, independent]
    metrics = {policy.name: SafeMetrics() for policy in policies}

    phase_oracles = [oracle_cache(probabilities, table) for probabilities in PHASE_PROBABILITIES]
    oracle_metrics = SafeMetrics()

    for phase, signature, recurring in make_stream(seed):
        for policy in policies:
            recognition = table.recognize(signature, policy.cache)
            policy.observe(recognition.identity)
            metrics[policy.name].add(
                phase=phase,
                recurring=recurring,
                recognition=recognition,
                cache=policy.cache,
            )

        oracle = phase_oracles[phase]
        recognition = table.recognize(signature, oracle)
        oracle_metrics.add(
            phase=phase,
            recurring=recurring,
            recognition=recognition,
            cache=oracle,
        )

    result = {name: metric.receipt() for name, metric in metrics.items()}
    result["oracle"] = oracle_metrics.receipt()
    representative = {
        policy.name: [signature_name(signature) for signature in policy.cache]
        for policy in policies
    }
    return result, representative


def mean_receipts(receipts: list[dict[str, dict]]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for name in receipts[0]:
        result[name] = {
            key: sum(receipt[name][key] for receipt in receipts) / len(receipts)
            for key in receipts[0][name]
        }
    return result


def interaction_audit() -> dict:
    table = RecognitionTable(ALPHA)
    oracle = oracle_cache(PHASE_PROBABILITIES[0], table)
    return {
        "oracle_cache": [signature_name(signature) for signature in oracle],
        "prototype_costs": {
            signature_name(signature): {
                "solo": table.cost(signature, [signature]),
                "inside_oracle_set": (
                    table.cost(signature, oracle) if signature in oracle else N_ACTIONS
                ),
            }
            for signature in RECURRING
        },
        "point": (
            "Prototype values are not additive: adding stored hypotheses can change the "
            "questions and evidence threshold needed to certify the other stored objects."
        ),
    }


def run_all() -> dict:
    receipts: list[dict[str, dict]] = []
    representative: dict = {}
    for seed in SEEDS:
        result, final_cache = run_seed(seed)
        receipts.append(result)
        if seed == 0:
            representative = final_cache

    policies = mean_receipts(receipts)
    value = policies["probe_value"]
    independent = policies["frequency_x_solo_saving"]
    oracle = policies["oracle"]

    passed = (
        value["conservative_recurring_mean_probes"]
        <= 0.98 * independent["conservative_recurring_mean_probes"]
        and value["conservative_recurring_mean_probes"]
        <= 1.03 * oracle["conservative_recurring_mean_probes"]
        and value["error_rate"] <= 0.02
        and value["mean_recurring_slot_occupancy"] < 0.90
    )

    return {
        "schema": "alternative-neuron-gate5b-v1",
        "gate": "G5B_COST_AWARE_ATTACKER",
        "pass": passed,
        "classification": (
            "JOINT_PROBE_VALUE_SELECTION_BEATS_FREQUENCY_TIMES_SOLO_SAVING_WITH_ERRORS_CHARGED_AS_FULL_SCANS"
            if passed
            else "GATE5B_FAILED"
        ),
        "policies": policies,
        "representative_seed0_final_cache": representative,
        "interaction_audit": interaction_audit(),
        "claim_boundary": (
            "Post-result attacker audit. The baseline is already frequency times independent probe saving; "
            "the remaining advantage comes from jointly evaluating prototype sets in this synthetic open-world "
            "recognition problem. This is a caching/active-sensing mechanism result, not a claim of a new theorem "
            "or general unsupervised concept formation."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/GATE5B_COST_AWARE_ATTACKER.json")
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
