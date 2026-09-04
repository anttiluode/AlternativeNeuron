#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


POSITIONS = (0, 1, 2)
DIRECTIONS = (-1, 1)


@dataclass(frozen=True)
class RingState:
    """Hidden moving state on a three-position ring.

    The scalar observation exposes only position. Direction is hidden. At
    position 0 the two directions therefore have the same instantaneous
    observation but different futures.
    """

    position: int
    direction: int

    def step(self) -> "RingState":
        return RingState((self.position + self.direction) % 3, self.direction)

    def back(self) -> "RingState":
        return RingState((self.position - self.direction) % 3, self.direction)

    def observe(self) -> int:
        return self.position


def history(state: RingState, length: int = 3) -> tuple[int, ...]:
    states = [state]
    cursor = state
    for _ in range(length - 1):
        cursor = cursor.back()
        states.append(cursor)
    states.reverse()
    return tuple(item.observe() for item in states)


def next_observation(state: RingState) -> int:
    return state.step().observe()


def reversible_step_probe(state: RingState) -> int:
    """Read one counterfactual natural step and then conceptually roll it back.

    The hidden state passed to this function is immutable, so the probe has no
    persistent side effect. It is the smallest active control for the claim:
    when the present point aliases two dynamical states, a reversible
    intervention can expose the direction of motion.
    """

    return state.step().observe()


def bayes_accuracy(features: list[tuple[object, int]]) -> float:
    """Exact empirical Bayes accuracy under a balanced finite assay."""

    table: dict[object, dict[int, int]] = {}
    for feature, label in features:
        counts = table.setdefault(feature, {})
        counts[label] = counts.get(label, 0) + 1
    correct = sum(max(counts.values()) for counts in table.values())
    return correct / len(features)


def run_all() -> dict:
    # Evaluate only the aliased crossing position. Direction is balanced.
    states = [RingState(0, direction) for direction in DIRECTIONS]

    instant_features: list[tuple[object, int]] = []
    bag_features: list[tuple[object, int]] = []
    ordered_features: list[tuple[object, int]] = []
    probe_features: list[tuple[object, int]] = []
    oracle_features: list[tuple[object, int]] = []

    examples = []
    for state in states:
        label = next_observation(state)
        ordered = history(state, 3)
        unordered = tuple(sorted(ordered))
        probed = reversible_step_probe(state)

        instant_features.append((state.observe(), label))
        bag_features.append((unordered, label))
        ordered_features.append((ordered, label))
        probe_features.append(((state.observe(), probed), label))
        oracle_features.append((state.direction, label))

        examples.append(
            {
                "direction": state.direction,
                "instant": state.observe(),
                "ordered_window": list(ordered),
                "unordered_multiset": list(unordered),
                "reversible_probe_response": probed,
                "next_observation": label,
            }
        )

    instant_accuracy = bayes_accuracy(instant_features)
    unordered_accuracy = bayes_accuracy(bag_features)
    ordered_accuracy = bayes_accuracy(ordered_features)
    probe_accuracy = bayes_accuracy(probe_features)
    oracle_accuracy = bayes_accuracy(oracle_features)

    same_instant = len({example["instant"] for example in examples}) == 1
    same_unordered = len(
        {tuple(example["unordered_multiset"]) for example in examples}
    ) == 1
    different_ordered = len(
        {tuple(example["ordered_window"]) for example in examples}
    ) == len(examples)

    passed = (
        same_instant
        and same_unordered
        and different_ordered
        and instant_accuracy == 0.5
        and unordered_accuracy == 0.5
        and ordered_accuracy == 1.0
        and probe_accuracy == 1.0
        and oracle_accuracy == 1.0
    )

    return {
        "schema": "alternative-neuron-gate8a-v1",
        "gate": "G8A_WIDE_PRESENT_STATE_ALIASING",
        "pass": passed,
        "classification": (
            "ORDERED_TRAJECTORY_FRAGMENT_OR_REVERSIBLE_PROBE_RESOLVES_AN_INSTANTANEOUSLY_ALIASED_MOVING_STATE"
            if passed
            else "GATE8A_FAILED"
        ),
        "setup": {
            "latent_state": "three-position ring plus hidden direction +/-1",
            "observation": "position only",
            "evaluated_crossing": 0,
            "window_length": 3,
            "directions": list(DIRECTIONS),
            "examples": examples,
        },
        "metrics": {
            "instantaneous_observation_accuracy": instant_accuracy,
            "unordered_same_samples_accuracy": unordered_accuracy,
            "causal_ordered_window_accuracy": ordered_accuracy,
            "reversible_one_step_probe_accuracy": probe_accuracy,
            "oracle_hidden_direction_accuracy": oracle_accuracy,
            "instant_is_exactly_aliased": same_instant,
            "unordered_window_is_exactly_aliased": same_unordered,
            "ordered_window_separates_directions": different_ordered,
        },
        "meaning": (
            "At the observed crossing y(t)=0, clockwise and counterclockwise latent states are observationally identical but have different futures. "
            "Even the same three observed values contain no information if temporal order is discarded: both histories have multiset {0,1,2}. "
            "Their ordered histories are [1,2,0] versus [2,1,0], which identifies the hidden direction exactly. "
            "If history is unavailable, one reversible trial step also exposes the direction. This gives WidePresent a precise minimal role: for a moving system, the useful present may be an ordered trajectory fragment rather than a point sample."
        ),
        "claim_boundary": (
            "This is a finite deterministic aliasing construction, not an attractor, engram, biological neuron, or proof that temporal windows are always necessary. "
            "The reversible probe is an idealized rollback query. Gate 8B must test whether a dynamical identity survives changes of physical coordinates, and Gate 8C must introduce genuine nonlinear basins before using the word attractor for the artificial system."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/GATE8A_WIDE_PRESENT_STATE_ALIASING.json")
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
