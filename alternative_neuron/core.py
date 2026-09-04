from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Iterable, Sequence


N_CONTEXTS = 16
N_GROUPS = 2
CONTEXTS_PER_GROUP = N_CONTEXTS // N_GROUPS


def _entropy(n: int) -> float:
    return 0.0 if n <= 1 else math.log2(n)


def _parity(value: int, mask: int) -> int:
    return (value & mask).bit_count() & 1


@dataclass(frozen=True)
class PokeWorld:
    """A deliberately tiny partially observed world.

    A free passive read reveals only one coarse group bit. Within that group,
    eight hidden contexts remain indistinguishable. Reversible poke channels
    return state-dependent binary consequences. Seven channels are informative
    parity questions over the hidden three-bit identity; five are decoys.

    The point is not the codebook. It is the causal distinction:
    passive observation can be blind while an intervention response is not.
    """

    action_names: tuple[str, ...] = tuple(
        [f"parity_{mask:03b}" for mask in range(1, 8)]
        + [f"decoy_{i}" for i in range(5)]
    )

    @property
    def n_actions(self) -> int:
        return len(self.action_names)

    def passive_group(self, context: int) -> int:
        self._check_context(context)
        return context // CONTEXTS_PER_GROUP

    def candidates_from_passive(self, context: int) -> list[int]:
        group = self.passive_group(context)
        lo = group * CONTEXTS_PER_GROUP
        return list(range(lo, lo + CONTEXTS_PER_GROUP))

    def response_model(self, context: int, action: int) -> int:
        """Known response model used by the first mechanism gate."""
        self._check_context(context)
        self._check_action(action)
        if action < 7:
            local_identity = context % CONTEXTS_PER_GROUP
            return _parity(local_identity, action + 1)
        # Decoys depend on at most the already-free group bit, so they add no
        # information inside the passive candidate set.
        return self.passive_group(context) if action % 2 else 0

    def poke(self, context: int, action: int, *, state_dependent: bool = True) -> int:
        """Return the scalar consequence of a reversible intervention.

        The negative-control arm removes state dependence. It still returns a
        perfectly valid scalar, but no within-group identity can be learned.
        """
        self._check_context(context)
        self._check_action(action)
        if state_dependent:
            return self.response_model(context, action)
        return self.passive_group(context)

    def _check_context(self, context: int) -> None:
        if not 0 <= context < N_CONTEXTS:
            raise ValueError(f"context must be in [0, {N_CONTEXTS})")

    def _check_action(self, action: int) -> None:
        if not 0 <= action < self.n_actions:
            raise ValueError(f"action must be in [0, {self.n_actions})")


@dataclass
class SlowStructure:
    """A fixed-budget transport allocation over poke channels.

    A channel with conductance g has latency/cost 1/g. Repeatedly useful
    channels accumulate traffic. Consolidation reallocates a fixed global
    budget with a square-root law plus a background body tax, so unused routes
    remain possible rather than collapsing to zero.
    """

    n_actions: int
    background: float = 20.0
    conductance: list[float] = field(init=False)
    traffic: list[float] = field(init=False)

    def __post_init__(self) -> None:
        self.conductance = [1.0] * self.n_actions
        self.traffic = [0.0] * self.n_actions

    @property
    def budget(self) -> float:
        return float(self.n_actions)

    def cost(self, action: int) -> float:
        return 1.0 / self.conductance[action]

    def record(self, actions: Iterable[int]) -> None:
        for action in actions:
            self.traffic[action] += 1.0

    def consolidate(self, *, shuffled: bool = False, seed: int = 20260904) -> None:
        traffic = list(self.traffic)
        if shuffled:
            order = list(range(self.n_actions))
            random.Random(seed).shuffle(order)
            traffic = [traffic[i] for i in order]
        target = [math.sqrt(value + self.background) for value in traffic]
        scale = self.budget / sum(target)
        self.conductance = [scale * value for value in target]


@dataclass
class Identification:
    predicted: int | None
    actions: list[int]
    cost: float
    remaining: list[int]


