import unittest

import pygame

import ase_viewer


class SettingsSectionNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.font.init()
        cls.font = pygame.font.Font(None, 16)

    @classmethod
    def tearDownClass(cls):
        pygame.font.quit()

    def tearDown(self):
        ase_viewer.set_current_language(ase_viewer.LANG_KO)

    def test_three_disjoint_buttons_have_exact_click_targets(self):
        rects = ase_viewer.settings_section_button_rects(450)
        self.assertEqual(list(rects), list(ase_viewer.SETTINGS_SECTIONS))
        self.assertEqual(len(rects), 3)
        values = list(rects.values())
        for index, (section, rect) in enumerate(rects.items()):
            self.assertEqual(
                ase_viewer.settings_section_click_target(rect.center, 450),
                section,
            )
            for other in values[index + 1:]:
                self.assertFalse(rect.colliderect(other))

    def test_invalid_and_old_sections_migrate_to_three_tabs(self):
        self.assertEqual(
            ase_viewer.normalize_settings_section("missing"),
            ase_viewer.SETTINGS_SECTION_CONTROLS_APP,
        )
        self.assertEqual(
            ase_viewer.settings_section_model("missing")["id"],
            ase_viewer.SETTINGS_SECTION_CONTROLS_APP,
        )
        expected = {
            "quick": ase_viewer.SETTINGS_SECTION_CONTROLS_APP,
            "input": ase_viewer.SETTINGS_SECTION_CONTROLS_APP,
            "ai_combat": ase_viewer.SETTINGS_SECTION_SCENE_COMBAT,
            "background": ase_viewer.SETTINGS_SECTION_VIEW_BACKGROUND,
            "view_debug": ase_viewer.SETTINGS_SECTION_VIEW_BACKGROUND,
            "advanced": ase_viewer.SETTINGS_SECTION_SCENE_COMBAT,
        }
        self.assertEqual(
            {
                old: ase_viewer.normalize_settings_section(old)
                for old in expected
            },
            expected,
        )

    def test_korean_and_english_labels_fit_minimum_tabs(self):
        rects = ase_viewer.settings_section_button_rects(450)
        for language in (ase_viewer.LANG_KO, ase_viewer.LANG_EN):
            ase_viewer.set_current_language(language)
            for section, rect in rects.items():
                label = ase_viewer.settings_section_model(section)["label"]
                self.assertLessEqual(self.font.size(label)[0], rect.w - 8)

    def test_every_section_clips_controls_and_tooltips_inside_options(self):
        width, height = 1100, 720
        play_width = width - ase_viewer.SIDEBAR_WIDTH
        _header, content = ase_viewer.sidebar_rects(play_width, height)
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        for section in ase_viewer.SETTINGS_SECTIONS:
            for scroll in (0, -500):
                regions = []
                controls = ase_viewer._draw_sidebar_check_settings(
                    surface, content, scroll, self.font, regions, section,
                )
                self.assertTrue(controls)
                self.assertTrue(all(content.contains(rect) for rect in controls))
                self.assertTrue(
                    all(content.contains(rect) for rect, _key in regions),
                )


if __name__ == "__main__":
    unittest.main()
