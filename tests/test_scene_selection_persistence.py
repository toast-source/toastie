import unittest
from types import SimpleNamespace

import ase_viewer


def fixture():
    source = SimpleNamespace(name="Scene.aseprite")
    player_profile = SimpleNamespace(name="PLAYER", source_idx=0, kind="player")
    npc_profile = SimpleNamespace(name="NPC_1", source_idx=0, kind="npc")
    npc = SimpleNamespace(
        profile=npc_profile, visible=True,
        is_dead=False, is_corpse=False, decision="IDLE",
        x=721.5, y=418.25,
    )
    player = SimpleNamespace(
        sources=[source], profiles=[player_profile, npc_profile],
        ai_list=[npc], prop_list=[],
        cur_profile_idx=1, cur_source_idx=0,
        selected_scene_actor_key=("npc", id(npc)),
        scene_object_filter=ase_viewer.SCENE_FILTER_ALL,
        scene_status_message="", language="ko", visible=True,
        x=100.0, y=200.0, cam_x=100.0, cam_y=200.0, cam_follow=True,
    )
    return player, npc


class SceneSelectionPersistenceTests(unittest.TestCase):
    def test_sidebar_mode_switches_do_not_change_scene_selection(self):
        player, npc = fixture()
        selected_key = ("npc", id(npc))
        mode = ase_viewer.SIDEBAR_SCENE
        for requested in (
            ase_viewer.SIDEBAR_RESOURCES,
            ase_viewer.SIDEBAR_SCENE,
            ase_viewer.SIDEBAR_SETTINGS,
            ase_viewer.SIDEBAR_SCENE,
        ):
            mode = ase_viewer.set_sidebar_mode(mode, requested)
            self.assertEqual(player.selected_scene_actor_key, selected_key)

    def test_filter_and_language_change_preserve_identity(self):
        player, npc = fixture()
        selected_key = ("npc", id(npc))
        ase_viewer.set_scene_object_filter(player, "prop")
        player.language = "en"
        ase_viewer.selection_workspace_model(player)
        ase_viewer.set_scene_object_filter(player, "all")
        self.assertEqual(player.selected_scene_actor_key, selected_key)

    def test_focus_moves_only_camera_and_disables_follow(self):
        player, npc = fixture()
        original_player_position = (player.x, player.y)
        original_npc_position = (npc.x, npc.y)
        self.assertTrue(ase_viewer.focus_selected_scene_object(player))
        self.assertEqual((player.cam_x, player.cam_y), original_npc_position)
        self.assertFalse(player.cam_follow)
        self.assertEqual((player.x, player.y), original_player_position)
        self.assertEqual((npc.x, npc.y), original_npc_position)

    def test_focus_without_explicit_selection_is_safe_noop(self):
        player, _npc = fixture()
        player.selected_scene_actor_key = None
        original_camera = (player.cam_x, player.cam_y, player.cam_follow)
        self.assertFalse(ase_viewer.focus_selected_scene_object(player))
        self.assertEqual(
            (player.cam_x, player.cam_y, player.cam_follow), original_camera,
        )
        self.assertEqual(
            player.scene_status_message,
            ase_viewer.tr("selection.no_scene_selected"),
        )


if __name__ == "__main__":
    unittest.main()
