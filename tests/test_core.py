import math
import unittest

from alternative_neuron import ActivePoker, AlternativeNeuron, PokeWorld, SlowStructure
from run_gates import gate0, gate1, gate2, gate3


class AlternativeNeuronTests(unittest.TestCase):
    def test_state_dependent_poke_is_the_necessary_part(self):
        world = PokeWorld()
        result = gate0(world)
        self.assertTrue(result["pass"])
        self.assertEqual(result["active_poke_accuracy"], 1.0)
        self.assertLessEqual(result["state_independent_poke_accuracy"], 0.125)

    def test_exact_three_poke_identification_under_uniform_structure(self):
        world = PokeWorld()
        poker = ActivePoker(world, SlowStructure(world.n_actions))
        for context in range(16):
            result = poker.identify(context)
            self.assertEqual(result.predicted, context)
            self.assertEqual(len(result.actions), 3)
            self.assertAlmostEqual(result.cost, 3.0)

    def test_memory_saves_only_when_cheap_surprise_sees_the_change(self):
        result = gate1()
        self.assertTrue(result["pass"])
        self.assertAlmostEqual(result["probe_reduction_x"], 8.0)
        # Deliberate boundary: context 0 -> 1 stays in the same passive group,
        # so the cheap HOME channel never requests a new poke.
        self.assertAlmostEqual(result["silent_same_group_switch"]["accuracy"], 0.5)

    def test_slow_structure_keeps_budget_and_beats_shuffled_traffic(self):
        world = PokeWorld()
        result, adapted, shuffled = gate2(world)
        self.assertTrue(result["pass"])
        self.assertAlmostEqual(sum(adapted.conductance), adapted.budget, places=12)
        self.assertLess(result["adapted_mean_cost"], result["frozen_mean_cost"])
        self.assertGreater(result["shuffled_traffic_mean_cost"], result["frozen_mean_cost"])

    def test_three_timescales_compose(self):
        world = PokeWorld()
        _, adapted, shuffled = gate2(world)
        result = gate3(world, adapted, shuffled)
        self.assertTrue(result["pass"])
        self.assertEqual(result["active_memory_adapted"]["accuracy"], 1.0)
        self.assertLess(
            result["active_memory_adapted"]["probe_cost"],
            result["active_memory_frozen"]["probe_cost"],
        )


if __name__ == "__main__":
    unittest.main()
