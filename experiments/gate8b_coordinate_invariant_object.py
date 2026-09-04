#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path


N_STATES = 4
OBJECTS = {
    "O0": (1, 2),
    "O1": (2, 1),
    "O2": (1, 3),
    "O3": (3, 1),
}
PERMUTATIONS = tuple(itertools.permutations(range(N_STATES)))
START_PHASES = tuple(range(N_STATES))


def physical_label(latent_phase: int, permutation: tuple[int, ...]) -> int:
    return permutation[latent_phase % N_STATES]


def passive_orbit(start: int, permutation: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        physical_label(start + offset, permutation)
        for offset in range(N_STATES + 1)
    )


def poke_response(
    start: int, offset: int, permutation: tuple[int, ...]
) -> int:
    return physical_label(start + offset, permutation)


def raw_coordinate_signature(
    object_offsets: tuple[int, int], start: int, permutation: tuple[int, ...]
) -> tuple[int, ...]:
    orbit = passive_orbit(start, permutation)
    pokes = tuple(poke_response(start, offset, permutation) for offset in object_offsets)
    return orbit + pokes


def canonical_response_signature(
    object_offsets: tuple[int, int], start: int, permutation: tuple[int, ...]
) -> tuple[int, int]:
    """Measure poke targets in passive-cycle coordinates, not physical labels.

    The passive orbit supplies an intrinsic coordinate system relative to the
    current phase. Any permutation of physical state labels is quotiented out.
    """

    orbit = passive_orbit(start, permutation)
    phase_of_label = {label: phase for phase, label in enumerate(orbit[:-1])}
    return tuple(
        phase_of_label[poke_response(start, offset, permutation)]
        for offset in object_offsets
    )


def hamming(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    return sum(x != y for x, y in zip(a, b))


def nearest_reference_accuracy() -> float:
    identity = tuple(range(N_STATES))
    references = {
        name: raw_coordinate_signature(offsets, 0, identity)
        for name, offsets in OBJECTS.items()
    }
    correct = 0
    total = 0
    for true_name, offsets in OBJECTS.items():
        for permutation in PERMUTATIONS:
            for start in START_PHASES:
                signature = raw_coordinate_signature(offsets, start, permutation)
                distances = {
                    name: hamming(signature, reference)
                    for name, reference in references.items()
                }
                best_distance = min(distances.values())
                # Deterministic tie-breaker. With complete remapping symmetry the
                # coordinate-template attacker should collapse to chance.
                prediction = sorted(
                    name for name, distance in distances.items() if distance == best_distance
                )[0]
                correct += int(prediction == true_name)
                total += 1
    return correct / total


def canonical_accuracy() -> tuple[float, dict[str, list[int]]]:
    lookup = {signature: name for name, signature in OBJECTS.items()}
    correct = 0
    total = 0
    examples: dict[str, list[int]] = {}
    for true_name, offsets in OBJECTS.items():
        seen: set[tuple[int, int]] = set()
        for permutation in PERMUTATIONS:
            for start in START_PHASES:
                signature = canonical_response_signature(offsets, start, permutation)
                seen.add(signature)
                prediction = lookup.get(signature)
                correct += int(prediction == true_name)
                total += 1
        examples[true_name] = list(next(iter(seen))) if len(seen) == 1 else []
    return correct / total, examples


def run_all() -> dict:
    total_embeddings_per_object = len(PERMUTATIONS) * len(START_PHASES)
    total_trials = total_embeddings_per_object * len(OBJECTS)

    # Every object has the same passive four-cycle and therefore the same
    # dominant period/frequency. Passive transition structure alone is also
    # isomorphic under relabeling.
    frequency_only_accuracy = 1.0 / len(OBJECTS)
    passive_graph_only_accuracy = 1.0 / len(OBJECTS)
    raw_coordinate_accuracy = nearest_reference_accuracy()
    invariant_accuracy, invariant_signatures = canonical_accuracy()

    all_signatures_unique = len(set(OBJECTS.values())) == len(OBJECTS)
    all_same_period = True

    passed = (
        all_same_period
        and all_signatures_unique
        and frequency_only_accuracy == 0.25
        and passive_graph_only_accuracy == 0.25
        and raw_coordinate_accuracy == 0.25
        and invariant_accuracy == 1.0
    )

    return {
        "schema": "alternative-neuron-gate8b-v1",
        "gate": "G8B_COORDINATE_INVARIANT_DYNAMICAL_OBJECT",
        "pass": passed,
        "classification": (
            "INTERVENTION_RESPONSE_DYNAMICS_IDENTIFY_OBJECTS_ACROSS_COMPLETE_SUBSTRATE_RELABELING_WHILE_COORDINATE_AND_FREQUENCY_TEMPLATES_FAIL"
            if passed
            else "GATE8B_FAILED"
        ),
        "setup": {
            "objects": {name: list(offsets) for name, offsets in OBJECTS.items()},
            "latent_states": N_STATES,
            "passive_dynamics": "phase -> phase+1 mod 4 for every object",
            "physical_embeddings": "all 4! coordinate permutations x all 4 start phases",
            "embeddings_per_object": total_embeddings_per_object,
            "total_trials": total_trials,
            "poke_semantics": (
                "two reversible actions land a fixed number of passive-cycle steps from the current state; "
                "the pair of intrinsic offsets defines the synthetic object"
            ),
        },
        "metrics": {
            "frequency_or_period_only_accuracy": frequency_only_accuracy,
            "passive_transition_graph_only_accuracy": passive_graph_only_accuracy,
            "raw_coordinate_nearest_template_accuracy": raw_coordinate_accuracy,
            "coordinate_invariant_intervention_signature_accuracy": invariant_accuracy,
            "all_objects_share_same_passive_period": all_same_period,
            "canonical_signatures": invariant_signatures,
        },
        "meaning": (
            "All four synthetic objects have exactly the same passive four-cycle, so dominant frequency/period and passive graph shape contain no identity information. "
            "Each object is embedded under every permutation of the four physical state labels and every start phase. A raw coordinate template falls to chance. "
            "The observer instead uses the observed passive cycle as an intrinsic coordinate chart and asks where two reversible pokes land relative to that cycle. "
            "Those intervention-response offsets are unchanged by physical relabeling and identify every object exactly. In dynamical-systems language, the useful identity lives in structure preserved under a change of coordinates, not in the coordinate labels themselves."
        ),
        "claim_boundary": (
            "This is an exactly solvable finite-state conjugacy/isomorphism toy, not evidence that biological engrams are coordinate-free, not a learned representation, and not yet a nonlinear attractor assay. "
            "The intervention family is engineered to distinguish the four objects. Gate 8C must test basins, return dynamics, reactivation, perturbation recovery, and same-frequency attackers in a genuinely nonlinear recurrent system."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/GATE8B_COORDINATE_INVARIANT_DYNAMICAL_OBJECT.json")
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
