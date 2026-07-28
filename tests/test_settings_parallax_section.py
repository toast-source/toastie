import unittest
from types import SimpleNamespace

import ase_viewer


class SettingsParallaxSectionTests(unittest.TestCase):
    def test_background_section_owns_parallax_and_history_guidance(self):
        model = ase_viewer.settings_section_model(
            ase_viewer.SETTINGS_SECTION_VIEW_BACKGROUND,
        )
        self.assertEqual(
            model["categories"],
            ("BG IMAGE", "BG COLOR", "CAMERA"),
        )
        for feature in (
            "background_layers", "parallax", "offsets", "gizmo",
            "axis_lock", "undo_redo",
        ):
            self.assertIn(feature, model["features"])

    def test_empty_and_invalid_active_layer_have_safe_height(self):
        player = SimpleNamespace(
            sources=[], profiles=[], bg_layers=[],
            active_bg_layer=-1, key_map={},
        )
        folds = {
            category: True
            for category in ase_viewer.CATEGORY_TRANSLATION_KEYS
        }
        height = ase_viewer.settings_content_height(
            player, folds, ase_viewer.SETTINGS_SECTION_VIEW_BACKGROUND,
        )
        self.assertGreater(height, 0)
        player.bg_layers = [{}]
        player.active_bg_layer = "invalid"
        self.assertEqual(ase_viewer.valid_background_layer_index(player), -1)
        self.assertGreater(
            ase_viewer.settings_content_height(
                player, folds, ase_viewer.SETTINGS_SECTION_VIEW_BACKGROUND,
            ),
            0,
        )


if __name__ == "__main__":
    unittest.main()
