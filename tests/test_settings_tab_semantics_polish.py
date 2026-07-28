import unittest

import ase_viewer


class SettingsTabSemanticsPolishTests(unittest.TestCase):
    def test_scene_combat_owns_layers_and_vfx(self):
        scene = ase_viewer.settings_section_model(
            ase_viewer.SETTINGS_SECTION_SCENE_COMBAT,
        )["categories"]
        view = ase_viewer.settings_section_model(
            ase_viewer.SETTINGS_SECTION_VIEW_BACKGROUND,
        )["categories"]
        self.assertIn("LAYERS", scene)
        self.assertIn("JUICE & VFX", scene)
        self.assertNotIn("LAYERS", view)
        self.assertNotIn("JUICE & VFX", view)

    def test_other_semantic_categories_remain_in_place(self):
        controls = ase_viewer.settings_section_model(
            ase_viewer.SETTINGS_SECTION_CONTROLS_APP,
        )["categories"]
        scene = ase_viewer.settings_section_model(
            ase_viewer.SETTINGS_SECTION_SCENE_COMBAT,
        )["categories"]
        view = ase_viewer.settings_section_model(
            ase_viewer.SETTINGS_SECTION_VIEW_BACKGROUND,
        )["categories"]
        self.assertEqual(controls, ("LANGUAGE", "CONTROLS"))
        self.assertTrue({"NPCS", "AI & COMBAT", "PROPS", "PHYSICS"} <= set(scene))
        self.assertEqual(view, ("BG IMAGE", "BG COLOR", "CAMERA"))

    def test_coverage_is_exact_and_tabs_remain_three(self):
        assigned = [
            category
            for section in ase_viewer.SETTINGS_SECTIONS.values()
            for category in section["categories"]
        ]
        self.assertEqual(len(ase_viewer.SETTINGS_SECTIONS), 3)
        self.assertCountEqual(assigned, ase_viewer.CATEGORY_TRANSLATION_KEYS)
        self.assertEqual(len(assigned), len(set(assigned)))
        labels = {
            ase_viewer.tr(data["label"], language="en")
            for data in ase_viewer.SETTINGS_SECTIONS.values()
        }
        self.assertNotIn("Quick", labels)
        self.assertNotIn("Advanced", labels)


if __name__ == "__main__":
    unittest.main()
