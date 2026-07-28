import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


def intro_source(tags=None):
    tags = tags or {"Intro": (0, 1), "Idle": (2, 2)}
    image = pygame.Surface((12, 20), pygame.SRCALPHA)
    image.fill((255, 255, 255, 255))
    return SimpleNamespace(
        id=0,
        name="Emerging.aseprite",
        file_path="Emerging.aseprite",
        kind="generic",
        is_prop_source=False,
        orig_w=32,
        orig_h=32,
        frames=[
            {"img": image, "ox": -6, "oy": -10, "duration": 100}
            for _ in range(3)
        ],
        tags=tags,
        tag_list=list(tags),
        tag_metadata={},
        slices={},
        source_revision=1,
        slice_analysis_revision=None,
        slice_export_analysis=None,
        clear_cache=lambda: None,
    )


class SpawnIntroGroundedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.player = ase_viewer.AsepritePlayer(
            project_path=os.path.join(self.temp_dir.name, "project.json"),
            settings_path=os.path.join(self.temp_dir.name, "settings.json"),
        )
        self.player.sources = [intro_source()]
        self.player.x = 0
        self.player.y = 100
        self.player.grounded = False
        self.player.facing_right = True
        self.player.platforms = [pygame.Rect(50, 320, 200, 20)]
        self.analysis = mock.patch.object(
            ase_viewer,
            "ensure_source_slice_analysis",
            return_value={
                "valid_parts_slices": [],
                "valid_particle_slices": [],
            },
        )
        self.analysis.start()

    def tearDown(self):
        self.analysis.stop()
        self.temp_dir.cleanup()

    def test_intro_tag_is_registered_in_dedicated_slot(self):
        profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        self.player.profiles = [profile]
        self.player.auto_map_profile(profile)
        self.assertEqual(profile.mappings["INTRO"], [[0, "Intro"]])
        self.assertEqual(profile.mappings["IDLE"], [[0, "Idle"]])

    def test_spawn_aliases_are_detected_but_action_intro_is_not(self):
        source = intro_source({
            "Spawn_Intro": (0, 0),
            "Summon": (1, 1),
            "Attack_Intro": (2, 2),
        })
        self.assertEqual(
            ase_viewer.spawn_intro_tags(source),
            ["Spawn_Intro", "Summon"],
        )

    def test_airborne_player_spawns_npc_on_surface_and_plays_intro(self):
        profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        self.player.profiles = [profile]
        self.player.auto_map_profile(profile)
        npc = self.player.spawn_npc_profile(0)
        self.assertEqual((npc.x, npc.y), (100, 320))
        self.assertTrue(npc.grounded)
        self.assertTrue(npc.spawned_with_intro)
        self.assertEqual(npc.active_action_slot, "INTRO")
        self.assertEqual(npc.active_tag_info, [0, "Intro"])

    def test_prop_uses_same_grounded_intro_spawn(self):
        profile = ase_viewer.AseProfile("PROP", 0, kind="prop")
        self.player.profiles = [profile]
        self.player.auto_map_profile(profile)
        prop = ase_viewer.AseAI(
            self.player, profile, is_prop=True, hp=3,
        )
        self.assertEqual((prop.x, prop.y), (100, 320))
        self.assertTrue(prop.spawned_with_intro)
        self.assertEqual(prop.active_action_slot, "INTRO")

    def test_no_platform_falls_back_to_world_ground(self):
        self.player.platforms = []
        profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        self.player.profiles = [profile]
        self.player.auto_map_profile(profile)
        npc = self.player.spawn_npc_profile(0)
        self.assertEqual(npc.y, self.player.world_ground_y)

    def test_missing_intro_is_safe_and_starts_idle(self):
        self.player.sources = [intro_source({"Idle": (0, 0)})]
        profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        self.player.profiles = [profile]
        self.player.auto_map_profile(profile)
        npc = self.player.spawn_npc_profile(0)
        self.assertEqual(profile.mappings["INTRO"], [])
        self.assertFalse(npc.spawned_with_intro)
        self.assertIsNone(npc.active_action_slot)


if __name__ == "__main__":
    unittest.main()
