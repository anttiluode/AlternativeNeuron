#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


N_WORLD = 8
N_SELF = 4
N_ACTIONS = 12
TRIALS_PER_CAUSE = 128
SEEDS = tuple(range(8))
CAUSES = ("neither", "world", "self", "both")

Signature = tuple[int, ...]
Pair = tuple[int, int]


def xor_signature(a: Signature, b: Signature) -> Signature:
    return tuple(x ^ y for x, y in zip(a, b))


def entropy(probabilities: Iterable[float]) -> float:
    return -sum(p * math.log2(p) for p in probabilities if p > 0.0)


def make_component_codes(seed: int) -> tuple[tuple[Signature, ...], tuple[Signature, ...]]:
    """Generate a reproducible XOR-compositional response world.

    Every joint world/self state must have a unique 12-bit intervention
    signature.  Self state 0 is the zero operator so the star calibration has a
    convenient gauge.
    """

    rng = random.Random(9000 + seed)
    for _ in range(10000):
        world = tuple(
            tuple(rng.randrange(2) for _ in range(N_ACTIONS))
            for _ in range(N_WORLD)
        )
        self_codes = [tuple(0 for _ in range(N_ACTIONS))]
        self_codes.extend(
            tuple(rng.randrange(2) for _ in range(N_ACTIONS))
            for _ in range(N_SELF - 1)
        )
        self_tuple = tuple(self_codes)
        joint = {
            xor_signature(world[x], self_tuple[t])
            for x in range(N_WORLD)
            for t in range(N_SELF)
        }
        if len(joint) != N_WORLD * N_SELF:
            continue
        # Avoid degenerate channels that never vary across the joint family.
        if all(
            len({xor_signature(world[x], self_tuple[t])[a]
                 for x in range(N_WORLD) for t in range(N_SELF)}) == 2
            for a in range(N_ACTIONS)
        ):
            return world, self_tuple
    raise RuntimeError("could not generate a nondegenerate component codebook")


@dataclass(frozen=True)
class CompositionalWorld:
    world_codes: tuple[Signature, ...]
    self_codes: tuple[Signature, ...]

    @classmethod
    def generate(cls, seed: int) -> "CompositionalWorld":
        world, self_codes = make_component_codes(seed)
        return cls(world, self_codes)

    def signature(self, pair: Pair) -> Signature:
        x, theta = pair
        return xor_signature(self.world_codes[x], self.self_codes[theta])

    def poke(self, pair: Pair, action: int) -> int:
        return self.signature(pair)[action]


@dataclass(frozen=True)
class StarCalibration:
    world_templates: tuple[Signature, ...]
    self_deltas: tuple[Signature, ...]
    scalar_pokes: int

    @property
    def stored_bits(self) -> int:
        # self delta 0 is the all-zero gauge and need not be stored.
        return (N_WORLD + N_SELF - 1) * N_ACTIONS

    def predict(self, pair: Pair) -> Signature:
        x, theta = pair
        return xor_signature(self.world_templates[x], self.self_deltas[theta])


def calibrate_factorized(world: CompositionalWorld) -> StarCalibration:
    # Controlled star calibration: all external states at theta=0, then all
    # self states at x=0.  The test never supplies a change-cause label.
    world_templates = tuple(world.signature((x, 0)) for x in range(N_WORLD))
    base = world_templates[0]
    self_deltas = [tuple(0 for _ in range(N_ACTIONS))]
    for theta in range(1, N_SELF):
        observed = world.signature((0, theta))
        self_deltas.append(xor_signature(observed, base))
    return StarCalibration(
        world_templates=world_templates,
        self_deltas=tuple(self_deltas),
        scalar_pokes=(N_WORLD + N_SELF - 1) * N_ACTIONS,
    )


def cause_of(previous: Pair, current: Pair) -> str:
    world_changed = previous[0] != current[0]
    self_changed = previous[1] != current[1]
    if world_changed and self_changed:
        return "both"
    if world_changed:
        return "world"
    if self_changed:
        return "self"
    return "neither"


def transition_candidates(previous: Pair) -> list[Pair]:
    return [(x, theta) for x in range(N_WORLD) for theta in range(N_SELF)]


