import inspect
import unittest
from types import SimpleNamespace

import pygame

import ase_viewer


class DashCountDisplayCleanupTests(unittest.TestCase):
    def test_normal_play_has_one_dash_remaining_renderer(self):
        self.assertEqual(len(ase_viewer.dash_charge_hud_rects(100)), 2)
        draw_source = inspect.getsource(ase_viewer.AsepritePlayer.draw)
        main_source = inspect.getsource(ase_viewer.main)
        self.assertIn("dash_charge_hud_rects", draw_source)
        self.assertNotIn("dash_charge_hud_rects", main_source)
        self.assertNotIn("player.dash_charges else", main_source)

    def test_character_guide_keeps_dash_key_without_remaining_count(self):
        player = SimpleNamespace(key_map={"DASH": pygame.K_x})
        items = ase_viewer.character_key_guide_items(player)
        self.assertEqual(items, [("X", ase_viewer.tr("guide.dash"), None)])
        self.assertNotIn("dash_charges", inspect.getsource(
            ase_viewer.character_key_guide_items,
        ))

    def test_f10_overlay_does_not_add_a_second_dash_counter(self):
        overlay_source = inspect.getsource(
            ase_viewer.PerformanceMonitor.overlay_surfaces,
        )
        self.assertNotIn("dash_charges", overlay_source)


if __name__ == "__main__":
    unittest.main()
