from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


Signature = tuple[int, ...]


@dataclass(frozen=True)
class NoveltyPrior:
    """Independent-bit prior used only to price open-world false acceptance.

    This is an explicit assumption, not hidden ontology.  If a novel response
    signature is drawn from these bit marginals, matching a rare response is
    stronger evidence for a stored prototype than matching a common response.
    """

    bit_one_probability: tuple[float, ...]

    @property
    def n_actions(self) -> int:
        return len(self.bit_one_probability)

    def probability(self, action: int, response: int) -> float:
        p_one = self.bit_one_probability[action]
        return p_one if response else 1.0 - p_one

    def surprisal(self, action: int, response: int) -> float:
        return -math.log2(self.probability(action, response))


@dataclass(frozen=True)
class PrototypeRecognition:
    identity: Signature
    probes: int
    correct: bool
    accepted_early: bool


class OpenWorldRecognizer:
    """Recognize stored action-response prototypes with a novelty guard.

    `alpha=None` is the deliberately unsafe closed-world attacker: as soon as a
    single stored prototype remains, it accepts it.  With finite `alpha`, early
    acceptance additionally requires enough evidence under the declared novelty
    prior to make the union-bound false-accept budget <= alpha.

    If no stored prototype survives, the recognizer pays for all remaining
    scalar actions and returns the exact response signature.  That full scan is
    how an unlabeled new object first becomes available to memory.
    """

    def __init__(self, prior: NoveltyPrior, *, alpha: float | None = 0.01):
        if alpha is not None and not 0.0 < alpha < 1.0:
            raise ValueError("alpha must be in (0, 1) or None")
        self.prior = prior
        self.alpha = alpha

    def _check_signature(self, signature: Signature) -> None:
        if len(signature) != self.prior.n_actions:
            raise ValueError("signature length must match action count")
        if any(bit not in (0, 1) for bit in signature):
            raise ValueError("signatures must be binary")

    def _choose_action(self, candidates: Sequence[Signature], used: set[int]) -> int:
        """Greedy question: split prototypes while accumulating novelty evidence."""
        best: tuple[float, int] | None = None
        for action in range(self.prior.n_actions):
            if action in used:
                continue
            ones = sum(signature[action] for signature in candidates)
            p_one = ones / len(candidates)
            if p_one in (0.0, 1.0):
                split_information = 0.0
            else:
                split_information = -(
                    p_one * math.log2(p_one)
                    + (1.0 - p_one) * math.log2(1.0 - p_one)
                )
            novelty_evidence = sum(
                self.prior.surprisal(action, signature[action])
                for signature in candidates
            ) / len(candidates)
            score = split_information + 0.30 * novelty_evidence
            candidate = (score, -action)
            if best is None or candidate > best:
                best = candidate
        if best is None:
            raise RuntimeError("no unused action remains")
        return -best[1]

    def recognize(
        self,
        signature: Signature,
        prototypes: Sequence[Signature],
    ) -> PrototypeRecognition:
        self._check_signature(signature)
        for prototype in prototypes:
            self._check_signature(prototype)

        candidates = list(dict.fromkeys(prototypes))
        if not candidates:
            return PrototypeRecognition(signature, self.prior.n_actions, True, False)

        initial_hypotheses = max(1, len(candidates))
        used: set[int] = set()
        evidence_bits = 0.0

        while candidates and len(used) < self.prior.n_actions:
            action = self._choose_action(candidates, used)
            used.add(action)
            observed = signature[action]
            evidence_bits += self.prior.surprisal(action, observed)
            candidates = [
                candidate
                for candidate in candidates
                if candidate[action] == observed
            ]

            if len(candidates) == 1:
                if self.alpha is None:
                    accepted = True
                else:
                    threshold = math.log2(initial_hypotheses / self.alpha)
                    accepted = evidence_bits >= threshold
                if accepted:
                    identity = candidates[0]
                    return PrototypeRecognition(
                        identity=identity,
                        probes=len(used),
                        correct=(identity == signature),
                        accepted_early=True,
                    )

        # Open world: if stored hypotheses fail or never earn enough evidence,
        # complete the response signature instead of guessing from the cache.
        return PrototypeRecognition(
            identity=signature,
            probes=self.prior.n_actions,
            correct=True,
            accepted_early=False,
        )

    def probe_cost(self, signature: Signature, prototypes: Sequence[Signature]) -> int:
        return self.recognize(signature, prototypes).probes
