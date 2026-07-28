import unittest
from types import SimpleNamespace

import pygame

import ase_viewer


class BottomKeyGuideModesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.font.init()
        cls.font = pygame.font.Font(None, 16)

    @classmethod
    def tearDownClass(cls):
        pygame.font.quit()

    def setUp(self):
        self.player = SimpleNamespace(key_map={
            "ATTACK": pygame.K_z, "DASH": pygame.K_x,
            "JUMP": pygame.K_SPACE, "SWAP": pygame.K_t,
            "SYNERGY": pygame.K_e,
        })

    def test_every_sidebar_mode_has_the_same_common_guide(self):
        expected = None
        for mode in ase_viewer.SIDEBAR_MODES:
            model = ase_viewer.bottom_key_guide_layout(
                self.player, mode, 650, 720, self.font,
            )
            self.assertTrue(model["items"])
            labels = [(item["key"], item["label"]) for item in model["items"]]
            expected = labels if expected is None else expected
            self.assertEqual(labels, expected)
            self.assertIn(("E", ase_viewer.tr("guide.synergy")), labels)

    def test_current_mapping_and_language_are_reflected(self):
        self.player.key_map["ATTACK"] = pygame.K_q
        ase_viewer.set_current_language("ko")
        items = ase_viewer.bottom_key_guide_items(self.player)
        self.assertIn(("Q", "공격", None), items)
        ase_viewer.set_current_language("en")
        items = ase_viewer.bottom_key_guide_items(self.player)
        self.assertIn(("Q", "Attack", None), items)

    def test_minimum_width_wraps_without_leaving_play_area(self):
        model = ase_viewer.bottom_key_guide_layout(
            self.player, ase_viewer.SIDEBAR_SCENE, 300, 720, self.font,
        )
        self.assertGreaterEqual(model["background"].top, 0)
        for item in model["items"]:
            self.assertGreaterEqual(item["rect"].left, 0)
            self.assertLessEqual(item["rect"].right, 300)
            self.assertLessEqual(item["rect"].bottom, 720)

    def test_f10_remains_in_common_guide_for_debug_overlay_discovery(self):
        items = ase_viewer.bottom_key_guide_items(self.player)
        self.assertTrue(any(key == "F10" for key, _, _ in items))


if __name__ == "__main__":
    unittest.main()
