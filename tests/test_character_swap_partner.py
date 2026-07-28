import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


def source_stub(source_id):
    return SimpleNamespace(
        id=source_id, name=f"Actor{source_id}.aseprite",
        file_path=f"Actor{source_id}.aseprite",
        kind="generic", is_prop_source=False,
        tags={}, tag_list=[], frames=[], slices={},
        source_revision=1, slice_analysis_revision=None,
        slice_export_analysis=None,
        clear_cache=lambda: None,
    )


class CharacterSwapPartnerTests(unittest.TestCase):
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
        self.player.sources = [source_stub(0), source_stub(1)]
        self.player_profile = ase_viewer.AseProfile("PLAYER", 0, kind="player")
        self.partner_profile = ase_viewer.AseProfile("PARTNER_1", 1, kind="partner")
        self.player.profiles = [self.player_profile, self.partner_profile]
        self.analysis = mock.patch.object(
            ase_viewer, "ensure_source_slice_analysis",
            return_value={"valid_parts_slices": [], "valid_particle_slices": []},
        )
        self.analysis.start()
        self.player.partner_profiles = [self.partner_profile]
        self.player.partner_list = []
        self.player.swap_target_idx = 1

    def tearDown(self):
        self.analysis.stop()
        self.temp_dir.cleanup()

    def test_swap_candidate_is_partner_not_npc_and_does_not_change_npc_count(self):
        self.assertEqual(
            ase_viewer.swap_candidate_profile_indices(self.player), [1],
        )
        npc_profile = ase_viewer.AseProfile("Enemy", 0, kind="npc")
        self.player.profiles.append(npc_profile)
        npc = ase_viewer.AseAI(self.player, npc_profile)
        npc.x, npc.y = 900, 450
        self.player.ai_list = [npc]
        self.player.target_ai_count = 1
        before_npc = (npc.x, npc.y)
        self.player.x, self.player.y = 321.5, 456.25
        before_player = (self.player.x, self.player.y)
        props_before = list(self.player.prop_list)

        self.player.execute_swap()

        self.assertTrue(self.player.temp_ai_list)
        self.assertTrue(self.player.temp_ai_list[-1].is_swap_departure)
        self.assertTrue(self.player.temp_ai_list[-1].render_below_player)
        self.assertEqual(self.player.target_ai_count, 1)
        self.assertEqual((npc.x, npc.y), before_npc)
        self.assertIn(npc, self.player.ai_list)
        self.assertEqual(ase_viewer.profile_kind(self.player.profiles[0], 0), "player")
        self.assertEqual(ase_viewer.profile_kind(self.player.profiles[1], 1), "partner")
        self.assertEqual((self.player.x, self.player.y), before_player)
        self.assertEqual(self.player.prop_list, props_before)
        self.assertEqual(self.player.partner_profiles, [self.player_profile])
        self.assertEqual(self.player.partner_list, [])
        self.assertEqual(
            [row["kind"] for row in ase_viewer.build_scene_actor_rows(self.player)],
            ["player", "npc"],
        )

        self.player.execute_swap()
        self.assertIs(self.player.profiles[0], self.player_profile)
        self.assertEqual(ase_viewer.profile_kind(self.player.profiles[0], 0), "player")
        self.assertEqual(ase_viewer.profile_kind(self.player.profiles[1], 1), "partner")
        self.assertEqual(self.player.target_ai_count, 1)
        self.assertEqual((npc.x, npc.y), before_npc)

    def test_selected_partner_becomes_selected_player_after_swap(self):
        self.player.selected_scene_actor_key = ("partner", id(self.partner_profile))
        self.player.execute_swap()
        self.assertEqual(
            self.player.selected_scene_actor_key, ("player", id(self.player)),
        )

    def test_historical_example_registers_swap_candidate_as_partner(self):
        preset = ase_viewer.example_preset(1)
        self.assertEqual(preset["profiles"][1]["name"], "NPC_1")
        self.assertEqual(preset["profiles"][1]["kind"], "partner")
        self.assertEqual(preset["ai_count"], 0)

    def test_legacy_npc_swap_candidate_still_has_fallback(self):
        self.partner_profile.kind = "npc"
        partner = ase_viewer.AseAI(self.player, self.partner_profile)
        self.player.partner_profiles = []
        self.player.partner_list = []
        self.player.ai_list = [partner]
        self.player.target_ai_count = 1
        self.assertEqual(
            ase_viewer.swap_candidate_profile_indices(self.player), [1],
        )
        self.player.execute_swap()
        self.assertNotIn(partner, self.player.ai_list)

    def test_swap_without_partner_is_safe_no_op(self):
        self.player.profiles = [self.player_profile]
        self.player.partner_profiles = []
        before = (
            self.player.profiles[0], self.player.x, self.player.y,
            list(self.player.ai_list), list(self.player.temp_ai_list),
        )

        self.player.execute_swap()

        after = (
            self.player.profiles[0], self.player.x, self.player.y,
            list(self.player.ai_list), list(self.player.temp_ai_list),
        )
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
