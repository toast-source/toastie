import unittest
from types import SimpleNamespace

import pygame

import ase_viewer


class SynergyKeyGuideTests(unittest.TestCase):
    def tearDown(self):
        ase_viewer.set_current_language(ase_viewer.LANG_KO)

    def test_default_synergy_key_appears_in_character_group(self):
        player = SimpleNamespace(key_map={"SYNERGY": pygame.K_e})

        items = ase_viewer.character_key_guide_items(player)

        self.assertIn(("E", ase_viewer.tr("guide.synergy"), None), items)

    def test_remapped_synergy_key_is_reflected(self):
        player = SimpleNamespace(key_map={"SYNERGY": pygame.K_q})

        items = ase_viewer.character_key_guide_items(player)

        self.assertIn(("Q", ase_viewer.tr("guide.synergy"), None), items)
        self.assertNotIn(("E", ase_viewer.tr("guide.synergy"), None), items)

    def test_missing_synergy_mapping_does_not_invent_a_key(self):
        player = SimpleNamespace(key_map={})

        items = ase_viewer.character_key_guide_items(player)

        self.assertFalse(
            any(label == ase_viewer.tr("guide.synergy") for _, label, _ in items),
        )

    def test_synergy_is_character_only_and_localized(self):
        player = SimpleNamespace(
            key_map={"SYNERGY": pygame.K_e}, playback_speed=1.0,
        )
        for language, expected in (
            (ase_viewer.LANG_KO, "합격기"),
            (ase_viewer.LANG_EN, "Synergy"),
        ):
            ase_viewer.set_current_language(language)
            groups = ase_viewer.bottom_key_guide_groups(player)
            character = next(
                group for group in groups if group["id"] == "character"
            )
            app = next(group for group in groups if group["id"] == "app")
            self.assertIn(("E", expected, None), character["items"])
            self.assertFalse(
                any(label == expected for _, label, _ in app["items"]),
            )


if __name__ == "__main__":
    unittest.main()
