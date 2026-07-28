import os
import tempfile
import unittest

import pygame

import ase_viewer


class FastActionInputPreparationTests(unittest.TestCase):
    def test_existing_default_mapping_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            player = ase_viewer.AsepritePlayer(
                project_path=os.path.join(temp_dir, "project.json"),
                settings_path=os.path.join(temp_dir, "settings.json"),
            )
        self.assertEqual(player.key_map["ATTACK"], pygame.K_z)
        self.assertEqual(player.key_map["DASH"], pygame.K_x)
        self.assertEqual(player.key_map["JUMP"], pygame.K_SPACE)
        self.assertEqual(player.key_map["SWAP"], pygame.K_t)

    def test_ui_translations_do_not_name_a_commercial_game(self):
        ui_text = " ".join(
            str(value)
            for language in ase_viewer.TRANSLATIONS.values()
            for value in language.values()
        ).casefold()
        self.assertNotIn("skul", ui_text)

    def test_character_remap_does_not_change_app_shortcuts(self):
        before = ase_viewer.app_shortcut_guide_items()
        player = type("Player", (), {"key_map": {
            "ATTACK": pygame.K_q, "DASH": pygame.K_w,
        }})()
        character = ase_viewer.character_key_guide_items(player)
        self.assertIn(("Q", ase_viewer.tr("guide.attack"), None), character)
        self.assertEqual(ase_viewer.app_shortcut_guide_items(), before)


if __name__ == "__main__":
    unittest.main()
