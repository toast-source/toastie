import unittest

import ase_viewer


class SettingsSmallUxPolishTests(unittest.TestCase):
    def test_each_tab_has_a_compact_localized_subtitle(self):
        for section in ase_viewer.SETTINGS_SECTIONS:
            model = ase_viewer.settings_section_model(section)
            self.assertTrue(model["subtitle"])
            self.assertTrue(model["subtitle_key"].startswith("settings.subtitle."))

    def test_empty_state_copy_is_actionable_in_both_languages(self):
        self.assertEqual(
            ase_viewer.tr("settings.background.empty", language="ko"),
            "배경 레이어가 없습니다. 리소스에서 배경을 추가하세요.",
        )
        self.assertEqual(
            ase_viewer.tr("settings.background.empty", language="en"),
            "No background layer. Add one from Resources.",
        )
        self.assertIn("배치 탭", ase_viewer.tr("settings.npc.empty", language="ko"))
        self.assertIn("Placement", ase_viewer.tr("settings.npc.empty", language="en"))

    def test_reset_and_delete_terms_are_distinct(self):
        for language in ("ko", "en"):
            self.assertNotEqual(
                ase_viewer.tr("common.reset", language=language),
                ase_viewer.tr("common.remove", language=language),
            )
        self.assertEqual(
            ase_viewer.tr("selection.delete_all_corpses", language="ko"),
            "시체 전체 삭제",
        )

    def test_minimum_supported_row_keeps_controls_inside_sidebar(self):
        rects = ase_viewer.settings_slider_control_rects(300, 20)
        for rect in rects.values():
            self.assertGreaterEqual(rect.left, 0)
            self.assertLessEqual(rect.right, 300)


if __name__ == "__main__":
    unittest.main()
