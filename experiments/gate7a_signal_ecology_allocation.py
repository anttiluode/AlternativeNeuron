#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
from collections import deque
from pathlib import Path


SOURCES = ("self", "partner", "fly", "context", "alarm")
SELF, PARTNER, FLY, CONTEXT, ALARM = range(len(SOURCES))

# Independent event rates per timestep. Several sources may occur together.
PHASE_RATES = (
    (0.25, 0.15, 0.58, 0.03, 0.02),
    (0.15, 0.35, 0.45, 0.025, 0.05),
)

# Observation amplitude is deliberately decoupled from consequence. The fly is
# loud and frequent; context is quiet. This makes raw variance a serious but
# wrong allocation heuristic.
AMPLITUDE = (1.0, 1.5, 5.0, 0.3, 2.0)

# Cost of simply ignoring one event. Partner/alarm interpretation depends on a
# slow context read; that makes source values complementary rather than additive.
IGNORE_LOSS = (1.5, 2.0, 0.08, 0.10, 4.0)
CONTEXT_READ_WEIGHT = 0.70

BACKGROUND_G = 0.20
TOTAL_G = 5.0
BOOST_QUANTUM = 0.25
BOOST_QUANTA = int(round((TOTAL_G - BACKGROUND_G * len(SOURCES)) / BOOST_QUANTUM))
MAX_BOOSTED_SOURCES = 3

PHASE_LENGTH = 3000
WINDOW = 256
REOPT_INTERVAL = 64
SEEDS = tuple(range(8))


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def expected_cost(rates: tuple[float, ...] | list[float], conductance: list[float]) -> float:
    """Expected per-step handling loss under one fixed conductance allocation."""

    g_context = conductance[CONTEXT]
    total = 0.0
    total += rates[SELF] * min(IGNORE_LOSS[SELF], 1.0 / conductance[SELF])
    total += rates[FLY] * min(IGNORE_LOSS[FLY], 1.0 / conductance[FLY])
    total += rates[CONTEXT] * min(IGNORE_LOSS[CONTEXT], 1.0 / conductance[CONTEXT])
    total += rates[PARTNER] * min(
        IGNORE_LOSS[PARTNER],
        1.0 / conductance[PARTNER] + CONTEXT_READ_WEIGHT / g_context,
    )
    total += rates[ALARM] * min(
        IGNORE_LOSS[ALARM],
        1.0 / conductance[ALARM] + CONTEXT_READ_WEIGHT / g_context,
    )
    return total


def event_cost(events: tuple[bool, ...], conductance: list[float]) -> float:
    g_context = conductance[CONTEXT]
    total = 0.0
    for source, active in enumerate(events):
        if not active:
            continue
        if source in (PARTNER, ALARM):
            total += min(
                IGNORE_LOSS[source],
                1.0 / conductance[source] + CONTEXT_READ_WEIGHT / g_context,
            )
        else:
            total += min(IGNORE_LOSS[source], 1.0 / conductance[source])
    return total


def optimize_within_subset(
    rates: tuple[float, ...] | list[float], subset: tuple[int, ...]
) -> tuple[float, list[float]]:
    """Give a chosen source subset the best discrete split of the same budget."""

    if not subset:
        conductance = [BACKGROUND_G] * len(SOURCES)
        return expected_cost(rates, conductance), conductance

    best_cost = float("inf")
    best_g: list[float] = []

    def recurse(remaining: int, position: int, assignment: list[int]) -> None:
        nonlocal best_cost, best_g
        if position == len(subset) - 1:
            quanta = assignment + [remaining]
            conductance = [BACKGROUND_G] * len(SOURCES)
            for source, amount in zip(subset, quanta):
                conductance[source] += amount * BOOST_QUANTUM
            cost = expected_cost(rates, conductance)
            if cost < best_cost - 1e-12:
                best_cost = cost
                best_g = conductance
            return
        for amount in range(remaining + 1):
            recurse(remaining - amount, position + 1, assignment + [amount])

    recurse(BOOST_QUANTA, 0, [])
    return best_cost, best_g


def optimize_joint(
    rates: tuple[float, ...] | list[float]
) -> tuple[float, tuple[int, ...], list[float]]:
    best_cost = float("inf")
    best_subset: tuple[int, ...] = ()
    best_g: list[float] = []
    for size in range(1, MAX_BOOSTED_SOURCES + 1):
        for subset in itertools.combinations(range(len(SOURCES)), size):
            cost, conductance = optimize_within_subset(rates, subset)
            if cost < best_cost - 1e-12:
                best_cost = cost
                best_subset = subset
                best_g = conductance
    return best_cost, best_subset, best_g


