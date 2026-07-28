import os
import unittest
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import ase_viewer


class RuntimeBenchmarkTests(unittest.TestCase):
    def test_benchmark_is_deterministic_in_shape_and_does_not_save(self):
        result = ase_viewer.run_performance_benchmark(
            warmup_frames=2,
            measured_frames=5,
            seed=1234,
        )
        self.assertEqual(result["seed"], 1234)
        self.assertEqual(result["measured_frames"], 5)
        self.assertEqual(result["actors"], 13)
        self.assertEqual(result["image_particles"], 100)
        self.assertEqual(result["color_particles"], 100)
        self.assertEqual(result["background_layers"], 6)
        self.assertFalse(result["project_saved"])
        self.assertFalse(result["settings_saved"])

    def test_benchmark_result_contains_timing_fields_and_sections(self):
        result = ase_viewer.run_performance_benchmark(
            warmup_frames=1,
            measured_frames=3,
            seed=99,
        )
        for field in (
            "frame_avg_ms",
            "frame_p95_ms",
            "frame_p99_ms",
            "frame_max_ms",
            "spikes_over_25ms",
        ):
            self.assertIn(field, result)
            self.assertGreaterEqual(result[field], 0)
        for section in (
            "update",
            "background_render",
            "actor_render",
            "particle_render",
            "world_render",
        ):
            self.assertIn(section, result["sections"])

    def test_closed_export_dialog_does_not_build_filename_plan(self):
        with mock.patch.object(
            ase_viewer, "build_slice_export_plan",
            side_effect=AssertionError("filename plans are modal-only"),
        ):
            result = ase_viewer.run_performance_benchmark(
                warmup_frames=1,
                measured_frames=2,
                seed=7,
            )
        self.assertEqual(result["measured_frames"], 2)


if __name__ == "__main__":
    unittest.main()
