import unittest
from types import SimpleNamespace

import ase_viewer


def profile(name, kind):
    return SimpleNamespace(
        name=name, source_idx=0, kind=kind,
        is_prop_profile=kind == "prop", mappings={},
    )


def entity(actor_profile, **overrides):
    values = {
        "profile": actor_profile, "visible": True,
        "is_dead": False, "is_corpse": False,
        "decision": "IDLE", "x": 0.0, "y": 500.0,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def scene_player(npcs):
    player_profile = profile("Player", "player")
    npc_profile = profile("NPC", "npc")
    player = SimpleNamespace(
        profiles=[player_profile, npc_profile],
        sources=[SimpleNamespace(name="NPC.aseprite")],
        ai_list=npcs, prop_list=[], partner_profiles=[],
        selected_scene_actor_key=None, cur_profile_idx=1,
        cur_source_idx=0, visible=True, decision="IDLE",
        x=0.0, y=500.0, target_ai_count=len(npcs),
        scene_object_filter="all", scene_status_message="",
    )
    return player


class SceneDespawnSelectedTests(unittest.TestCase):
    def test_live_selected_npc_is_removed_without_corpse_or_respawn_target(self):
        npc_profile = profile("NPC", "npc")
        selected = entity(npc_profile, intro_locked=True)
        remaining = entity(npc_profile)
        player = scene_player([selected, remaining])
        player.profiles[1] = npc_profile
        player.selected_scene_actor_key = ("npc", id(selected))
        result = ase_viewer.despawn_selected_npc(player)
        self.assertTrue(result["despawned"])
        self.assertNotIn(selected, player.ai_list)
        self.assertFalse(selected.is_corpse)
        self.assertEqual(player.target_ai_count, 1)
        self.assertEqual(player.selected_scene_actor_key, ("npc", id(remaining)))
        self.assertIn(npc_profile, player.profiles)
        self.assertEqual(len(player.sources), 1)

    def test_combo_locked_npc_can_be_despawned(self):
        npc_profile = profile("NPC", "npc")
        npc = entity(npc_profile, npc_attack_locked=True)
        player = scene_player([npc])
        player.profiles[1] = npc_profile
        player.selected_scene_actor_key = ("npc", id(npc))
        self.assertTrue(ase_viewer.despawn_selected_npc(player)["despawned"])
        self.assertEqual(player.ai_list, [])
        self.assertEqual(player.target_ai_count, 0)

    def test_player_corpse_prop_and_no_selection_are_rejected(self):
        npc_profile = profile("NPC", "npc")
        corpse = entity(npc_profile, is_dead=True, is_corpse=True)
        player = scene_player([corpse])
        player.profiles[1] = npc_profile

        self.assertEqual(
            ase_viewer.despawn_selected_npc(player)["status_key"],
            "selection.no_npc_selected",
        )
        player.selected_scene_actor_key = ("player", id(player))
        self.assertEqual(
            ase_viewer.despawn_selected_npc(player)["status_key"],
            "selection.player_not_despawnable",
        )
        player.selected_scene_actor_key = ("npc", id(corpse))
        self.assertEqual(
            ase_viewer.despawn_selected_npc(player)["status_key"],
            "selection.corpse_use_delete",
        )


if __name__ == "__main__":
    unittest.main()
