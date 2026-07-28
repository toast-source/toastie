import os
import unittest
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import ase_viewer


def source(name, revision=1):
    return SimpleNamespace(
        name=name,
        file_path=name,
        source_revision=revision,
        slice_analysis_revision=None,
        slice_export_analysis=None,
    )


def profile(name, source_idx, kind):
    return SimpleNamespace(
        name=name,
        source_idx=source_idx,
        kind=kind,
        is_prop_profile=kind == "prop",
    )


def actor(profile_value, **state):
    defaults = {"profile": profile_value, "visible": True, "is_corpse": False}
    defaults.update(state)
    return SimpleNamespace(**defaults)


def player_fixture():
    sources = [source("SporeHeart.aseprite"), source("Goblin.aseprite")]
    profiles = [
        profile("PLAYER", 0, "player"),
        profile("NPC_1", 0, "npc"),
        profile("Goblin Captain", 1, "npc"),
        profile("PROP_3", 1, "prop"),
    ]
    return SimpleNamespace(
        sources=sources,
        profiles=profiles,
        ai_list=[actor(profiles[1]), actor(profiles[1]), actor(profiles[2], is_corpse=True)],
        prop_list=[actor(profiles[3])],
        cur_profile_idx=0,
        cur_source_idx=0,
        language=ase_viewer.LANG_KO,
        visible=True,
    )


class SelectionWorkspaceTests(unittest.TestCase):
    def test_empty_state(self):
        player = SimpleNamespace(
            sources=[], profiles=[], ai_list=[], prop_list=[],
            cur_profile_idx=0, cur_source_idx=0, language="ko", visible=True,
        )
        model = ase_viewer.selection_workspace_model(player)
        self.assertEqual(model["scene_rows"], [])
        self.assertEqual(model["resource_rows"], [])
        summary = ase_viewer.current_selection_summary(player)
        self.assertIsNone(summary["actor"])

    def test_scene_rows_are_instances_with_friendly_names_and_numbers(self):
        player = player_fixture()
        rows = ase_viewer.build_scene_actor_rows(player)
        self.assertEqual([row["kind"] for row in rows], ["player", "npc", "npc", "npc", "prop"])
        self.assertEqual(rows[0]["display_name"], "SporeHeart")
        self.assertEqual(rows[1]["display_name"], "SporeHeart #1")
        self.assertEqual(rows[2]["display_name"], "SporeHeart #2")
        self.assertEqual(rows[3]["display_name"], "Goblin Captain #1")
        self.assertEqual(rows[3]["status"], "corpse")
        self.assertEqual(rows[4]["display_name"], "Goblin #1")

    def test_actor_selection_updates_existing_profile_and_source_indices(self):
        player = player_fixture()
        npc_row = ase_viewer.build_scene_actor_rows(player)[3]
        self.assertTrue(ase_viewer.select_scene_actor(player, npc_row["key"]))
        self.assertEqual(player.cur_profile_idx, 2)
        self.assertEqual(player.cur_source_idx, 1)
        self.assertEqual(
            ase_viewer.current_selection_summary(player)["linked_source_index"], 1,
        )

    def test_missing_profile_fallback_is_not_selectable(self):
        player = player_fixture()
        orphan = actor(None)
        player.ai_list.append(orphan)
        row = next(
            item for item in ase_viewer.build_scene_actor_rows(player)
            if item["key"] == ("npc", id(orphan))
        )
        self.assertEqual(row["display_name"], "NPC #1")
        self.assertFalse(ase_viewer.select_scene_actor(player, row["key"]))

    def test_deleted_selected_instance_falls_back_safely(self):
        player = player_fixture()
        selected = player.ai_list[0]
        self.assertTrue(ase_viewer.select_scene_actor(player, ("npc", id(selected))))
        player.ai_list.remove(selected)
        summary = ase_viewer.current_selection_summary(player)
        self.assertIsNotNone(summary["actor"])
        self.assertLess(summary["actor"]["profile_index"], len(player.profiles))

    def test_model_is_reused_until_data_or_state_changes(self):
        player = player_fixture()
        first = ase_viewer.selection_workspace_model(player)
        self.assertIs(first, ase_viewer.selection_workspace_model(player))
        player.ai_list[0].is_corpse = True
        second = ase_viewer.selection_workspace_model(player)
        self.assertIsNot(first, second)
        self.assertEqual(second["scene_rows"][1]["status"], "corpse")

    def test_workspace_uses_explicit_content_viewport_without_duplicate_tabs(self):
        import pygame

        pygame.init()
        pygame.display.set_mode((1, 1))
        surface = pygame.Surface((1100, 720))
        viewport = pygame.Rect(
            650, ase_viewer.TOP_UI_HEIGHT, 450, 720 - ase_viewer.TOP_UI_HEIGHT,
        )
        regions = []
        result = ase_viewer.draw_selection_workspace(
            surface, player_fixture(), ase_viewer.SIDEBAR_SCENE, 0,
            (ase_viewer.create_ui_font(12), ase_viewer.create_ui_font(14, bold=True)),
            regions, viewport_rect=viewport,
        )
        self.assertTrue(viewport.contains(result["viewport"]))
        self.assertFalse(any(control["action"] == "tab" for control in result["controls"]))
        actions = [control["action"] for control in result["controls"]]
        self.assertEqual(actions.count("scene_filter"), 5)
        self.assertIn("focus_selected", actions)
        self.assertIn("delete_corpse", actions)
        self.assertIn("delete_all_corpses", actions)
        self.assertTrue(
            all(viewport.contains(control["rect"]) for control in result["controls"])
        )
        filter_controls = [
            control for control in result["controls"]
            if control["action"] == "scene_filter"
        ]
        self.assertTrue(
            all(control["rect"].bottom <= result["viewport"].top for control in filter_controls)
        )
        action_controls = [
            control for control in result["controls"]
            if control["action"] in {
                "focus_selected", "delete_corpse", "delete_all_corpses",
            }
        ]
        self.assertTrue(
            all(control["rect"].top >= result["viewport"].bottom for control in action_controls)
        )

        hidden_player = player_fixture()
        corpse = hidden_player.ai_list[-1]
        hidden_player.selected_scene_actor_key = ("npc", id(corpse))
        hidden_player.scene_object_filter = ase_viewer.SCENE_FILTER_NPC
        hidden_result = ase_viewer.draw_selection_workspace(
            surface, hidden_player, ase_viewer.SIDEBAR_SCENE, 0,
            (ase_viewer.create_ui_font(12), ase_viewer.create_ui_font(14, bold=True)),
            [], viewport_rect=viewport,
        )
        delete_control = next(
            control for control in hidden_result["controls"]
            if control["action"] == "delete_corpse"
        )
        self.assertFalse(delete_control["enabled"])
        self.assertEqual(
            hidden_player.selected_scene_actor_key, ("npc", id(corpse)),
        )


if __name__ == "__main__":
    unittest.main()
