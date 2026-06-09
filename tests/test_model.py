import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import numpy as np

from exponential_random_orchestra.audio import find_soundfont, render_midi_to_mp3
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


class AudioTests(unittest.TestCase):
    def test_explicit_soundfont_must_exist(self):
        with self.assertRaises(FileNotFoundError):
            find_soundfont("/does/not/exist.sf2")

    def test_renderer_uses_fluidsynth_then_ffmpeg(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            midi_path = root / "input.mid"
            soundfont_path = root / "orchestra.sf2"
            mp3_path = root / "output" / "clip.mp3"
            midi_path.touch()
            soundfont_path.touch()

            with (
                patch(
                    "exponential_random_orchestra.audio.shutil.which",
                    side_effect=lambda command: f"/usr/bin/{command}",
                ),
                patch("exponential_random_orchestra.audio.subprocess.run") as run,
            ):
                render_midi_to_mp3(midi_path, mp3_path, soundfont_path)

            self.assertEqual(run.call_count, 2)
            fluidsynth_command = run.call_args_list[0].args[0]
            ffmpeg_command = run.call_args_list[1].args[0]
            self.assertEqual(fluidsynth_command[0], "/usr/bin/fluidsynth")
            self.assertIn(str(soundfont_path), fluidsynth_command)
            self.assertEqual(ffmpeg_command[0], "/usr/bin/ffmpeg")
            self.assertEqual(ffmpeg_command[-1], str(mp3_path))


if __name__ == "__main__":
    unittest.main()
