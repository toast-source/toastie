import unittest
from types import SimpleNamespace

import pygame

import ase_viewer


class SettingsInputControlsSectionTests(unittest.TestCase):
    def test_input_section_owns_controls_and_required_guidance(self):
        model = ase_viewer.settings_section_model(
            ase_viewer.SETTINGS_SECTION_CONTROLS_APP,
        )
        self.assertEqual(model["categories"], ("LANGUAGE", "CONTROLS"))
        for feature in (
            "language", "character_controls", "app_shortcuts", "synergy",
            "fast_action_scope", "controller_todo",
        ):
            self.assertIn(feature, model["features"])

    def test_reading_section_does_not_modify_user_key_map(self):
        player = SimpleNamespace(key_map={
            "ATTACK": pygame.K_q, "SYNERGY": pygame.K_r,
        })
        before = dict(player.key_map)
        ase_viewer.settings_section_model(
            ase_viewer.SETTINGS_SECTION_CONTROLS_APP,
        )
        self.assertEqual(player.key_map, before)

    def test_fast_action_and_controller_copy_are_explicit_todos(self):
        for language in (ase_viewer.LANG_KO, ase_viewer.LANG_EN):
            fast = ase_viewer.tr("settings.input.fast_action", language=language)
            controller = ase_viewer.tr(
                "settings.input.controller_todo", language=language,
            )
            self.assertIn("character" if language == "en" else "캐릭터", fast.lower())
            self.assertTrue(controller)


if __name__ == "__main__":
    unittest.main()
