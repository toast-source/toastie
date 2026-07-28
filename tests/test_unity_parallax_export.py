import math
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


def layer(name, parallax=0.25, off_x=100, off_y=100, zoom=3.0, enabled=True):
    return {
        "name": name,
        "path": rf"C:\Art\{name}.png",
        "parallax": parallax,
        "off_x": off_x,
        "off_y": off_y,
        "zoom": zoom,
        "alpha": 255,
        "loop_x": False,
        "enabled": enabled,
    }


class UnityParallaxExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_ppu_offsets_scale_and_negative_zero(self):
        converted = ase_viewer.convert_layer_to_unity_parallax(layer("Sky"), 100, 0)
        self.assertEqual(converted["unity_offset_x"], 1.0)
        self.assertEqual(converted["unity_offset_y"], -1.0)
        self.assertEqual(converted["unity_scale_x"], 1.5)
        zero = ase_viewer.convert_layer_to_unity_parallax(
            layer("Zero", off_x=-0.0, off_y=0.0, zoom=0.0), 100, 0,
        )
        self.assertEqual(math.copysign(1, zero["unity_offset_x"]), 1)
        self.assertEqual(ase_viewer._format_export_number(-0.0), "0")

    def test_parallax_maps_to_unity_camera_follow_ratio(self):
        expected = [(0.0, 1.0), (0.25, 0.75), (1.0, 0.0), (-0.5, 1.5)]
        for viewer_value, unity_follow in expected:
            with self.subTest(viewer_value=viewer_value):
                converted = ase_viewer.convert_layer_to_unity_parallax(
                    layer("P", parallax=viewer_value), 100, 0,
                )
                self.assertEqual(converted["viewer_parallax_x"], viewer_value)
                self.assertEqual(converted["unity_camera_follow_x"], unity_follow)
                self.assertEqual(converted["unity_camera_follow_y"], unity_follow)

    def test_viewer_and_unity_screen_positions_are_equivalent(self):
        source = layer("Equivalent", parallax=0.25, off_x=20, off_y=-10, zoom=2)
        converted = ase_viewer.convert_layer_to_unity_parallax(source, 100, 0)
        viewer_x, viewer_y = ase_viewer.viewer_layer_center_offset(source, 100, 40)
        unity_x, unity_y = ase_viewer.unity_layer_screen_offset(converted, 1.0, -0.4)
        self.assertAlmostEqual(unity_x, viewer_x / 100)
        self.assertAlmostEqual(unity_y, -viewer_y / 100)

    def test_render_order_and_disabled_filter(self):
        layers = [layer("Sky"), layer("Hidden", enabled=False), layer("Front")]
        detailed = ase_viewer.build_unity_parallax_export(layers, 100, language="en")
        self.assertLess(detailed.index("[Layer 01]"), detailed.index("[Layer 02]"))
        self.assertLess(detailed.index("[Layer 02]"), detailed.index("[Layer 03]"))
        self.assertIn("Suggested Sorting Order: 0", detailed)
        self.assertIn("Suggested Sorting Order: 2", detailed)
        active_only = ase_viewer.build_unity_parallax_export(
            layers, 100, include_disabled=False, language="en",
        )
        self.assertNotIn("Hidden", active_only)
        self.assertIn("Front", active_only)
        alpha_disabled = layer("Alpha Zero")
        alpha_disabled.pop("enabled")
        alpha_disabled["alpha"] = 0
        self.assertFalse(
            ase_viewer.convert_layer_to_unity_parallax(alpha_disabled, 100, 0)["enabled"],
        )

    def test_detailed_languages_preserve_names_paths_and_numbers(self):
        layers = [layer("한글 Sky", parallax=0.25, off_x=120, off_y=-40)]
        korean = ase_viewer.build_unity_parallax_export(layers, 100, language="ko")
        english = ase_viewer.build_unity_parallax_export(layers, 100, language="en")
        for text in (korean, english):
            self.assertIn("한글 Sky", text)
            self.assertIn(r"C:\Art\한글 Sky.png", text)
            self.assertIn("Parallax X: 0.25", text)
            self.assertIn("Position Offset X: 1.2 units", text)
            self.assertIn("Position Offset Y: 0.4 units", text)
            self.assertIn("Camera Follow Ratio X: 0.75", text)
        self.assertIn("좌표 기준", korean)
        self.assertIn("Coordinate Basis", english)

    def test_compact_maps_to_slack_and_preserves_orders(self):
        compact = ase_viewer.build_unity_parallax_export(
            [layer("Sky"), layer("Cloud")], 100, output_format="compact", language="en",
        )
        slack = ase_viewer.build_unity_parallax_export(
            [layer("Sky"), layer("Cloud")], 100, output_format="slack", language="en",
        )
        self.assertEqual(compact, slack)
        self.assertIn("Offset: Unity units", slack)
        self.assertIn("LAYER", slack)
        self.assertIn("Sky", slack)
        self.assertIn("Cloud", slack)
        self.assertLess(slack.index("Sky"), slack.index("Cloud"))

    def test_invalid_ppu_empty_layers_and_bad_layer_data_are_safe(self):
        for invalid in (0, -1, "bad", float("inf"), float("nan"), 10001):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    ase_viewer.validate_unity_pixels_per_unit(invalid)
        empty = ase_viewer.build_unity_parallax_export([], 100, language="en")
        self.assertIn("There are no background layers", empty)
        converted = ase_viewer.convert_layer_to_unity_parallax(
            {"parallax": "bad", "zoom": None, "off_x": float("nan")}, 100, 0,
        )
        self.assertEqual(converted["viewer_parallax_x"], 1.0)
        self.assertEqual(converted["unity_scale_x"], 1.0)


if __name__ == "__main__":
    unittest.main()
