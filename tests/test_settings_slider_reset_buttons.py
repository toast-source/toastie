import unittest
from types import SimpleNamespace

import ase_viewer


class ResetPlayer(SimpleNamespace):
    def __init__(self):
        super().__init__(
            dash_speed=42.0,
            jump_power=-12.0,
            bg_color=[90, 80, 70],
            bg_layers=[{
                "off_x": 24,
                "off_y": 31,
                "zoom": 4.0,
                "alpha": 100,
                "parallax": 3.0,
            }],
            active_bg_layer=0,
            parallax_offset_history=[],
            parallax_offset_redo_stack=[],
            parallax_offset_edit=None,
        )
        self.save_count = 0

    def save_settings(self):
        self.save_count += 1


class SettingsSliderResetButtonTests(unittest.TestCase):
    def test_common_layout_keeps_slider_numeric_and_reset_disjoint(self):
        rects = ase_viewer.settings_slider_control_rects(450, 100)
        self.assertFalse(rects["slider"].colliderect(rects["numeric"]))
        self.assertFalse(rects["slider"].colliderect(rects["reset"]))
        self.assertFalse(rects["numeric"].colliderect(rects["reset"]))
        self.assertEqual(rects["numeric"].right + 8, rects["reset"].left)

    def test_reset_one_persisted_value_uses_verified_default(self):
        player = ResetPlayer()
        result = ase_viewer.reset_slider_setting(player, "dash_speed")
        self.assertTrue(result["changed"])
        self.assertEqual(player.dash_speed, 12.0)
        self.assertEqual(player.jump_power, -12.0)
        self.assertEqual(player.save_count, 1)

    def test_unknown_default_is_safe_noop(self):
        player = ResetPlayer()
        result = ase_viewer.reset_slider_setting(player, "unknown")
        self.assertFalse(result["changed"])
        self.assertIsNone(result["value"])
        self.assertEqual(player.save_count, 0)

    def test_parallax_x_reset_preserves_y_and_supports_undo_redo(self):
        player = ResetPlayer()
        result = ase_viewer.reset_slider_setting(
            player, "off_x", layer_index=0,
        )
        self.assertTrue(result["changed"])
        self.assertEqual(
            ase_viewer.get_parallax_layer_offset(player.bg_layers[0]),
            (0.0, 31.0),
        )
        self.assertEqual(len(player.parallax_offset_history), 1)
        self.assertTrue(ase_viewer.undo_parallax_offset(player))
        self.assertEqual(
            ase_viewer.get_parallax_layer_offset(player.bg_layers[0]),
            (24.0, 31.0),
        )
        self.assertTrue(ase_viewer.redo_parallax_offset(player))
        self.assertEqual(
            ase_viewer.get_parallax_layer_offset(player.bg_layers[0]),
            (0.0, 31.0),
        )

    def test_parallax_y_reset_preserves_x(self):
        player = ResetPlayer()
        ase_viewer.reset_slider_setting(player, "off_y", layer_index=0)
        self.assertEqual(
            ase_viewer.get_parallax_layer_offset(player.bg_layers[0]),
            (24.0, 0.0),
        )

    def test_invalid_active_layer_is_safe(self):
        player = ResetPlayer()
        result = ase_viewer.reset_slider_setting(
            player, "off_x", layer_index=99,
        )
        self.assertFalse(result["changed"])
        self.assertEqual(player.save_count, 0)

    def test_reset_value_immediately_drives_numeric_and_thumb_model(self):
        player = ResetPlayer()
        ase_viewer.reset_slider_setting(player, "dash_speed", persist=False)
        value = ase_viewer.slider_setting_value(player, "dash_speed")
        rect = ase_viewer.settings_slider_control_rects(450, 100)["slider"]
        thumb_x = rect.x + (value - 10) / (50 - 10) * rect.w
        self.assertEqual(value, 12.0)
        self.assertGreaterEqual(thumb_x, rect.left)
        self.assertLessEqual(thumb_x, rect.right)


if __name__ == "__main__":
    unittest.main()
