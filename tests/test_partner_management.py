import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


def source_stub():
    return SimpleNamespace(
        id=0, name="Knight.aseprite", file_path="Knight.aseprite",
        kind="generic", is_prop_source=False,
        tags={}, tag_list=[], frames=[], slices={},
        source_revision=1, slice_analysis_revision=None,
        slice_export_analysis=None,
        export_and_load=lambda: True, clear_cache=lambda: None,
    )


class PartnerManagementTests(unittest.TestCase):
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
        self.player.sources = [source_stub()]
        self.player.profiles = [
            ase_viewer.AseProfile("PLAYER", 0, kind="player"),
        ]
        self.analysis = mock.patch.object(
            ase_viewer, "ensure_source_slice_analysis",
            return_value={"valid_parts_slices": [], "valid_particle_slices": []},
        )
        self.analysis.start()

    def tearDown(self):
        self.analysis.stop()
        self.temp_dir.cleanup()

    def add_partner(self):
        with mock.patch.object(self.player, "auto_map_profile"):
            return ase_viewer.assign_resource_role(self.player, 0, "partner")

    def test_add_partner_is_roster_only_and_not_a_scene_actor(self):
        result = self.add_partner()
        self.assertTrue(result["assigned"])
        self.assertIsNone(result["instance"])
        self.assertEqual(
            ase_viewer.partner_roster_profiles(self.player),
            [result["profile"]],
        )
        self.assertEqual(self.player.partner_list, [])
        self.assertEqual(self.player.ai_list, [])
        self.assertEqual(self.player.target_ai_count, 0)
        rows = ase_viewer.build_scene_actor_rows(self.player)
        self.assertEqual([row["kind"] for row in rows], ["player"])
        self.assertNotIn("partner", ase_viewer.SCENE_OBJECT_FILTERS)

    def test_partner_is_not_focus_or_corpse_cleanup_target(self):
        profile = self.add_partner()["profile"]
        self.player.selected_scene_actor_key = ("partner", id(profile))
        camera = (self.player.cam_x, self.player.cam_y)
        self.assertFalse(ase_viewer.focus_selected_scene_object(self.player))
        self.assertEqual((self.player.cam_x, self.player.cam_y), camera)
        self.assertFalse(ase_viewer.delete_selected_corpse(self.player)["deleted"])
        self.assertEqual(ase_viewer.delete_all_corpses(self.player)["deleted"], 0)
        self.assertIn(profile, ase_viewer.partner_roster_profiles(self.player))

    def test_legacy_partner_actor_is_absorbed_without_becoming_scene_data(self):
        profile = ase_viewer.AseProfile("LEGACY", 0, kind="partner")
        self.player.profiles.append(profile)
        legacy = ase_viewer.AseAI(self.player, profile, is_partner=True)
        self.player.partner_list = [legacy]
        self.assertEqual(ase_viewer.partner_roster_profiles(self.player), [profile])
        self.assertEqual(self.player.partner_list, [])
        self.assertNotIn(
            legacy,
            [row["entity"] for row in ase_viewer.build_scene_actor_rows(self.player)],
        )

    def test_f5_refresh_preserves_scene_positions_without_partner_transform(self):
        self.add_partner()
        npc_profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        prop_profile = ase_viewer.AseProfile("PROP", 0, kind="prop")
        self.player.profiles.extend([npc_profile, prop_profile])
        npc = ase_viewer.AseAI(self.player, npc_profile)
        prop = ase_viewer.AseAI(self.player, prop_profile, is_prop=True)
        self.player.ai_list = [npc]
        self.player.prop_list = [prop]
        self.player.x, self.player.y = 111, 222
        npc.x, npc.y = 555, 666
        prop.x, prop.y = 777, 888
        self.player.selected_scene_actor_key = ("npc", id(npc))

        def mutating_refresh():
            self.player.x = npc.x = prop.x = 0
            self.player.selected_scene_actor_key = None
            return True

        self.player.sources[0].export_and_load = mutating_refresh
        with mock.patch.object(self.player, "auto_map_profile"):
            self.assertTrue(
                ase_viewer.refresh_all_sources_preserving_scene(self.player),
            )
        self.assertEqual((self.player.x, self.player.y), (111, 222))
        self.assertEqual((npc.x, npc.y), (555, 666))
        self.assertEqual((prop.x, prop.y), (777, 888))
        self.assertEqual(
            self.player.selected_scene_actor_key, ("npc", id(npc)),
        )


if __name__ == "__main__":
    unittest.main()
