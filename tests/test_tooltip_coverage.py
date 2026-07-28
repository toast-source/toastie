import os
import unittest
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


class TooltipCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))
        cls.font_s = ase_viewer.create_ui_font(12)
        cls.font_b = ase_viewer.create_ui_font(14, bold=True)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_selection_controls_have_bilingual_tooltips(self):
        for control_id, metadata in ase_viewer.SELECTION_WORKSPACE_CONTROLS.items():
            with self.subTest(control_id=control_id):
                key = metadata.get("tooltip_key")
                self.assertTrue(key)
                self.assertIn(key, ase_viewer.TRANSLATIONS[ase_viewer.LANG_KO])
                self.assertIn(key, ase_viewer.TRANSLATIONS[ase_viewer.LANG_EN])

    def test_disabled_actions_keep_tooltip_keys(self):
        for action in ("use_player", "spawn_npc", "place_prop", "export_png"):
            self.assertIn(f"resource.{action}", ase_viewer.SELECTION_WORKSPACE_CONTROLS)

    def test_only_visible_rows_register_tooltips_and_lists_do_not_accumulate(self):
        sources = [
            SimpleNamespace(
                name=f"Resource_{index}.aseprite", file_path=f"Resource_{index}.aseprite",
                source_revision=1, slice_analysis_revision=None, slice_export_analysis=None,
            )
            for index in range(50)
        ]
        player = SimpleNamespace(
            sources=sources, profiles=[], ai_list=[], prop_list=[],
            cur_profile_idx=0, cur_source_idx=0, language="ko", visible=True,
        )
        surface = pygame.Surface((1280, 720))
        first_regions = []
        result = ase_viewer.draw_selection_workspace(
            surface, player, "resources", 0,
            (self.font_s, self.font_b), first_regions, origin_x=960,
        )
        self.assertLess(result["visible_rows"], 50)
        self.assertLess(len(first_regions), 20)
        second_regions = []
        ase_viewer.draw_selection_workspace(
            surface, player, "resources", 0,
            (self.font_s, self.font_b), second_regions, origin_x=960,
        )
        self.assertEqual(len(first_regions), len(second_regions))


if __name__ == "__main__":
    unittest.main()
