#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from alternative_neuron import (
    ActivePoker,
    AlternativeNeuron,
    PokeWorld,
    SlowStructure,
    silent_switch_sequence,
    visible_event_sequence,
)


def accuracy(values: list[bool]) -> float:
    return sum(values) / max(1, len(values))


def gate0(world: PokeWorld) -> dict:
    uniform = SlowStructure(world.n_actions)
    poker = ActivePoker(world, uniform)

    passive_correct = []
    active_correct = []
    negative_correct = []
    probes = []

    for context in range(16):
        passive_guess = world.candidates_from_passive(context)[0]
        passive_correct.append(passive_guess == context)

        active = poker.identify(context, state_dependent=True)
        active_correct.append(active.predicted == context)
        probes.append(len(active.actions))

        negative = poker.identify(context, state_dependent=False)
        negative_correct.append(negative.predicted == context)

    result = {
        "passive_accuracy": accuracy(passive_correct),
        "active_poke_accuracy": accuracy(active_correct),
        "state_independent_poke_accuracy": accuracy(negative_correct),
        "mean_paid_pokes": sum(probes) / len(probes),
    }
    result["pass"] = (
        result["passive_accuracy"] <= 0.125
        and result["active_poke_accuracy"] == 1.0
        and result["state_independent_poke_accuracy"] <= 0.125
        and result["mean_paid_pokes"] <= 3.0
    )
    result["classification"] = (
        "STATE_DEPENDENT_INTERVENTION_RESCUES_PASSIVE_AMBIGUITY"
        if result["pass"]
        else "GATE0_FAILED"
    )
    return result


def run_sequence(sequence: list[int], *, use_memory: bool, structure: SlowStructure | None = None) -> dict:
    neuron = AlternativeNeuron(structure=structure)
    correct: list[bool] = []
    probes = 0
    cost = 0.0
    surprises = 0
    for context in sequence:
        step = neuron.step(context, use_memory=use_memory)
        correct.append(step.correct)
        probes += step.probes
        cost += step.probe_cost
        surprises += int(step.surprised)
    return {
        "accuracy": accuracy(correct),
        "paid_pokes": probes,
        "probe_cost": cost,
        "surprises": surprises,
    }


def gate1() -> dict:
    visible = visible_event_sequence(events=64, dwell=8)
    with_memory = run_sequence(visible, use_memory=True)
    without_memory = run_sequence(visible, use_memory=False)
    silent = run_sequence(silent_switch_sequence(), use_memory=True)

    reduction = without_memory["paid_pokes"] / with_memory["paid_pokes"]
    result = {
        "visible_changes_with_memory": with_memory,
        "visible_changes_no_memory": without_memory,
        "probe_reduction_x": reduction,
        "silent_same_group_switch": silent,
    }
    result["pass"] = (
        with_memory["accuracy"] == 1.0
        and reduction >= 7.9
        and silent["accuracy"] <= 0.5
    )
    result["classification"] = (
        "MEMORY_AMORTIZES_PERSISTENT_EVENTS_BUT_CHEAP_SURPRISE_HAS_A_BLIND_SPOT"
        if result["pass"]
        else "GATE1_FAILED"
    )
    return result


def trained_structures(world: PokeWorld) -> tuple[SlowStructure, SlowStructure, list[float]]:
    traffic_source = SlowStructure(world.n_actions)
    poker = ActivePoker(world, traffic_source)
    for episode in range(1024):
        context = episode % 16
        identification = poker.identify(context)
        traffic_source.record(identification.actions)

    traffic = list(traffic_source.traffic)

    adapted = SlowStructure(world.n_actions)
    adapted.traffic = list(traffic)
    adapted.consolidate()

    shuffled = SlowStructure(world.n_actions)
    shuffled.traffic = list(traffic)
    shuffled.consolidate(shuffled=True, seed=20260904)

    return adapted, shuffled, traffic


def mean_identification_cost(world: PokeWorld, structure: SlowStructure) -> float:
    poker = ActivePoker(world, structure)
    return sum(poker.identify(context).cost for context in range(16)) / 16.0


