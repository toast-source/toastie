import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import ase_viewer


class PerformanceMonitorTests(unittest.TestCase):
    def test_empty_snapshot_is_safe(self):
        snapshot = ase_viewer.PerformanceMonitor(enabled=True).snapshot()
        self.assertEqual(snapshot["frames"], 0)
        self.assertEqual(snapshot["fps"], 0)
        self.assertEqual(snapshot["frame_p95_ms"], 0)
        self.assertEqual(snapshot["spikes_over_25ms"], 0)

    def test_sections_statistics_spikes_and_counts(self):
        monitor = ase_viewer.PerformanceMonitor(enabled=True, window_size=10)
        for frame_ms in (10, 20, 30, 40):
            monitor.begin_frame()
            monitor.record("update", frame_ms / 4)
            monitor.record("update", frame_ms / 4)
            monitor.record("particle_render", frame_ms / 2)
            monitor.end_frame(None, {"npc": 8}, total_ms=frame_ms)
        snapshot = monitor.snapshot()
        self.assertEqual(snapshot["frame_avg_ms"], 25)
        self.assertEqual(snapshot["frame_median_ms"], 20)
        self.assertEqual(snapshot["frame_p95_ms"], 30)
        self.assertEqual(snapshot["frame_p99_ms"], 30)
        self.assertEqual(snapshot["frame_max_ms"], 40)
        self.assertEqual(snapshot["spikes_over_25ms"], 2)
        self.assertEqual(snapshot["frames_over_16_67ms"], 3)
        self.assertEqual(snapshot["sections"]["update"]["avg_ms"], 12.5)
        self.assertEqual(snapshot["sections"]["particle_render"]["max_ms"], 20)
        self.assertEqual(snapshot["objects"]["npc"], 8)

    def test_ring_buffer_keeps_only_recent_frames(self):
        monitor = ase_viewer.PerformanceMonitor(enabled=True, window_size=3)
        for frame_ms in (1, 2, 3, 4, 5):
            monitor.begin_frame()
            monitor.end_frame(None, total_ms=frame_ms)
        self.assertEqual(list(monitor.frame_times), [3, 4, 5])
        self.assertEqual(monitor.snapshot()["frame_avg_ms"], 4)
        self.assertEqual(monitor.final_summary()["frames"], 5)

    def test_disabled_monitor_does_not_collect(self):
        monitor = ase_viewer.PerformanceMonitor(enabled=False)
        self.assertIsNone(monitor.begin_frame())
        monitor.record("update", 10)
        monitor.end_frame(None, total_ms=10)
        self.assertEqual(monitor.snapshot()["frames"], 0)


if __name__ == "__main__":
    unittest.main()
