import inspect
import unittest

import ase_viewer


class SettingsTabConsolidationTests(unittest.TestCase):
    def test_exactly_three_predictable_tabs_are_exposed(self):
        self.assertEqual(
            list(ase_viewer.SETTINGS_SECTIONS),
            [
                ase_viewer.SETTINGS_SECTION_CONTROLS_APP,
                ase_viewer.SETTINGS_SECTION_SCENE_COMBAT,
                ase_viewer.SETTINGS_SECTION_VIEW_BACKGROUND,
            ],
        )
        self.assertEqual(
            [
                ase_viewer.tr(
                    ase_viewer.SETTINGS_SECTIONS[section]["label"],
                    language="ko",
                )
                for section in ase_viewer.SETTINGS_SECTIONS
            ],
            ["조작·앱", "장면·전투", "화면·배경"],
        )
        self.assertEqual(
            [
                ase_viewer.tr(
                    ase_viewer.SETTINGS_SECTIONS[section]["label"],
                    language="en",
                )
                for section in ase_viewer.SETTINGS_SECTIONS
            ],
            ["Controls & App", "Scene & Combat", "View & Background"],
        )

    def test_every_legacy_category_is_assigned_once(self):
        assigned = [
            category
            for section in ase_viewer.SETTINGS_SECTIONS
            for category in ase_viewer.SETTINGS_SECTIONS[section]["categories"]
        ]
        self.assertCountEqual(assigned, ase_viewer.CATEGORY_TRANSLATION_KEYS)
        self.assertEqual(len(assigned), len(set(assigned)))

    def test_section_state_remains_session_only_and_schema_two(self):
        settings_source = inspect.getsource(
            ase_viewer.AsepritePlayer.save_settings,
        )
        project_source = inspect.getsource(
            ase_viewer.AsepritePlayer.save_project,
        )
        self.assertNotIn('"settings_section"', settings_source)
        self.assertIn('"schema_version": 2', project_source)

    def test_three_buttons_use_one_compact_row(self):
        rects = list(ase_viewer.settings_section_button_rects(450).values())
        self.assertEqual(len({rect.y for rect in rects}), 1)
        self.assertLess(
            ase_viewer.SETTINGS_SECTION_NAV_HEIGHT,
            76,
        )
        self.assertTrue(all(
            first.right <= second.left
            for first, second in zip(rects, rects[1:])
        ))

    def test_tab_transition_resets_scroll_and_stale_inputs(self):
        transition = ase_viewer.settings_section_transition("background")
        self.assertEqual(
            transition["section"],
            ase_viewer.SETTINGS_SECTION_VIEW_BACKGROUND,
        )
        self.assertEqual(transition["scroll"], 0)
        self.assertIsNone(transition["binding_key"])
        self.assertIsNone(transition["active_input_attr"])


if __name__ == "__main__":
    unittest.main()