def equal_cause_weights(previous: Pair, candidates: Sequence[Pair]) -> dict[Pair, float]:
    grouped = {cause: [] for cause in CAUSES}
    for pair in candidates:
        grouped[cause_of(previous, pair)].append(pair)
    weights: dict[Pair, float] = {}
    for cause in CAUSES:
        group = grouped[cause]
        for pair in group:
            weights[pair] = 1.0 / (len(CAUSES) * len(group))
    return weights


def normalize_weights(candidates: Sequence[Pair], weights: dict[Pair, float]) -> dict[Pair, float]:
    total = sum(weights[pair] for pair in candidates)
    return {pair: weights[pair] / total for pair in candidates}


def cause_entropy(previous: Pair, candidates: Sequence[Pair], weights: dict[Pair, float]) -> float:
    mass = {cause: 0.0 for cause in CAUSES}
    normalized = normalize_weights(candidates, weights)
    for pair in candidates:
        mass[cause_of(previous, pair)] += normalized[pair]
    return entropy(mass.values())


def response_entropy(
    candidates: Sequence[Pair],
    weights: dict[Pair, float],
    action: int,
    predict,
) -> float:
    normalized = normalize_weights(candidates, weights)
    p1 = sum(normalized[pair] for pair in candidates if predict(pair)[action] == 1)
    return entropy((p1, 1.0 - p1))


def cause_information_gain(
    previous: Pair,
    candidates: Sequence[Pair],
    weights: dict[Pair, float],
    action: int,
    predict,
) -> float:
    before = cause_entropy(previous, candidates, weights)
    normalized = normalize_weights(candidates, weights)
    after = 0.0
    for response in (0, 1):
        subset = [pair for pair in candidates if predict(pair)[action] == response]
        probability = sum(normalized[pair] for pair in subset)
        if subset and probability > 0.0:
            after += probability * cause_entropy(previous, subset, normalized)
    return before - after


@dataclass(frozen=True)
class TrialResult:
    pair_correct: bool
    cause_correct: bool
    probes_to_pair: int
    probes_to_cause: int


def identify_factorized(
    world: CompositionalWorld,
    calibration: StarCalibration,
    previous: Pair,
    target: Pair,
    *,
    random_actions: bool = False,
    rng: random.Random | None = None,
) -> TrialResult:
    candidates = transition_candidates(previous)
    prior_weights = equal_cause_weights(previous, candidates)
    used: set[int] = set()
    cause_probe: int | None = None
    rng = rng or random.Random(0)

    while len(candidates) > 1 and len(used) < N_ACTIONS:
        remaining = [action for action in range(N_ACTIONS) if action not in used]
        if random_actions:
            action = rng.choice(remaining)
        else:
            causes_left = {cause_of(previous, pair) for pair in candidates}
            if len(causes_left) > 1:
                scored = [
                    (
                        cause_information_gain(
                            previous, candidates, prior_weights, action, calibration.predict
                        ),
                        response_entropy(candidates, prior_weights, action, calibration.predict),
                        -action,
                    )
                    for action in remaining
                ]
            else:
                scored = [
                    (
                        response_entropy(candidates, prior_weights, action, calibration.predict),
                        0.0,
                        -action,
                    )
                    for action in remaining
                ]
            best = max(scored)
            action = -best[2]

        used.add(action)
        observed = world.poke(target, action)
        candidates = [
            pair for pair in candidates
            if calibration.predict(pair)[action] == observed
        ]
        if not candidates:
            break
        if cause_probe is None:
            causes_left = {cause_of(previous, pair) for pair in candidates}
            if len(causes_left) == 1:
                cause_probe = len(used)

    predicted = candidates[0] if len(candidates) == 1 else None
    if cause_probe is None:
        cause_probe = len(used)
    predicted_cause = cause_of(previous, predicted) if predicted is not None else "unknown"
    return TrialResult(
        pair_correct=(predicted == target),
        cause_correct=(predicted_cause == cause_of(previous, target)),
        probes_to_pair=len(used),
        probes_to_cause=cause_probe,
    )


@dataclass(frozen=True)
class MonolithicResult:
    predicted_pair: Pair | None
    probes: int
    correct: bool
    cause_correct: bool


def star_pairs() -> list[Pair]:
    return [(x, 0) for x in range(N_WORLD)] + [(0, theta) for theta in range(1, N_SELF)]