def gate2(world: PokeWorld) -> tuple[dict, SlowStructure, SlowStructure]:
    frozen = SlowStructure(world.n_actions)
    adapted, shuffled, traffic = trained_structures(world)

    frozen_cost = mean_identification_cost(world, frozen)
    adapted_cost = mean_identification_cost(world, adapted)
    shuffled_cost = mean_identification_cost(world, shuffled)
    budget_error = abs(sum(adapted.conductance) - adapted.budget)

    result = {
        "traffic": traffic,
        "frozen_mean_cost": frozen_cost,
        "adapted_mean_cost": adapted_cost,
        "shuffled_traffic_mean_cost": shuffled_cost,
        "adapted_over_frozen": adapted_cost / frozen_cost,
        "shuffled_over_frozen": shuffled_cost / frozen_cost,
        "budget_error": budget_error,
        "conductance": adapted.conductance,
    }
    result["pass"] = (
        adapted_cost <= 0.40 * frozen_cost
        and shuffled_cost >= 1.25 * frozen_cost
        and budget_error <= 1e-12
    )
    result["classification"] = (
        "REPEATED_PROBE_TRAFFIC_RESHAPES_FIXED_BUDGET_TRANSPORT_AND_CHANGES_FUTURE_SENSING_COST"
        if result["pass"]
        else "GATE2_FAILED"
    )
    return result, adapted, shuffled


def passive_sequence_accuracy(world: PokeWorld, sequence: list[int]) -> float:
    correct = 0
    for context in sequence:
        correct += int(world.candidates_from_passive(context)[0] == context)
    return correct / len(sequence)


def gate3(world: PokeWorld, adapted: SlowStructure, shuffled: SlowStructure) -> dict:
    sequence = visible_event_sequence(events=64, dwell=8)

    frozen_memory = run_sequence(sequence, use_memory=True)
    frozen_no_memory = run_sequence(sequence, use_memory=False)

    adapted_copy = SlowStructure(world.n_actions)
    adapted_copy.conductance = list(adapted.conductance)
    adapted_copy.traffic = list(adapted.traffic)
    adapted_memory = run_sequence(sequence, use_memory=True, structure=adapted_copy)

    shuffled_copy = SlowStructure(world.n_actions)
    shuffled_copy.conductance = list(shuffled.conductance)
    shuffled_copy.traffic = list(shuffled.traffic)
    shuffled_memory = run_sequence(sequence, use_memory=True, structure=shuffled_copy)

    passive_acc = passive_sequence_accuracy(world, sequence)

    result = {
        "passive_only_accuracy": passive_acc,
        "active_no_memory_frozen": frozen_no_memory,
        "active_memory_frozen": frozen_memory,
        "active_memory_adapted": adapted_memory,
        "active_memory_shuffled_structure": shuffled_memory,
    }
    result["pass"] = (
        adapted_memory["accuracy"] == 1.0
        and adapted_memory["paid_pokes"] <= frozen_no_memory["paid_pokes"] / 7.9
        and adapted_memory["probe_cost"] <= frozen_memory["probe_cost"] * 0.40
        and shuffled_memory["probe_cost"] >= frozen_memory["probe_cost"] * 1.25
        and passive_acc <= 0.125
    )
    result["classification"] = (
        "FAST_POKE_MEDIUM_MEMORY_AND_SLOW_STRUCTURE_COMPOSE"
        if result["pass"]
        else "GATE3_FAILED"
    )
    return result


def run_all() -> dict:
    world = PokeWorld()
    g0 = gate0(world)
    g1 = gate1()
    g2, adapted, shuffled = gate2(world)
    g3 = gate3(world, adapted, shuffled)
    all_pass = all(gate["pass"] for gate in (g0, g1, g2, g3))
    return {
        "schema": "alternative-neuron-gates-v1",
        "gate0_intervention_as_sense": g0,
        "gate1_medium_memory": g1,
        "gate2_slow_structure": g2,
        "gate3_composition": g3,
        "all_pass": all_pass,
        "claim_boundary": (
            "Mechanism toy only. The response codebook is supplied, HOME sees only a coarse group, "
            "and the silent-switch failure is intentional. No claim of biological neuron equivalence, "
            "general intelligence, or subjective experience."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/GATES.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = run_all()
    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")

    if args.check and not result["all_pass"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
