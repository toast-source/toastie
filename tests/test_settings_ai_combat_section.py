import unittest

import ase_viewer


class SettingsAiCombatSectionTests(unittest.TestCase):
    def test_ai_section_contains_existing_npc_and_combat_categories(self):
        model = ase_viewer.settings_section_model(
            ase_viewer.SETTINGS_SECTION_SCENE_COMBAT,
        )
        self.assertEqual(
            model["categories"],
            (
                "NPCS", "AI & COMBAT", "JUICE & VFX", "LAYERS",
                "PROPS", "PHYSICS",
            ),
        )
        self.assertIn("npc_behavior", model["features"])
        self.assertIn("intro_replay", model["features"])
        self.assertIn("combo_attack", model["features"])
        self.assertIn("attack_lock", model["features"])
        self.assertIn("despawn", model["features"])
        self.assertIn("corpse", model["features"])
        self.assertIn("props", model["features"])
        self.assertIn("physics", model["features"])
        self.assertIn("layers", model["features"])
        self.assertIn("vfx", model["features"])

    def test_ai_copy_mentions_intro_combo_and_hitbox(self):
        keys = ase_viewer.settings_section_model(
            ase_viewer.SETTINGS_SECTION_SCENE_COMBAT,
        )["info_keys"]
        text = " ".join(ase_viewer.tr(key, language="en") for key in keys)
        self.assertIn("Intro", text)
        self.assertIn("ComboAttack_1", text)
        self.assertIn("Corpse", text)


if __name__ == "__main__":
    unittest.main()
