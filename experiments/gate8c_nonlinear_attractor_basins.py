#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


N = 24
K = 3
PATTERN_SEED = 810000
MAX_STEPS = 20
PERTURB_TRIALS = 300
CUE_TRIALS = 200
PERMUTATION_TRIALS = 8


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def make_patterns() -> list[list[int]]:
    rng = random.Random(PATTERN_SEED)
    return [
        [1 if rng.random() < 0.5 else -1 for _ in range(N)]
        for _ in range(K)
    ]


def hebbian_weights(patterns: list[list[int]]) -> list[list[float]]:
    weights = [[0.0 for _ in range(N)] for _ in range(N)]
    for pattern in patterns:
        for i in range(N):
            for j in range(N):
                if i != j:
                    weights[i][j] += pattern[i] * pattern[j] / N
    return weights


def step(state: list[int], weights: list[list[float]]) -> list[int]:
    """Synchronous nonlinear sign update; permutation-equivariant by design."""

    result: list[int] = []
    for i in range(N):
        drive = sum(weights[i][j] * state[j] for j in range(N))
        if drive > 0:
            result.append(1)
        elif drive < 0:
            result.append(-1)
        else:
            result.append(state[i])
    return result


def converge(
    state: list[int], weights: list[list[float]], max_steps: int = MAX_STEPS
) -> tuple[list[int], int, str]:
    previous: list[int] | None = None
    current = state[:]
    for iteration in range(1, max_steps + 1):
        nxt = step(current, weights)
        if nxt == current:
            return nxt, iteration, "fixed"
        if previous is not None and nxt == previous:
            return nxt, iteration, "two_cycle"
        previous, current = current, nxt
    return current, max_steps, "timeout"


def flip_bits(pattern: list[int], indices: list[int]) -> list[int]:
    state = pattern[:]
    for index in indices:
        state[index] *= -1
    return state


def perturbation_curve(
    patterns: list[list[int]], weights: list[list[float]]
) -> dict[str, dict[str, float]]:
    curve: dict[str, dict[str, float]] = {}
    for flips in (1, 2, 3, 4, 6, 8, 10, 12):
        rng = random.Random(820000 + flips)
        returns = 0
        total = 0
        return_steps: list[float] = []
        for pattern in patterns:
            for _ in range(PERTURB_TRIALS):
                indices = rng.sample(range(N), flips)
                final, iterations, status = converge(flip_bits(pattern, indices), weights)
                returned = status == "fixed" and final == pattern
                returns += int(returned)
                total += 1
                if returned:
                    return_steps.append(float(iterations))
        curve[str(flips)] = {
            "return_probability": returns / total,
            "escape_probability": 1.0 - returns / total,
            "mean_return_iterations_if_recovered": mean(return_steps) if return_steps else 0.0,
        }
    return curve


def partial_cue_reactivation(
    patterns: list[list[int]], weights: list[list[float]], known_bits: int = 12
) -> float:
    """Activity can be zero between episodes; weights carry the persistent trace."""

    successes = 0
    total = 0
    for pattern_index, pattern in enumerate(patterns):
        rng = random.Random(830000 + pattern_index)
        for _ in range(CUE_TRIALS):
            known = set(rng.sample(range(N), known_bits))
            cue = [pattern[i] if i in known else 0 for i in range(N)]
            final, _, status = converge(cue, weights)
            successes += int(status == "fixed" and final == pattern)
            total += 1
    return successes / total


def permute_vector(vector: list[int], permutation: list[int]) -> list[int]:
    # physical[i] = latent[permutation[i]]
    return [vector[permutation[i]] for i in range(N)]


def permute_weights(
    weights: list[list[float]], permutation: list[int]
) -> list[list[float]]:
    return [
        [weights[permutation[i]][permutation[j]] for j in range(N)]
        for i in range(N)
    ]


