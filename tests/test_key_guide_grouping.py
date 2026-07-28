import unittest
from types import SimpleNamespace

import pygame

import ase_viewer


def guide_player(attack=pygame.K_z):
    return SimpleNamespace(key_map={
        "ATTACK": attack, "DASH": pygame.K_x,
        "JUMP": pygame.K_SPACE, "SWAP": pygame.K_t,
        "SKILL1": pygame.K_c, "SKILL2": pygame.K_b,
        "SKILL3": pygame.K_n,
    })


class KeyGuideGroupingTests(unittest.TestCase):
    def test_character_and_app_groups_are_separate(self):
        groups = ase_viewer.bottom_key_guide_groups(guide_player())
        self.assertEqual([group["id"] for group in groups], ["character", "app"])
        character = groups[0]["items"]
        app = groups[1]["items"]
        self.assertTrue({"Z", "X", "SPACE", "T"}.issubset(
            {key for key, _, _ in character},
        ))
        self.assertIn("C/B/N", {key for key, _, _ in character})
        self.assertIn("F10", {key for key, _, _ in app})
        self.assertFalse(
            {key for key, _, _ in character}
            & {"P", "O", "[ ]", "F5", "F10", "H", "R-Drag", "F"},
        )

    def test_group_titles_are_localized(self):
        for language in ("ko", "en"):
            ase_viewer.set_current_language(language)
            groups = ase_viewer.bottom_key_guide_groups(guide_player())
            self.assertTrue(all(group["title"] for group in groups))
            self.assertNotEqual(groups[0]["title"], "guide.group.character")
            self.assertNotEqual(groups[1]["title"], "guide.group.app")

    def test_key_map_change_affects_character_only(self):
        before = ase_viewer.bottom_key_guide_groups(guide_player())
        after = ase_viewer.bottom_key_guide_groups(guide_player(pygame.K_q))
        self.assertNotEqual(before[0]["items"], after[0]["items"])
        self.assertEqual(before[1]["items"], after[1]["items"])

    def test_layout_preserves_both_groups_in_every_mode(self):
        pygame.font.init()
        try:
            font = pygame.font.Font(None, 16)
            for mode in ase_viewer.SIDEBAR_MODES:
                model = ase_viewer.bottom_key_guide_layout(
                    guide_player(), mode, 650, 720, font,
                )
                self.assertEqual(
                    {group["group"] for group in model["groups"]},
                    {"character", "app"},
                )
                self.assertEqual(
                    {item["group"] for item in model["items"]},
                    {"character", "app"},
                )
        finally:
            pygame.font.quit()


if __name__ == "__main__":
    unittest.main()
