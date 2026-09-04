import unittest

from alternative_neuron.prototypes import NoveltyPrior, OpenWorldRecognizer
from experiments.gate5_selective_objects import (
    ALPHA,
    K,
    PRIOR,
    ProbeValuePolicy,
    RecognitionTable,
    RECURRING,
)


class Gate5PrototypeTests(unittest.TestCase):
    def test_closed_world_can_false_accept_novel_signature(self):
        cache = list(RECURRING[:3])
        closed = OpenWorldRecognizer(PRIOR, alpha=None)
        found = False
        for integer in range(1 << PRIOR.n_actions):
            signature = tuple((integer >> action) & 1 for action in range(PRIOR.n_actions))
            if signature in cache:
                continue
            result = closed.recognize(signature, cache)
            if not result.correct:
                found = True
                self.assertTrue(result.accepted_early)
                self.assertLess(result.probes, PRIOR.n_actions)
                break
        self.assertTrue(found)

    def test_open_world_guard_can_force_full_scan(self):
        cache = list(RECURRING[:3])
        guarded = OpenWorldRecognizer(PRIOR, alpha=ALPHA)
        # A signature outside the cache that looks initially familiar must not
        # be accepted merely because one cached prototype remains.
        for integer in range(1 << PRIOR.n_actions):
            signature = tuple((integer >> action) & 1 for action in range(PRIOR.n_actions))
            if signature in cache:
                continue
            closed = OpenWorldRecognizer(PRIOR, alpha=None).recognize(signature, cache)
            if not closed.correct:
                result = guarded.recognize(signature, cache)
                if result.correct:
                    self.assertEqual(result.probes, PRIOR.n_actions)
                    return
        self.fail("did not find a novelty case separated by the guard")

    def test_probe_value_policy_is_allowed_to_leave_slots_empty(self):
        table = RecognitionTable(ALPHA)
        policy = ProbeValuePolicy(table, k=K)
        # P5 needs all 12 responses even when stored alone, so recurrence does
        # not automatically earn a durable slot when it saves no sensing cost.
        hard = RECURRING[5]
        for _ in range(8):
            policy.observe(hard)
        self.assertNotIn(hard, policy.cache)
        self.assertLess(len(policy.cache), K)

    def test_novelty_prior_validates_signature_length(self):
        prior = NoveltyPrior((0.25, 0.75))
        recognizer = OpenWorldRecognizer(prior, alpha=0.01)
        with self.assertRaises(ValueError):
            recognizer.recognize((0, 1, 0), [])


if __name__ == "__main__":
    unittest.main()
