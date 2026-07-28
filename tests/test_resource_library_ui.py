import os
import unittest
from types import SimpleNamespace
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import ase_viewer


def make_player():
    analysis = {
        "revision": 3,
        "valid_parts_slices": [object(), object()],
        "valid_particle_slices": [object()],
    }
    source = SimpleNamespace(
        name="Shared.aseprite",
        file_path=r"C:\Art\Shared.aseprite",
        source_revision=3,
        slice_analysis_revision=3,
        slice_export_analysis=analysis,
    )
    player_profile = SimpleNamespace(name="PLAYER", source_idx=0, kind="player", is_prop_profile=False)
    partner_profile = SimpleNamespace(name="PARTNER_1", source_idx=0, kind="partner", is_prop_profile=False)
    npc_profile = SimpleNamespace(name="NPC_2", source_idx=0, kind="npc", is_prop_profile=False)
    prop_profile = SimpleNamespace(name="PROP_3", source_idx=0, kind="prop", is_prop_profile=True)
    return SimpleNamespace(
        sources=[source],
        profiles=[player_profile, partner_profile, npc_profile, prop_profile],
        partner_list=[SimpleNamespace(profile=partner_profile)],
        ai_list=[SimpleNamespace(profile=npc_profile)],
        prop_list=[SimpleNamespace(profile=prop_profile)],
        cur_profile_idx=0,
        cur_source_idx=0,
        language="ko",
        visible=True,
    )


class ResourceLibraryUiTests(unittest.TestCase):
    def test_roles_counts_and_action_capabilities(self):
        row = ase_viewer.build_resource_library_rows(make_player())[0]
        self.assertEqual(row["roles"], ["NPC", "PARTNER", "PLAYER", "PROP"])
        self.assertEqual(
            (row["partner_profiles"], row["npc_instances"], row["prop_instances"]),
            (1, 1, 1),
        )
        self.assertEqual((row["parts"], row["particles"]), (2, 1))
        self.assertTrue(row["can_use_player"])
        self.assertTrue(row["can_spawn_npc"])
        self.assertTrue(row["can_place_prop"])
        self.assertTrue(row["can_export_png"])

    def test_missing_roles_disable_unsupported_actions(self):
        player = make_player()
        player.profiles = [player.profiles[2]]
        player.partner_list = []
        row = ase_viewer.build_resource_library_rows(player)[0]
        self.assertFalse(row["can_use_player"])
        self.assertTrue(row["can_spawn_npc"])
        self.assertFalse(row["can_place_prop"])

    def test_existing_callbacks_are_reused(self):
        player = make_player()
        player.spawn_npc_profile = mock.Mock(return_value=True)
        self.assertTrue(ase_viewer.activate_resource_action(player, "spawn_npc", 0))
        player.spawn_npc_profile.assert_called_once_with(2)
        with mock.patch.object(ase_viewer, "begin_slice_export", return_value=True) as export:
            self.assertTrue(ase_viewer.activate_resource_action(player, "export_png", 0))
            export.assert_called_once_with(player, player.sources[0], "Source")

    def test_visible_range_limits_fifty_rows_and_clamps(self):
        start, end, offset, maximum = ase_viewer.visible_row_range(50, 99999, 580, 58)
        self.assertEqual(offset, maximum)
        self.assertLessEqual(end - start, 12)
        self.assertEqual(end, 50)

    def test_library_does_not_trigger_slice_analysis(self):
        player = make_player()
        player.sources[0].slice_export_analysis = None
        with mock.patch.object(
            ase_viewer, "ensure_source_slice_analysis",
            side_effect=AssertionError("must not analyze during list build"),
        ):
            row = ase_viewer.build_resource_library_rows(player)[0]
        self.assertEqual((row["parts"], row["particles"]), (0, 0))


if __name__ == "__main__":
    unittest.main()
