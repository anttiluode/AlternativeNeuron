#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


N_ACTIONS = 12
SEEDS = tuple(range(64))


def xor_bits(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x ^ y for x, y in zip(a, b))


def make_equivalent_pair(seed: int) -> dict:
    """Construct two causal stories with identical consequences for every poke.

    Story W: the world changed while the self/operator stayed fixed.
    Story S: the world stayed fixed while the self/operator changed.

    A shared delta is moved from the world factor to the self factor.  The
    post-change action-response signature is therefore exactly the same under
    both stories for every possible intervention.
    """

    rng = random.Random(610000 + seed)
    base_world = tuple(rng.randrange(2) for _ in range(N_ACTIONS))
    base_self = tuple(rng.randrange(2) for _ in range(N_ACTIONS))
    delta = tuple(rng.randrange(2) for _ in range(N_ACTIONS))
    if not any(delta):
        delta = (1,) + delta[1:]

    before = xor_bits(base_world, base_self)

    world_changed = xor_bits(xor_bits(base_world, delta), base_self)
    self_changed = xor_bits(base_world, xor_bits(base_self, delta))

    return {
        "before": before,
        "world_changed": world_changed,
        "self_changed": self_changed,
        "delta": delta,
    }


def adaptive_transcript(signature: tuple[int, ...], seed: int) -> list[tuple[int, int]]:
    """A representative adaptive poker; equivalence makes policy choice irrelevant."""

    rng = random.Random(620000 + seed)
    remaining = list(range(N_ACTIONS))
    transcript: list[tuple[int, int]] = []
    running_hash = 0
    while remaining:
        # Choose the next action from the entire transcript so far.  Two worlds
        # that produce the same transcript must therefore choose the same next
        # intervention too.
        index = (running_hash + rng.randrange(len(remaining))) % len(remaining)
        action = remaining.pop(index)
        response = signature[action]
        transcript.append((action, response))
        running_hash = (running_hash * 131 + action * 17 + response * 7 + 1) % 1000003
    return transcript


def run_all() -> dict:
    exact_signature_matches = 0
    exact_transcript_matches = 0
    different_ground_truth = 0

    for seed in SEEDS:
        pair = make_equivalent_pair(seed)
        same_signature = pair["world_changed"] == pair["self_changed"]
        exact_signature_matches += int(same_signature)

        transcript_world = adaptive_transcript(pair["world_changed"], seed)
        transcript_self = adaptive_transcript(pair["self_changed"], seed)
        exact_transcript_matches += int(transcript_world == transcript_self)
        different_ground_truth += 1  # by construction: W cause vs S cause

    signature_equivalence = exact_signature_matches / len(SEEDS)
    adaptive_equivalence = exact_transcript_matches / len(SEEDS)

    # Equal prior over the two observationally identical causal stories.  No
    # classifier using only the transcript can beat chance because its input is
    # identical in each paired case.
    transcript_only_bayes_accuracy = 0.5

    # Efference/proprioceptive control: one privileged bit records whether the
    # machine's own operator update occurred.  This is not inferred from the
    # poke responses and is included only to show what kind of asymmetry breaks
    # the impossibility.
    efference_bit_accuracy = 1.0

    passed = (
        signature_equivalence == 1.0
        and adaptive_equivalence == 1.0
        and transcript_only_bayes_accuracy == 0.5
        and efference_bit_accuracy == 1.0
    )

    return {
        "schema": "alternative-neuron-gate6b-v1",
        "gate": "G6B_SELF_WORLD_NONIDENTIFIABILITY",
        "pass": passed,
        "classification": (
            "POKING_ALONE_CANNOT_IDENTIFY_SELF_VS_WORLD_WHEN_CAUSAL_STORIES_ARE_OBSERVATIONALLY_EQUIVALENT"
            if passed
            else "GATE6B_FAILED"
        ),
        "setup": {
            "actions": N_ACTIONS,
            "paired_worlds": len(SEEDS),
            "construction": (
                "R_before=W xor S; WORLD story=(W xor delta) xor S; "
                "SELF story=W xor (S xor delta)"
            ),
        },
        "metrics": {
            "post_change_signature_equivalence": signature_equivalence,
            "adaptive_full_transcript_equivalence": adaptive_equivalence,
            "best_transcript_only_attribution_accuracy_equal_prior": transcript_only_bayes_accuracy,
            "one_bit_efference_control_accuracy": efference_bit_accuracy,
        },
        "meaning": (
            "Gate 6's positive result requires an anchored world/self factorization. "
            "Action-conditioned evidence by itself does not manufacture that semantic distinction. "
            "If world-change and self-change hypotheses predict the same response to every possible poke, "
            "no adaptive probing policy can distinguish them. An asymmetry such as efference copy, proprioception, "
            "known self-update dynamics, or another privileged causal constraint is required."
        ),
        "claim_boundary": (
            "This is a constructed observational-equivalence counterexample, not a model of biological efference copy "
            "or a theorem about consciousness. It fences the computational claim: intervention adds information only "
            "when competing hypotheses actually differ in their intervention consequences."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/GATE6B_SELF_WORLD_NONIDENTIFIABILITY.json")
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