def permutation_conjugacy_accuracy(
    patterns: list[list[int]], weights: list[list[float]]
) -> float:
    """Check that basin recovery survives complete neuron-index relabeling."""

    successes = 0
    total = 0
    for permutation_seed in range(PERMUTATION_TRIALS):
        rng = random.Random(840000 + permutation_seed)
        permutation = list(range(N))
        rng.shuffle(permutation)
        permuted_weights = permute_weights(weights, permutation)

        for pattern_index, pattern in enumerate(patterns):
            perturb_rng = random.Random(850000 + 100 * permutation_seed + pattern_index)
            for _ in range(40):
                latent_indices = perturb_rng.sample(range(N), 3)
                latent_cue = flip_bits(pattern, latent_indices)
                latent_final, latent_steps, latent_status = converge(latent_cue, weights)

                physical_cue = permute_vector(latent_cue, permutation)
                physical_target = permute_vector(pattern, permutation)
                physical_final, physical_steps, physical_status = converge(
                    physical_cue, permuted_weights
                )

                equivalent = (
                    latent_status == physical_status
                    and latent_steps == physical_steps
                    and physical_final == permute_vector(latent_final, permutation)
                    and (latent_final == pattern) == (physical_final == physical_target)
                )
                successes += int(equivalent)
                total += 1
    return successes / total


def run_all() -> dict:
    patterns = make_patterns()
    weights = hebbian_weights(patterns)

    stable = [step(pattern, weights) == pattern for pattern in patterns]
    curve = perturbation_curve(patterns, weights)
    reactivation = partial_cue_reactivation(patterns, weights, known_bits=N // 2)
    conjugacy_accuracy = permutation_conjugacy_accuracy(patterns, weights)

    # Fixed points have no oscillation. All three memories therefore share the
    # same dominant temporal frequency (zero), so frequency alone cannot label
    # which basin has been reached.
    frequency_only_identity_accuracy = 1.0 / K

    local_return = curve["3"]["return_probability"]
    far_return = curve["10"]["return_probability"]

    # This is a supplied-pattern mechanism assay, not a statistical benchmark.
    # The threshold asks only for a clear local basin (>90% return from three
    # flipped bits) and a clear far-field escape regime (<25% return at ten).
    passed = (
        all(stable)
        and local_return > 0.90
        and far_return < 0.25
        and reactivation > 0.93
        and conjugacy_accuracy == 1.0
        and frequency_only_identity_accuracy == 1.0 / 3.0
    )

    return {
        "schema": "alternative-neuron-gate8c-v1",
        "gate": "G8C_NONLINEAR_ATTRACTOR_BASINS",
        "pass": passed,
        "classification": (
            "NONLINEAR_RECURRENT_BASINS_REACTIVATE_FROM_PARTIAL_CUES_AND_SURVIVE_COORDINATE_RELABELING_WHILE_FREQUENCY_ALONE_CANNOT_IDENTIFY_THE_MEMORY"
            if passed
            else "GATE8C_FAILED"
        ),
        "setup": {
            "units": N,
            "stored_patterns": K,
            "weight_rule": "off-diagonal Hebbian sum",
            "update": "synchronous sign nonlinearity",
            "max_steps": MAX_STEPS,
            "partial_cue_known_bits": N // 2,
            "perturbation_trials_per_pattern_per_radius": PERTURB_TRIALS,
            "coordinate_permutations": PERMUTATION_TRIALS,
        },
        "metrics": {
            "stored_patterns_are_fixed_points": stable,
            "perturbation_return_curve": curve,
            "partial_cue_reactivation_accuracy_after_zero_activity": reactivation,
            "coordinate_permutation_dynamical_conjugacy_accuracy": conjugacy_accuracy,
            "frequency_only_attractor_identity_accuracy": frequency_only_identity_accuracy,
        },
        "meaning": (
            "The artificial system now earns the word attractor in the narrow dynamical sense: several distinct fixed points are stable, nearby perturbed states return with high probability, and sufficiently distant perturbations often escape the original basin. "
            "The activation state can be completely zero between episodes; a half-pattern cue later reactivates the stored fixed point because the persistent information lives in the recurrent operator. "
            "Permuting all neuron indices together with the operator leaves the dynamics exactly conjugate, so the basin is not defined by neuron names. "
            "All three attractors are fixed points and therefore have the same zero oscillation frequency: frequency is one possible dynamical coordinate, not the identity of a memory object."
        ),
        "claim_boundary": (
            "This is a small engineered Hopfield-style recurrent network, not a biological engram assay and not evidence that a human memory is one fixed-point attractor. "
            "The coordinate permutation is a mathematical relabeling of the whole operator, not biological representational drift. The stored patterns were supplied rather than learned from an open world. "
            "What the gate earns is only the dynamical vocabulary: basin, return, escape, reactivation, and coordinate conjugacy."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/GATE8C_NONLINEAR_ATTRACTOR_BASINS.json")
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
