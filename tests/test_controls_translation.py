import unittest

import pygame

import ase_viewer


class ControlsTranslationTests(unittest.TestCase):
    def tearDown(self):
        ase_viewer.set_current_language("ko")

    def test_korean_character_action_labels_are_localized(self):
        expected = {
            "ATTACK": "공격", "DASH": "대시", "JUMP": "점프",
            "SWAP": "교대", "SKILL1": "스킬 1", "SKILL2": "스킬 2",
            "SKILL3": "스킬 3", "SYNERGY": "합격기",
        }
        for action, label in expected.items():
            self.assertEqual(
                ase_viewer.control_action_label(action, "ko"), label,
            )
            self.assertNotEqual(label, action.title())

    def test_english_character_action_labels_are_natural(self):
        expected = {
            "ATTACK": "Attack", "DASH": "Dash", "JUMP": "Jump",
            "SWAP": "Swap", "SKILL1": "Skill 1", "SKILL2": "Skill 2",
            "SKILL3": "Skill 3", "SYNERGY": "Synergy",
        }
        for action, label in expected.items():
            self.assertEqual(
                ase_viewer.control_action_label(action, "en"), label,
            )

    def test_key_names_and_internal_mapping_keys_are_unchanged(self):
        key_map = {"ATTACK": pygame.K_z, "SYNERGY": pygame.K_e}
        player = type("Player", (), {"key_map": key_map})()
        ase_viewer.set_current_language("ko")
        items = ase_viewer.character_key_guide_items(player)
        self.assertIn(("Z", "공격", None), items)
        self.assertIn(("E", "합격기", None), items)
        self.assertEqual(set(player.key_map), {"ATTACK", "SYNERGY"})

    def test_korean_app_shortcuts_are_localized(self):
        ase_viewer.set_current_language("ko")
        labels = {
            key: label
            for key, label, _ in ase_viewer.app_shortcut_guide_items()
        }
        self.assertEqual(labels["P"], "일시정지")
        self.assertEqual(labels["O"], "1프레임 진행")
        self.assertIn("속도 조절", labels["[ ]"])
        self.assertEqual(labels["F5"], "새로고침")
        self.assertEqual(labels["F10"], "성능 표시")
        self.assertEqual(labels["H"], "히트박스")
        self.assertEqual(labels["R-Drag"], "카메라 이동")
        self.assertEqual(labels["F"], "카메라 복귀")


if __name__ == "__main__":
    unittest.main()
