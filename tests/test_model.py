import unittest

import numpy as np

from exponential_random_orchestra.generator import generate_sequence, sample_softmax
from exponential_random_orchestra.harmony import harmonic_weight, interval_class, memory_score
from exponential_random_orchestra.instruments import INSTRUMENTS, build_interaction_matrix
from exponential_random_orchestra.metrics import average_consonance, pitch_class_entropy
from exponential_random_orchestra.presets import HARMONIC_SOCIAL_TUNING, RAW_RANDOM


class HarmonyTests(unittest.TestCase):
    def test_interval_class_is_octave_invariant(self):
        self.assertEqual(interval_class(60, 67), 5)
        self.assertEqual(interval_class(60, 79), 5)

    def test_large_gaps_receive_a_penalty(self):
        self.assertGreater(harmonic_weight(60, 67), harmonic_weight(60, 79))

    def test_memory_prefers_nearby_notes(self):
        self.assertGreater(memory_score(61, 60), memory_score(72, 60))


class ModelTests(unittest.TestCase):
    def test_oboe_has_extra_influence(self):
        matrix = build_interaction_matrix(INSTRUMENTS)
        violin = 0
        clarinet = 6
        oboe = 7
        self.assertGreater(matrix[violin, oboe], matrix[violin, clarinet])

    def test_softmax_returns_a_candidate(self):
        rng = np.random.default_rng(1)
        self.assertIn(sample_softmax([60, 61], [0.0, 1.0], 1.0, rng), [60, 61])

    def test_generation_is_reproducible(self):
        first, history_a = generate_sequence(
            INSTRUMENTS, HARMONIC_SOCIAL_TUNING, total_time=1.0, seed=4
        )
        second, history_b = generate_sequence(
            INSTRUMENTS, HARMONIC_SOCIAL_TUNING, total_time=1.0, seed=4
        )
        self.assertEqual(first, second)
        self.assertEqual(history_a, history_b)

    def test_state_history_includes_sustained_notes(self):
        _, history = generate_sequence(
            INSTRUMENTS, HARMONIC_SOCIAL_TUNING, total_time=2.0, seed=4
        )
        self.assertTrue(any(
            history[step][instrument_id] is not None
            and history[step + 1][instrument_id] is not None
            for step in range(len(history) - 1)
            for instrument_id in range(len(INSTRUMENTS))
        ))

    def test_raw_random_uses_global_range(self):
        events, _ = generate_sequence(INSTRUMENTS, RAW_RANDOM, total_time=5.0, seed=2)
        self.assertTrue(all(36 <= event["pitch"] <= 96 for event in events))
        self.assertTrue(any(
            event["pitch"] < INSTRUMENTS[event["instrument_id"]]["pitch_min"]
            or event["pitch"] > INSTRUMENTS[event["instrument_id"]]["pitch_max"]
            for event in events
        ))

    def test_metrics(self):
        self.assertAlmostEqual(pitch_class_entropy([60, 72]), 0.0)
        self.assertGreater(average_consonance([60, 67]), 0.0)


if __name__ == "__main__":
    unittest.main()
