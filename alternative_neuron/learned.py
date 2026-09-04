from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Sequence

from .core import CONTEXTS_PER_GROUP, N_CONTEXTS, SlowStructure


@dataclass(frozen=True)
class UnknownResponseWorld:
    """A poke world whose response codebook is hidden from the agent.

    The environment builds a deterministic random binary response signature for
    every context. Signatures are unique within each passive group. The agent
    may only learn them by issuing scalar pokes.
    """

    seed: int = 20260904
    n_actions: int = 12

    def __post_init__(self) -> None:
        rng = random.Random(self.seed)
        signatures: list[tuple[int, ...]] = []
        for _group in range(2):
            seen: set[tuple[int, ...]] = set()
            while len(seen) < CONTEXTS_PER_GROUP:
                signature = tuple(rng.randrange(2) for _ in range(self.n_actions))
                seen.add(signature)
            # Sort for deterministic order independent of set hashing.
            signatures.extend(sorted(seen))
        object.__setattr__(self, "signatures", tuple(signatures))

    def passive_group(self, context: int) -> int:
        if not 0 <= context < N_CONTEXTS:
            raise ValueError("bad context")
        return context // CONTEXTS_PER_GROUP

    def poke(self, context: int, action: int) -> int:
        if not 0 <= action < self.n_actions:
            raise ValueError("bad action")
        return self.signatures[context][action]

    def exhaustive_signature(self, context: int) -> tuple[int, ...]:
        return tuple(self.poke(context, action) for action in range(self.n_actions))


@dataclass
class Calibration:
    signatures: list[tuple[int, ...]]
    scalar_pokes: int


def calibrate_labeled(world: UnknownResponseWorld) -> Calibration:
    """Learn the response operator by exhaustive anchored calibration.

    Context labels are supplied during calibration. This removes the preloaded
    response codebook but does NOT solve unsupervised object discovery.
    """
    signatures = [world.exhaustive_signature(context) for context in range(N_CONTEXTS)]
    return Calibration(signatures=signatures, scalar_pokes=N_CONTEXTS * world.n_actions)


def shuffled_calibration(calibration: Calibration, seed: int = 77) -> Calibration:
    rng = random.Random(seed)
    shuffled = list(calibration.signatures)
    for group in range(2):
        lo = group * CONTEXTS_PER_GROUP
        block = shuffled[lo : lo + CONTEXTS_PER_GROUP]
        rng.shuffle(block)
        shuffled[lo : lo + CONTEXTS_PER_GROUP] = block
    return Calibration(signatures=shuffled, scalar_pokes=calibration.scalar_pokes)


def _entropy(n: int) -> float:
    return 0.0 if n <= 1 else math.log2(n)


@dataclass
class LearnedIdentification:
    predicted: int | None
    actions: list[int]
    cost: float


class LearnedPoker:
    """Information-directed poking using a learned, not supplied, codebook."""

    def __init__(
        self,
        world: UnknownResponseWorld,
        calibration: Calibration,
        structure: SlowStructure | None = None,
    ) -> None:
        self.world = world
        self.calibration = calibration
        self.structure = structure or SlowStructure(world.n_actions)

    def _gain(self, candidates: Sequence[int], action: int) -> float:
        groups = [[], []]
        for context in candidates:
            groups[self.calibration.signatures[context][action]].append(context)
        if not groups[0] or not groups[1]:
            return 0.0
        before = _entropy(len(candidates))
        after = sum(
            len(group) / len(candidates) * _entropy(len(group)) for group in groups
        )
        return before - after

    def choose_action(self, candidates: Sequence[int], used: set[int]) -> int | None:
        best: tuple[float, int] | None = None
        for action in range(self.world.n_actions):
            if action in used:
                continue
            score = self._gain(candidates, action) * self.structure.conductance[action]
            if score <= 0:
                continue
            candidate = (score, -action)
            if best is None or candidate > best:
                best = candidate
        return None if best is None else -best[1]

    def identify(self, context: int) -> LearnedIdentification:
        group = self.world.passive_group(context)
        lo = group * CONTEXTS_PER_GROUP
        candidates = list(range(lo, lo + CONTEXTS_PER_GROUP))
        used: set[int] = set()
        actions: list[int] = []
        cost = 0.0

        while len(candidates) > 1:
            action = self.choose_action(candidates, used)
            if action is None:
                break
            used.add(action)
            actions.append(action)
            cost += self.structure.cost(action)
            observed = self.world.poke(context, action)
            candidates = [
                candidate
                for candidate in candidates
                if self.calibration.signatures[candidate][action] == observed
            ]
            if not candidates:
                break

        predicted = candidates[0] if len(candidates) == 1 else None
        return LearnedIdentification(predicted=predicted, actions=actions, cost=cost)