def choose_split_action(signatures: Sequence[Signature], used: set[int]) -> int | None:
    best: tuple[float, int] | None = None
    for action in range(N_ACTIONS):
        if action in used:
            continue
        ones = sum(signature[action] for signature in signatures)
        p1 = ones / len(signatures)
        score = entropy((p1, 1.0 - p1))
        candidate = (score, -action)
        if best is None or candidate > best:
            best = candidate
    return None if best is None else -best[1]


def monolithic_closed_world(
    world: CompositionalWorld,
    previous: Pair,
    target: Pair,
) -> MonolithicResult:
    # Equal storage budget to the factorized star model: eleven complete joint
    # signatures.  The attacker makes the optimistic/unsafe assumption that one
    # of those cached joint states must be the answer.
    candidates = star_pairs()
    used: set[int] = set()
    while len(candidates) > 1 and len(used) < N_ACTIONS:
        signatures = [world.signature(pair) for pair in candidates]
        action = choose_split_action(signatures, used)
        if action is None:
            break
        used.add(action)
        observed = world.poke(target, action)
        matching = [pair for pair in candidates if world.poke(pair, action) == observed]
        if matching:
            candidates = matching
        else:
            # Closed-world error: contradictory evidence is ignored rather than
            # creating a novel joint object.
            pass
    predicted = candidates[0] if len(candidates) == 1 else None
    return MonolithicResult(
        predicted_pair=predicted,
        probes=len(used),
        correct=(predicted == target),
        cause_correct=(
            predicted is not None
            and cause_of(previous, predicted) == cause_of(previous, target)
        ),
    )


def monolithic_exact_open_world(world: CompositionalWorld, target: Pair) -> int:
    # Without a compositional response family or a declared novelty prior, an
    # arbitrary unseen 12-bit joint signature requires all 12 scalar responses
    # for exact reconstruction.  This is the boring safe attacker.
    _ = world.signature(target)
    return N_ACTIONS


def target_for_cause(rng: random.Random, cause: str, previous: Pair = (0, 0)) -> Pair:
    if cause == "neither":
        return previous
    if cause == "world":
        return (rng.randrange(1, N_WORLD), previous[1])
    if cause == "self":
        return (previous[0], rng.randrange(1, N_SELF))
    if cause == "both":
        return (rng.randrange(1, N_WORLD), rng.randrange(1, N_SELF))
    raise ValueError(cause)


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def run_seed(seed: int) -> dict:
    world = CompositionalWorld.generate(seed)
    calibration = calibrate_factorized(world)

    # Calibration must reconstruct every held-out world/self composition exactly.
    compositional_exact = all(
        calibration.predict((x, theta)) == world.signature((x, theta))
        for x in range(N_WORLD)
        for theta in range(N_SELF)
    )

    rng = random.Random(60000 + seed)
    random_rng = random.Random(70000 + seed)
    factorized: list[TrialResult] = []
    random_policy: list[TrialResult] = []
    closed: list[MonolithicResult] = []
    by_cause: dict[str, dict[str, list[float]]] = {
        cause: {"factorized_pair": [], "factorized_cause": [], "random_pair": []}
        for cause in CAUSES
    }

    previous = (0, 0)
    for cause in CAUSES:
        for _ in range(TRIALS_PER_CAUSE):
            target = target_for_cause(rng, cause, previous)
            active = identify_factorized(world, calibration, previous, target)
            random_result = identify_factorized(
                world,
                calibration,
                previous,
                target,
                random_actions=True,
                rng=random_rng,
            )
            closed_result = monolithic_closed_world(world, previous, target)
            factorized.append(active)
            random_policy.append(random_result)
            closed.append(closed_result)
            by_cause[cause]["factorized_pair"].append(active.probes_to_pair)
            by_cause[cause]["factorized_cause"].append(active.probes_to_cause)
            by_cause[cause]["random_pair"].append(random_result.probes_to_pair)

    both_closed = [
        result.correct
        for result, cause in zip(
            closed,
            [cause for cause in CAUSES for _ in range(TRIALS_PER_CAUSE)],
        )
        if cause == "both"
    ]

    full_joint_bits = N_WORLD * N_SELF * N_ACTIONS
    return {
        "compositional_reconstruction_exact": compositional_exact,
        "calibration_scalar_pokes": calibration.scalar_pokes,
        "factorized_stored_bits": calibration.stored_bits,
        "full_joint_stored_bits": full_joint_bits,
        "compression_vs_full_joint": calibration.stored_bits / full_joint_bits,
        "factorized_pair_accuracy": mean([float(r.pair_correct) for r in factorized]),
        "factorized_cause_accuracy": mean([float(r.cause_correct) for r in factorized]),
        "factorized_mean_pair_probes": mean([r.probes_to_pair for r in factorized]),
        "factorized_mean_cause_probes": mean([r.probes_to_cause for r in factorized]),
        "random_mean_pair_probes": mean([r.probes_to_pair for r in random_policy]),
        "random_cause_accuracy": mean([float(r.cause_correct) for r in random_policy]),
        "monolithic_closed_accuracy": mean([float(r.correct) for r in closed]),
        "monolithic_closed_cause_accuracy": mean([float(r.cause_correct) for r in closed]),
        "monolithic_closed_both_accuracy": mean([float(value) for value in both_closed]),
        "monolithic_closed_mean_probes": mean([r.probes for r in closed]),
        "monolithic_exact_open_world_probes": float(monolithic_exact_open_world(world, (1, 1))),
        "by_cause": {
            cause: {
                key: mean(values)
                for key, values in metrics.items()
            }
            for cause, metrics in by_cause.items()
        },
    }