def independent_value_subset(
    rates: tuple[float, ...] | list[float]
) -> tuple[float, tuple[int, ...], list[float]]:
    """Strong attacker: rank each source by its value when boosted alone.

    It gets the same consequence model as the joint optimizer. Its only missing
    capability is evaluating complementary source sets before choosing slots.
    After it chooses the top K independently, it is even allowed to optimize the
    conductance split jointly inside that selected set.
    """

    baseline = [BACKGROUND_G] * len(SOURCES)
    baseline_cost = expected_cost(rates, baseline)
    total_boost = TOTAL_G - BACKGROUND_G * len(SOURCES)
    scores: list[tuple[float, int]] = []
    for source in range(len(SOURCES)):
        conductance = baseline.copy()
        conductance[source] += total_boost
        saving = baseline_cost - expected_cost(rates, conductance)
        scores.append((saving, source))
    scores.sort(reverse=True)
    subset = tuple(source for _, source in scores[:MAX_BOOSTED_SOURCES])
    cost, conductance = optimize_within_subset(rates, subset)
    return cost, subset, conductance


class Policy:
    def __init__(self, name: str, seed: int):
        self.name = name
        self.rng = random.Random(seed)
        self.history: deque[tuple[bool, ...]] = deque(maxlen=WINDOW)
        self.last_seen: list[int] = []
        self.subset: tuple[int, ...] = ()
        self.conductance = [BACKGROUND_G] * len(SOURCES)
        self.first_phase1_oracle_match: int | None = None

    def empirical_rates(self) -> list[float]:
        if not self.history:
            return [0.10] * len(SOURCES)
        count = len(self.history)
        return [
            sum(int(events[source]) for events in self.history) / count
            for source in range(len(SOURCES))
        ]

    def choose(self, timestep: int, phase: int) -> None:
        rates = self.empirical_rates()

        if self.name == "joint_consequence":
            _, subset, conductance = optimize_joint(rates)
        elif self.name == "independent_value":
            _, subset, conductance = independent_value_subset(rates)
        elif self.name == "frequency":
            subset = tuple(
                sorted(range(len(SOURCES)), key=lambda source: rates[source], reverse=True)[
                    :MAX_BOOSTED_SOURCES
                ]
            )
            _, conductance = optimize_within_subset(rates, subset)
        elif self.name == "variance":
            subset = tuple(
                sorted(
                    range(len(SOURCES)),
                    key=lambda source: rates[source] * AMPLITUDE[source] ** 2,
                    reverse=True,
                )[:MAX_BOOSTED_SOURCES]
            )
            _, conductance = optimize_within_subset(rates, subset)
        elif self.name == "lru":
            subset = tuple(self.last_seen[-MAX_BOOSTED_SOURCES:]) or (SELF,)
            _, conductance = optimize_within_subset(rates, subset)
        elif self.name == "random":
            subset = tuple(sorted(self.rng.sample(range(len(SOURCES)), MAX_BOOSTED_SOURCES)))
            _, conductance = optimize_within_subset(rates, subset)
        elif self.name == "oracle":
            _, subset, conductance = optimize_joint(PHASE_RATES[phase])
        else:
            raise ValueError(self.name)

        self.subset = subset
        self.conductance = conductance

        if phase == 1 and self.first_phase1_oracle_match is None:
            oracle_subset = optimize_joint(PHASE_RATES[1])[1]
            if set(subset) == set(oracle_subset):
                self.first_phase1_oracle_match = timestep - PHASE_LENGTH

    def observe(self, events: tuple[bool, ...]) -> None:
        self.history.append(events)
        for source, active in enumerate(events):
            if not active:
                continue
            if source in self.last_seen:
                self.last_seen.remove(source)
            self.last_seen.append(source)


def run_seed(seed: int) -> tuple[dict[str, dict], dict]:
    names = (
        "joint_consequence",
        "independent_value",
        "frequency",
        "variance",
        "lru",
        "random",
        "oracle",
    )
    policies = {
        name: Policy(name, seed=710000 + seed * 31 + index)
        for index, name in enumerate(names)
    }
    traces = {name: [] for name in names}
    rng = random.Random(700000 + seed)

    for timestep in range(PHASE_LENGTH * 2):
        phase = 0 if timestep < PHASE_LENGTH else 1
        if timestep % REOPT_INTERVAL == 0:
            for policy in policies.values():
                policy.choose(timestep, phase)

        events = tuple(rng.random() < rate for rate in PHASE_RATES[phase])
        for name, policy in policies.items():
            traces[name].append(event_cost(events, policy.conductance))
            policy.observe(events)

    receipt: dict[str, dict] = {}
    for name, trace in traces.items():
        usable = trace[WINDOW:]
        receipt[name] = {
            "mean_cost": mean(usable),
            "phase0_late_cost": mean(trace[1000:PHASE_LENGTH]),
            "phase1_early_cost": mean(trace[PHASE_LENGTH : PHASE_LENGTH + 500]),
            "phase1_late_cost": mean(trace[PHASE_LENGTH + 1500 :]),
            "phase1_oracle_subset_match_delay": policies[name].first_phase1_oracle_match,
            "final_subset": [SOURCES[source] for source in policies[name].subset],
            "final_conductance": {
                SOURCES[source]: policies[name].conductance[source]
                for source in range(len(SOURCES))
            },
        }

    representative = {
        "phase0_oracle_subset": [SOURCES[source] for source in optimize_joint(PHASE_RATES[0])[1]],
        "phase1_oracle_subset": [SOURCES[source] for source in optimize_joint(PHASE_RATES[1])[1]],
    }
    return receipt, representative


