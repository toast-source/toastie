import json
import os
import tempfile
import types
import unittest
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


def source(source_id, kind="generic", path="source.aseprite"):
    return types.SimpleNamespace(id=source_id, kind=kind, is_prop_source=kind == "prop", file_path=path)


def entity(profile, source_index):
    return types.SimpleNamespace(
        profile=profile,
        active_tag_info=[source_index, "Idle"],
        active_action_slot="IDLE",
        action_queue=[[source_index, "Idle"]],
    )


class SourceRemovalTests(unittest.TestCase):
    def make_player(self):
        player = ase_viewer.AsepritePlayer(project_path="unused-project.json", settings_path="unused-settings.json")
        player.sources = [source(0), source(1, "npc"), source(2, "prop")]
        player_profile = ase_viewer.AseProfile("PLAYER", 0, kind="player")
        npc_profile = ase_viewer.AseProfile("NPC", 1, kind="npc")
        prop_profile = ase_viewer.AseProfile("PROP", 2, kind="prop")
        for profile in (player_profile, npc_profile, prop_profile):
            profile.mappings["IDLE"] = [[profile.source_idx, "Idle"]]
        player.profiles = [player_profile, npc_profile, prop_profile]
        player.ai_list = [entity(npc_profile, 1)]
        player.temp_ai_list = [entity(npc_profile, 1)]
        player.prop_list = [entity(prop_profile, 2)]
        player.projectiles = [types.SimpleNamespace(source_idx=1), types.SimpleNamespace(source_idx=2)]
        player.afterimages = [{"s": 1}, {"s": 2}]
        player.active_tag_info = [0, "Idle"]
        player.active_action_slot = "IDLE"
        player.action_queue = [[0, "Idle"], [2, "Idle"]]
        player.cur_source_idx = 2
        player.cur_profile_idx = 2
        player.target_ai_count = 1
        player.roaming_npc_idx = 1
        player.swap_target_idx = 1
        return player

    def test_remove_middle_source_deletes_linked_profile_and_shifts_later_indices(self):
        player = self.make_player()
        result = player.remove_source_by_index(1)
        self.assertTrue(result["removed"])
        self.assertEqual(result["profiles"], 1)
        self.assertEqual(result["npcs"], 2)
        self.assertEqual([item.id for item in player.sources], [0, 1])
        self.assertEqual([profile.name for profile in player.profiles], ["PLAYER", "PROP"])
        self.assertEqual(player.profiles[1].source_idx, 1)
        self.assertFalse(player.ai_list)
        self.assertFalse(player.temp_ai_list)
        self.assertEqual(player.prop_list[0].profile.source_idx, 1)
        self.assertEqual([projectile.source_idx for projectile in player.projectiles], [1])
        self.assertEqual(player.afterimages, [{"s": 1}])
        self.assertEqual(player.target_ai_count, 0)

    def test_remove_first_and_last_sources_leave_no_out_of_range_references(self):
        for remove_index in (0, 2):
            with self.subTest(remove_index=remove_index):
                player = self.make_player()
                result = player.remove_source_by_index(remove_index)
                self.assertTrue(all(0 <= p.source_idx < len(player.sources) for p in player.profiles))
                self.assertTrue(all(0 <= mapping[0] < len(player.sources) for p in player.profiles for mappings in p.mappings.values() for mapping in mappings))
                self.assertLessEqual(player.cur_source_idx, max(0, len(player.sources) - 1))
                self.assertLessEqual(player.cur_profile_idx, max(0, len(player.profiles) - 1))
                if remove_index == 0:
                    self.assertTrue(result["player_disabled"])
                    self.assertFalse(player.visible)

    def test_empty_lists_and_invalid_index_are_safe(self):
        player = self.make_player()
        player.sources = []
        player.profiles = []
        player.ai_list = []
        player.temp_ai_list = []
        player.prop_list = []
        result = player.remove_source_by_index(0)
        self.assertFalse(result["removed"])

    def test_project_save_records_kinds_and_rejects_invalid_source_index(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = os.path.join(temp_dir, "npc.aseprite")
            with open(source_path, "wb") as source_file:
                source_file.write(b"fixture")
            project_path = os.path.join(temp_dir, "project.json")
            player = ase_viewer.AsepritePlayer(project_path=project_path, settings_path=os.path.join(temp_dir, "settings.json"))
            player.sources = [source(0, "npc", source_path)]
            player.profiles = [ase_viewer.AseProfile("NPC", 0, kind="npc")]
            player.save_project()
            with open(project_path, "r", encoding="utf-8") as project_file:
                data = json.load(project_file)
            self.assertEqual(data["source_kinds"], ["npc"])
            self.assertEqual(data["profiles"][0]["kind"], "npc")

            with open(project_path, "rb") as project_file:
                original = project_file.read()
            player.profiles[0].source_idx = 99
            with mock.patch("ase_viewer.show_user_error"):
                player.save_project()
            with open(project_path, "rb") as project_file:
                self.assertEqual(project_file.read(), original)

    def test_project_load_preserves_explicit_kinds_and_infers_legacy_profiles(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = os.path.join(temp_dir, "shared.aseprite")
            with open(source_path, "wb") as source_file:
                source_file.write(b"fixture")
            project_path = os.path.join(temp_dir, "project.json")
            settings_path = os.path.join(temp_dir, "settings.json")

            explicit = {
                "schema_version": 2,
                "sources": [source_path],
                "source_kinds": ["prop"],
                "profiles": [{"name": "PROP", "source_idx": 0, "kind": "prop", "mappings": {"DEAD_LOOP": [[0, "Dead_(Loop)"]]}}],
            }
            with open(project_path, "w", encoding="utf-8") as project_file:
                json.dump(explicit, project_file)
            player = ase_viewer.AsepritePlayer(project_path=project_path, settings_path=settings_path)
            with mock.patch.object(player, "_create_source", return_value=source(0, path=source_path)):
                self.assertTrue(player.load_project())
            self.assertEqual(ase_viewer.source_kind(player.sources[0]), "prop")
            self.assertEqual(ase_viewer.profile_kind(player.profiles[0], 0), "prop")
            self.assertEqual(player.profiles[0].mappings["DEAD_LOOP"], [[0, "Dead_(Loop)"]])

            legacy = {
                "sources": [source_path],
                "profiles": [
                    {"name": "FIRST", "source_idx": 0, "mappings": {}},
                    {"name": "SECOND", "source_idx": 0, "mappings": {}},
                ],
            }
            with open(project_path, "w", encoding="utf-8") as project_file:
                json.dump(legacy, project_file)
            with mock.patch.object(player, "_create_source", return_value=source(0, path=source_path)):
                self.assertTrue(player.load_project())
            self.assertEqual(
                [ase_viewer.profile_kind(profile, index) for index, profile in enumerate(player.profiles)],
                ["player", "npc"],
            )


if __name__ == "__main__":
    unittest.main()