def aggregate(seed_results: list[dict]) -> dict:
    scalar_keys = [
        key for key, value in seed_results[0].items()
        if isinstance(value, (int, float, bool))
    ]
    result = {
        key: mean([float(seed_result[key]) for seed_result in seed_results])
        for key in scalar_keys
    }
    result["by_cause"] = {
        cause: {
            key: mean([
                seed_result["by_cause"][cause][key]
                for seed_result in seed_results
            ])
            for key in seed_results[0]["by_cause"][cause]
        }
        for cause in CAUSES
    }
    return result


def run_all() -> dict:
    seed_results = [run_seed(seed) for seed in SEEDS]
    metrics = aggregate(seed_results)

    passed = (
        metrics["compositional_reconstruction_exact"] == 1.0
        and metrics["factorized_pair_accuracy"] == 1.0
        and metrics["factorized_cause_accuracy"] == 1.0
        and metrics["compression_vs_full_joint"] <= 0.35
        and metrics["factorized_mean_pair_probes"] < 0.60 * metrics["monolithic_exact_open_world_probes"]
        and metrics["factorized_mean_cause_probes"] < metrics["random_mean_pair_probes"]
        and metrics["monolithic_closed_both_accuracy"] <= 0.25
    )

    return {
        "schema": "alternative-neuron-gate6-v1",
        "gate": "G6_WORLD_VS_SELF_ATTRIBUTION",
        "pass": passed,
        "classification": (
            "FACTORIZED_WORLD_SELF_MODEL_COMPOSES_UNSEEN_JOINT_RESPONSES_AND_ATTRIBUTES_CHANGE_WITH_FEWER_SCALAR_POKES"
            if passed
            else "GATE6_FAILED"
        ),
        "setup": {
            "world_states": N_WORLD,
            "self_operator_states": N_SELF,
            "actions": N_ACTIONS,
            "trials_per_cause_per_seed": TRIALS_PER_CAUSE,
            "seeds": list(SEEDS),
            "calibration": (
                "controlled star: all world states at self=0 plus all self states at world=0; "
                "test cause labels are never supplied"
            ),
            "response_law": "R(x, theta, a) = W(x,a) XOR S(theta,a)",
        },
        "metrics": metrics,
        "attackers": {
            "random_diagnostic_pokes": (
                "same exact factorized model, but random unused intervention order"
            ),
            "monolithic_closed_equal_bits": (
                "stores the same eleven 12-bit star signatures and assumes one cached joint state must be current"
            ),
            "monolithic_exact_open_world": (
                "refuses the closed-world assumption; arbitrary unknown joint signature costs all 12 scalar responses"
            ),
            "full_joint_oracle": (
                "would store all 32 joint signatures (384 bits) rather than the 132-bit factorized star model"
            ),
        },
        "claim_boundary": (
            "Synthetic XOR-compositional response family with known finite world/self component families and controlled star calibration. "
            "The result tests the value of a correct factorization, not spontaneous discovery of selfhood, general intelligence, biology, "
            "or consciousness. Novel world/self component states are not handled in this gate."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/GATE6_SELF_WORLD_ATTRIBUTION.json")
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
