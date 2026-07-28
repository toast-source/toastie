import unittest
from types import SimpleNamespace

import ase_viewer


def fixture():
    source = SimpleNamespace(name="SporeHeart.aseprite")
    player_profile = SimpleNamespace(name="PLAYER", source_idx=0, kind="player")
    npc_profile = SimpleNamespace(name="NPC_1", source_idx=0, kind="npc")
    living = SimpleNamespace(
        profile=npc_profile, visible=True, is_dead=False,
        is_corpse=False, decision="IDLE",
    )
    corpse = SimpleNamespace(
        profile=npc_profile, visible=True, is_dead=True,
        is_corpse=True, decision="DEAD",
    )
    player = SimpleNamespace(
        sources=[source], profiles=[player_profile, npc_profile],
        ai_list=[living, corpse], prop_list=[],
        cur_profile_idx=1, cur_source_idx=0, language="ko", visible=True,
    )
    return player, living, corpse


class CorpseCleanupTests(unittest.TestCase):
    def test_explicit_corpse_states_are_detected_before_name_fallback(self):
        self.assertTrue(ase_viewer._is_scene_object_corpse(
            SimpleNamespace(is_corpse=True),
        ))
        self.assertTrue(ase_viewer._is_scene_object_corpse(
            SimpleNamespace(is_corpse=False, is_dead=True),
        ))
        self.assertTrue(ase_viewer._is_scene_object_corpse(
            SimpleNamespace(is_corpse=False, is_dead=False, state="remnant"),
        ))
        self.assertFalse(ase_viewer._is_scene_object_corpse(
            SimpleNamespace(is_corpse=False, is_dead=False, state="idle", name="Deadly"),
        ))

    def test_selected_corpse_is_deleted_and_selection_falls_back(self):
        player, living, corpse = fixture()
        player.selected_scene_actor_key = ("npc", id(corpse))
        result = ase_viewer.delete_selected_corpse(player)
        self.assertTrue(result["deleted"])
        self.assertNotIn(corpse, player.ai_list)
        self.assertIn(living, player.ai_list)
        self.assertNotEqual(
            getattr(player, "selected_scene_actor_key", None),
            ("npc", id(corpse)),
        )
        npc_rows = [
            row for row in ase_viewer.build_scene_actor_rows(player)
            if row["kind"] == "npc"
        ]
        self.assertEqual(npc_rows[0]["badge_text"], "NPC 01")

    def test_living_selection_is_safe_noop(self):
        player, living, corpse = fixture()
        player.selected_scene_actor_key = ("npc", id(living))
        result = ase_viewer.delete_selected_corpse(player)
        self.assertFalse(result["deleted"])
        self.assertEqual(result["status_key"], "selection.no_corpse_selected")
        self.assertEqual(player.ai_list, [living, corpse])

    def test_no_corpse_is_safe_noop(self):
        player, living, _corpse = fixture()
        player.ai_list = [living]
        player.selected_scene_actor_key = ("npc", id(living))
        result = ase_viewer.delete_selected_corpse(player)
        self.assertFalse(result["deleted"])
        self.assertEqual(result["status_key"], "selection.no_corpses")
        self.assertEqual(player.ai_list, [living])


if __name__ == "__main__":
    unittest.main()
