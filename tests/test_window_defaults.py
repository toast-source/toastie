import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import ase_viewer


class WindowDefaultTests(unittest.TestCase):
    def test_large_desktop_contains_zoomed_guide_and_sidebar(self):
        width, height = ase_viewer.calculate_initial_window_size((3840, 2160))
        self.assertGreaterEqual(
            width,
            ase_viewer.SIDEBAR_WIDTH + 640 * 3 + ase_viewer.WINDOW_MARGIN[0],
        )
        self.assertGreaterEqual(
            height,
            ase_viewer.TOP_UI_HEIGHT + 360 * 3 + ase_viewer.WINDOW_MARGIN[1],
        )

    def test_small_desktop_is_limited_to_ninety_percent(self):
        width, height = ase_viewer.calculate_initial_window_size((1280, 720))
        self.assertLessEqual(width, int(1280 * 0.9))
        self.assertLessEqual(height, int(720 * 0.9))

    def test_saved_size_wins_but_is_safely_clamped(self):
        self.assertEqual(
            ase_viewer.calculate_initial_window_size((2560, 1440), saved_size=(1600, 900)),
            (1600, 900),
        )
        self.assertEqual(
            ase_viewer.calculate_initial_window_size((1280, 720), saved_size=(2000, 1200)),
            (1152, 648),
        )

    def test_version_is_shared_by_title_and_check_source(self):
        self.assertEqual(ase_viewer.APP_VERSION, "v0.5.8.3")
        self.assertIn(ase_viewer.APP_VERSION, ase_viewer.app_window_title())
        self.assertIn(ase_viewer.APP_VERSION, ase_viewer.application_check_success_message(9))

    def test_packaged_check_message_marks_external_examples_and_tcl(self):
        message = ase_viewer.application_check_success_message(
            0, expected_example_count=9, tk_patchlevel="8.6.12",
        )
        self.assertIn("example_resources=0/9", message)
        self.assertIn("external_example_resources_required=true", message)
        self.assertIn("tkinter_tcl=8.6.12", message)


if __name__ == "__main__":
    unittest.main()