def average_receipts(receipts: list[dict[str, dict]]) -> dict[str, dict]:
    names = receipts[0].keys()
    result: dict[str, dict] = {}
    numeric_keys = ("mean_cost", "phase0_late_cost", "phase1_early_cost", "phase1_late_cost")
    for name in names:
        result[name] = {
            key: mean([receipt[name][key] for receipt in receipts])
            for key in numeric_keys
        }
        delays = [
            receipt[name]["phase1_oracle_subset_match_delay"]
            for receipt in receipts
            if receipt[name]["phase1_oracle_subset_match_delay"] is not None
        ]
        result[name]["mean_phase1_oracle_subset_match_delay"] = mean(delays) if delays else None
        result[name]["oracle_subset_match_fraction"] = len(delays) / len(receipts)
    return result


def run_all() -> dict:
    seed_receipts: list[dict[str, dict]] = []
    representative: dict = {}
    for seed in SEEDS:
        receipt, rep = run_seed(seed)
        seed_receipts.append(receipt)
        if seed == 0:
            representative = rep

    policies = average_receipts(seed_receipts)
    joint = policies["joint_consequence"]
    independent = policies["independent_value"]
    variance = policies["variance"]
    oracle = policies["oracle"]

    passed = (
        joint["mean_cost"] < independent["mean_cost"] * 0.90
        and joint["mean_cost"] < variance["mean_cost"] * 0.80
        and joint["mean_cost"] < oracle["mean_cost"] * 1.03
        and joint["phase1_late_cost"] < independent["phase1_late_cost"] * 0.85
        and joint["oracle_subset_match_fraction"] == 1.0
        and joint["mean_phase1_oracle_subset_match_delay"] is not None
        and joint["mean_phase1_oracle_subset_match_delay"] <= WINDOW + REOPT_INTERVAL
    )

    return {
        "schema": "alternative-neuron-gate7a-v1",
        "gate": "G7A_SIGNAL_ECOLOGY_ALLOCATION",
        "pass": passed,
        "classification": (
            "JOINT_CONSEQUENCE_ALLOCATION_IGNORES_LOUD_DISTRACTOR_AND_REALLOCATES_FIXED_ROUTING_BUDGET_TO_COMPLEMENTARY_SOURCES"
            if passed
            else "GATE7A_FAILED"
        ),
        "setup": {
            "sources": list(SOURCES),
            "phase_rates": [list(rates) for rates in PHASE_RATES],
            "amplitudes": list(AMPLITUDE),
            "ignore_losses": list(IGNORE_LOSS),
            "context_read_weight": CONTEXT_READ_WEIGHT,
            "background_conductance": BACKGROUND_G,
            "total_conductance": TOTAL_G,
            "max_boosted_sources": MAX_BOOSTED_SOURCES,
            "window": WINDOW,
            "reopt_interval": REOPT_INTERVAL,
            "phase_length": PHASE_LENGTH,
            "seeds": list(SEEDS),
            "fairness_boundary": (
                "All policies receive the same already-separated source identities in Gate 7A. "
                "This isolates allocation only; blind source separation and delayed coupling are deferred to Gate 7B."
            ),
        },
        "policies": policies,
        "representative": representative,
        "interaction": {
            "partner_and_alarm_require_context_read": True,
            "reason": (
                "At background conductance, boosting partner or context alone can be nearly worthless because interpretation cost saturates at ignore loss. "
                "Boosting them together crosses that threshold, so resource value is non-additive."
            ),
        },
        "meaning": (
            "The loud frequent fly is a deliberate variance/frequency trap: its ignore loss is tiny, so consequence-aware allocation should not spend scarce routing budget on it. "
            "The slow quiet context is individually weak but becomes useful jointly with partner/alarm channels because it reduces their interpretation cost. "
            "After the phase shift, the optimal three-source boosted set changes from self+partner+context to partner+context+alarm; the rolling joint policy must release self and reallocate toward the now more frequent alarm."
        ),
        "claim_boundary": (
            "This is an allocation assay after source separation, not a full solution to mixed-signal ecology and not a biological cortical-area model. "
            "The source interaction law and ignore losses are hand designed. Gate 7B must remove the clean source-ID assumption and test delayed coupled mixtures against PCA/ICA and shuffled-lag attackers."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/GATE7A_SIGNAL_ECOLOGY_ALLOCATION.json")
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
