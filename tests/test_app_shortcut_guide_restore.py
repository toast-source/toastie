import unittest
from types import SimpleNamespace

import pygame

import ase_viewer


class AppShortcutGuideRestoreTests(unittest.TestCase):
    def test_previously_displayed_app_shortcuts_are_restored(self):
        keys = [key for key, _, _ in ase_viewer.app_shortcut_guide_items()]
        self.assertEqual(
            keys,
            ["P", "O", "[ ]", "F5", "F10", "H", "R-Drag", "F"],
        )

    def test_f10_retains_performance_help_tooltip(self):
        f10 = next(
            item for item in ase_viewer.app_shortcut_guide_items()
            if item[0] == "F10"
        )
        self.assertEqual(f10[2], "performance.help")

    def test_app_shortcuts_exist_with_empty_character_key_map(self):
        groups = ase_viewer.bottom_key_guide_groups(
            SimpleNamespace(key_map={}),
        )
        character = next(group for group in groups if group["id"] == "character")
        app = next(group for group in groups if group["id"] == "app")
        self.assertEqual(character["items"], [])
        self.assertTrue(app["items"])

    def test_restored_shortcuts_match_live_input_constants(self):
        source_names = {
            pygame.K_p: "P", pygame.K_o: "O",
            pygame.K_F5: "F5", pygame.K_F10: "F10",
            pygame.K_h: "H", pygame.K_f: "F",
        }
        guide_keys = {
            key for key, _, _ in ase_viewer.app_shortcut_guide_items()
        }
        self.assertTrue(set(source_names.values()).issubset(guide_keys))


if __name__ == "__main__":
    unittest.main()