class ActivePoker:
    """Fast exploratory state: candidate set + information-directed pokes."""

    def __init__(self, world: PokeWorld, structure: SlowStructure | None = None):
        self.world = world
        self.structure = structure or SlowStructure(world.n_actions)

    def _information_gain(self, candidates: Sequence[int], action: int) -> float:
        groups = [[], []]
        for context in candidates:
            groups[self.world.response_model(context, action)].append(context)
        if not groups[0] or not groups[1]:
            return 0.0
        before = _entropy(len(candidates))
        after = sum(
            (len(group) / len(candidates)) * _entropy(len(group))
            for group in groups
        )
        return before - after

    def choose_action(self, candidates: Sequence[int], used: set[int]) -> int | None:
        best: tuple[float, int] | None = None
        for action in range(self.world.n_actions):
            if action in used:
                continue
            gain = self._information_gain(candidates, action)
            # gain / latency = gain * conductance
            score = gain * self.structure.conductance[action]
            if score <= 0:
                continue
            candidate = (score, -action)
            if best is None or candidate > best:
                best = candidate
        return None if best is None else -best[1]

    def identify(self, context: int, *, state_dependent: bool = True) -> Identification:
        candidates = self.world.candidates_from_passive(context)
        used: set[int] = set()
        actions: list[int] = []
        total_cost = 0.0

        while len(candidates) > 1:
            action = self.choose_action(candidates, used)
            if action is None:
                break
            used.add(action)
            actions.append(action)
            total_cost += self.structure.cost(action)
            observed = self.world.poke(context, action, state_dependent=state_dependent)
            candidates = [
                candidate
                for candidate in candidates
                if self.world.response_model(candidate, action) == observed
            ]
            if not candidates:
                break

        predicted = candidates[0] if len(candidates) == 1 else None
        return Identification(predicted, actions, total_cost, candidates)


@dataclass
class MediumMemory:
    """Persistent event memory between fast exploratory episodes.

    The cheap HOME channel is intentionally weak: it reveals only the passive
    group. Therefore memory can safely amortize sensing while a context persists
    and group changes are visible, but it can miss a silent within-group switch.
    That failure is part of the gate, not hidden.
    """

    remembered_context: int | None = None
    remembered_group: int | None = None

    def needs_probe(self, passive_group: int) -> bool:
        return self.remembered_context is None or passive_group != self.remembered_group

    def write(self, context: int, passive_group: int) -> None:
        self.remembered_context = context
        self.remembered_group = passive_group

    def clear(self) -> None:
        self.remembered_context = None
        self.remembered_group = None


@dataclass
class StepResult:
    predicted: int | None
    correct: bool
    probes: int
    probe_cost: float
    surprised: bool


class AlternativeNeuron:
    """Three-timescale toy architecture.

    fast   : candidate/posterior state during active probing
    medium : remembered context across a persistent event
    slow   : transport conductances accumulated across many events
    """

    def __init__(self, world: PokeWorld | None = None, structure: SlowStructure | None = None):
        self.world = world or PokeWorld()
        self.structure = structure or SlowStructure(self.world.n_actions)
        self.poker = ActivePoker(self.world, self.structure)
        self.memory = MediumMemory()

    def step(self, context: int, *, use_memory: bool = True) -> StepResult:
        passive = self.world.passive_group(context)
        surprised = (not use_memory) or self.memory.needs_probe(passive)

        if surprised:
            identification = self.poker.identify(context)
            self.structure.record(identification.actions)
            predicted = identification.predicted
            probes = len(identification.actions)
            cost = identification.cost
            if use_memory and predicted is not None:
                self.memory.write(predicted, passive)
        else:
            predicted = self.memory.remembered_context
            probes = 0
            cost = 0.0

        return StepResult(
            predicted=predicted,
            correct=(predicted == context),
            probes=probes,
            probe_cost=cost,
            surprised=surprised,
        )


def visible_event_sequence(events: int = 64, dwell: int = 8) -> list[int]:
    """Contexts persist; every event boundary flips the cheap passive group."""
    sequence: list[int] = []
    for event in range(events):
        local = (event // 2) % CONTEXTS_PER_GROUP
        context = local if event % 2 == 0 else CONTEXTS_PER_GROUP + local
        sequence.extend([context] * dwell)
    return sequence


def silent_switch_sequence() -> list[int]:
    """A deliberate failure: hidden identity changes without changing HOME group."""
    return [0] * 4 + [1] * 4
