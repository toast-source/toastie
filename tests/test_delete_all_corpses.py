import unittest
from types import SimpleNamespace

import ase_viewer


def fixture():
    source = SimpleNamespace(name="Scene.aseprite")
    player_profile = SimpleNamespace(name="PLAYER", source_idx=0, kind="player")
    npc_profile = SimpleNamespace(name="NPC_1", source_idx=0, kind="npc")
    prop_profile = SimpleNamespace(
        name="PROP_2", source_idx=0, kind="prop", is_prop_profile=True,
    )
    living = SimpleNamespace(
        name="Corpse Knight", profile=npc_profile, visible=True,
        is_dead=False, is_corpse=False, decision="IDLE",
    )
    corpse_flag = SimpleNamespace(
        profile=npc_profile, visible=True,
        is_dead=True, is_corpse=True, decision="DEAD",
    )
    corpse_state = SimpleNamespace(
        profile=npc_profile, visible=True,
        is_dead=False, is_corpse=False, decision="dead_hold",
    )
    prop = SimpleNamespace(
        profile=prop_profile, visible=True,
        is_dead=False, is_corpse=False, decision="IDLE",
    )
    player = SimpleNamespace(
        sources=[source], profiles=[player_profile, npc_profile, prop_profile],
        ai_list=[living, corpse_flag, corpse_state], prop_list=[prop],
        cur_profile_idx=1, cur_source_idx=0,
        selected_scene_actor_key=None,
        scene_object_filter=ase_viewer.SCENE_FILTER_ALL,
        scene_status_message="", language="ko", visible=True,
    )
    return player, living, corpse_flag, corpse_state, prop


class DeleteAllCorpsesTests(unittest.TestCase):
    def test_multiple_corpses_removed_without_touching_living_or_prop(self):
        player, living, corpse_flag, corpse_state, prop = fixture()
        player.selected_scene_actor_key = ("npc", id(corpse_flag))
        result = ase_viewer.delete_all_corpses(player)
        self.assertEqual(result["deleted"], 2)
        self.assertEqual(player.ai_list, [living])
        self.assertEqual(player.prop_list, [prop])
        self.assertNotIn(corpse_flag, player.ai_list)
        self.assertNotIn(corpse_state, player.ai_list)
        self.assertEqual(
            player.scene_status_message,
            ase_viewer.tr("selection.corpses_deleted", count=2),
        )
        remaining_npc = next(
            row for row in ase_viewer.build_scene_actor_rows(player)
            if row["kind"] == "npc"
        )
        self.assertEqual(remaining_npc["badge_text"], "NPC 01")

    def test_living_selection_and_identity_are_preserved(self):
        player, living, _corpse_flag, _corpse_state, _prop = fixture()
        selected_key = ("npc", id(living))
        player.selected_scene_actor_key = selected_key
        result = ase_viewer.delete_all_corpses(player)
        self.assertEqual(result["deleted"], 2)
        self.assertEqual(player.selected_scene_actor_key, selected_key)
        self.assertIs(player.ai_list[0], living)

    def test_deleted_selection_uses_visible_fallback_or_clears(self):
        player, _living, corpse_flag, _corpse_state, prop = fixture()
        player.selected_scene_actor_key = ("npc", id(corpse_flag))
        result = ase_viewer.delete_all_corpses(player)
        self.assertEqual(result["deleted"], 2)
        self.assertIn(
            player.selected_scene_actor_key,
            {("player", id(player)), ("npc", id(player.ai_list[0])), ("prop", id(prop))},
        )

        filtered, _living, filtered_corpse, _other_corpse, _prop = fixture()
        filtered.scene_object_filter = ase_viewer.SCENE_FILTER_CORPSE
        filtered.selected_scene_actor_key = ("npc", id(filtered_corpse))
        ase_viewer.delete_all_corpses(filtered)
        self.assertIsNone(filtered.selected_scene_actor_key)

    def test_no_corpse_is_noop_and_explicit_living_state_beats_name(self):
        player, living, _corpse_flag, _corpse_state, prop = fixture()
        player.ai_list = [living]
        player.selected_scene_actor_key = ("npc", id(living))
        result = ase_viewer.delete_all_corpses(player)
        self.assertEqual(result["deleted"], 0)
        self.assertEqual(result["status_key"], "selection.no_corpses")
        self.assertEqual(player.ai_list, [living])
        self.assertEqual(player.prop_list, [prop])


if __name__ == "__main__":
    unittest.main()
