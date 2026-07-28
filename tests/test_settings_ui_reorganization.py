import unittest
import inspect

import ase_viewer


class SettingsUiReorganizationTests(unittest.TestCase):
    def test_every_legacy_category_remains_reachable_once(self):
        categories = [
            category
            for section in ase_viewer.SETTINGS_SECTIONS
            for category in ase_viewer.settings_section_model(section)["categories"]
        ]
        self.assertCountEqual(categories, ase_viewer.CATEGORY_TRANSLATION_KEYS)
        self.assertEqual(len(categories), len(set(categories)))

    def test_content_height_is_scoped_to_current_section(self):
        player = type("Player", (), {
            "sources": [], "profiles": [], "bg_layers": [],
            "active_bg_layer": -1, "key_map": {},
        })()
        folds = {
            category: True
            for category in ase_viewer.CATEGORY_TRANSLATION_KEYS
        }
        full_height = ase_viewer.settings_content_height(player, folds)
        for section in ase_viewer.SETTINGS_SECTIONS:
            self.assertLess(
                ase_viewer.settings_content_height(player, folds, section),
                full_height,
            )

    def test_navigation_is_session_model_not_settings_schema(self):
        save_source = inspect.getsource(ase_viewer.AsepritePlayer.save_settings)
        self.assertNotIn('"settings_section"', save_source)
        project_source = inspect.getsource(ase_viewer.AsepritePlayer.save_project)
        self.assertIn('"schema_version": 2', project_source)


if __name__ == "__main__":
    unittest.main()
