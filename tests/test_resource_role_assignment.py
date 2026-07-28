import os
import json
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


def source_stub(source_id=0, name="Shared.aseprite"):
    return SimpleNamespace(
        id=source_id,
        name=name,
        file_path=name,
        kind="generic",
        is_prop_source=False,
        tags={},
        tag_list=[],
        frames=[],
        slices={},
        source_revision=1,
        slice_analysis_revision=None,
        slice_export_analysis=None,
        export_and_load=lambda: True,
        clear_cache=lambda: None,
    )


class ResourceRoleAssignmentTests(unittest.TestCase):
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
        self.source = source_stub()
        self.player.sources = [self.source]
        self.analysis = mock.patch.object(
            ase_viewer,
            "ensure_source_slice_analysis",
            return_value={
                "valid_parts_slices": [], "valid_particle_slices": [],
            },
        )
        self.analysis.start()

    def tearDown(self):
        self.analysis.stop()
        self.temp_dir.cleanup()

    def test_import_resource_does_not_force_a_scene_role(self):
        player = self.player
        player.sources = []
        with mock.patch.object(player, "_create_source", return_value=self.source):
            self.assertEqual(player.add_source("Shared.aseprite"), 0)
        self.assertEqual(player.profiles, [])
        self.assertEqual(player.partner_profiles, [])
        self.assertEqual(player.partner_list, [])
        self.assertEqual(player.ai_list, [])
        self.assertEqual(player.prop_list, [])

    def test_same_source_can_receive_all_roles_as_separate_profiles(self):
        original_source_name = self.source.name
        original_source_path = self.source.file_path
        with mock.patch.object(self.player, "auto_map_profile"):
            player_result = ase_viewer.assign_resource_role(self.player, 0, "player")
            partner_result = ase_viewer.assign_resource_role(self.player, 0, "partner")
            npc_result = ase_viewer.assign_resource_role(self.player, 0, "npc")
            prop_result = ase_viewer.assign_resource_role(self.player, 0, "prop")

        self.assertTrue(player_result["assigned"])
        self.assertTrue(partner_result["assigned"])
        self.assertTrue(npc_result["assigned"])
        self.assertTrue(prop_result["assigned"])
        profiles = [
            player_result["profile"], partner_result["profile"],
            npc_result["profile"], prop_result["profile"],
        ]
        self.assertEqual(len({id(profile) for profile in profiles}), 4)
        self.assertEqual(
            [ase_viewer.profile_kind(profile, index) for index, profile in enumerate(self.player.profiles)],
            ["player", "partner", "npc", "prop"],
        )
        self.assertEqual(len(self.player.partner_profiles), 1)
        self.assertEqual(self.player.partner_list, [])
        self.assertIsNone(partner_result["instance"])
        self.assertEqual(len(self.player.ai_list), 1)
        self.assertEqual(len(self.player.prop_list), 1)
        self.assertEqual(self.player.target_ai_count, 1)
        self.assertEqual(self.source.name, original_source_name)
        self.assertEqual(self.source.file_path, original_source_path)
        self.assertEqual(self.source.kind, "generic")

    def test_partner_or_player_assignment_never_creates_an_npc(self):
        with mock.patch.object(self.player, "auto_map_profile"):
            partner = ase_viewer.assign_resource_role(self.player, 0, "partner")
            self.assertTrue(partner["assigned"])
            self.assertFalse(self.player.ai_list)
            self.assertEqual(self.player.target_ai_count, 0)
            player = ase_viewer.assign_resource_role(self.player, 0, "player")
            self.assertTrue(player["assigned"])
            self.assertFalse(self.player.ai_list)
            self.assertEqual(self.player.target_ai_count, 0)

    def test_invalid_resource_is_safe_noop(self):
        result = ase_viewer.assign_resource_role(self.player, 99, "partner")
        self.assertFalse(result["assigned"])
        self.assertEqual(
            self.player.resource_status_message,
            ase_viewer.tr("selection.no_resource_selected"),
        )
        self.assertFalse(self.player.profiles)

    def test_role_actions_preserve_existing_scene_positions_and_selection(self):
        player_profile = ase_viewer.AseProfile("PLAYER", 0, kind="player")
        partner_profile = ase_viewer.AseProfile("PARTNER", 0, kind="partner")
        npc_profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        prop_profile = ase_viewer.AseProfile("PROP", 0, kind="prop")
        self.player.profiles = [
            player_profile, partner_profile, npc_profile, prop_profile,
        ]
        npc = ase_viewer.AseAI(self.player, npc_profile)
        prop = ase_viewer.AseAI(self.player, prop_profile, is_prop=True)
        self.player.partner_profiles = [partner_profile]
        self.player.partner_list = []
        self.player.ai_list = [npc]
        self.player.prop_list = [prop]
        self.player.target_ai_count = 1
        self.player.x, self.player.y = 101, 202
        npc.x, npc.y = 505, 606
        prop.x, prop.y = 707, 808
        selected_key = ("npc", id(npc))
        self.player.selected_scene_actor_key = selected_key

        with mock.patch.object(self.player, "auto_map_profile"):
            for role in ("partner", "npc", "prop", "player"):
                with self.subTest(role=role):
                    self.assertTrue(
                        ase_viewer.assign_resource_role(
                            self.player, 0, role,
                        )["assigned"],
                    )
                    self.assertEqual((self.player.x, self.player.y), (101, 202))
                    self.assertEqual((npc.x, npc.y), (505, 606))
                    self.assertEqual((prop.x, prop.y), (707, 808))
                    self.assertEqual(
                        self.player.selected_scene_actor_key, selected_key,
                    )

    def test_resource_action_area_exposes_four_role_buttons(self):
        self.player.profiles = [
            ase_viewer.AseProfile("PLAYER", 0, kind="player"),
        ]
        surface = pygame.Surface((1100, 720))
        viewport = pygame.Rect(
            650, ase_viewer.TOP_UI_HEIGHT,
            ase_viewer.SIDEBAR_WIDTH, 720 - ase_viewer.TOP_UI_HEIGHT,
        )
        result = ase_viewer.draw_selection_workspace(
            surface, self.player, ase_viewer.SIDEBAR_RESOURCES, 0,
            (
                ase_viewer.create_ui_font(12),
                ase_viewer.create_ui_font(14, bold=True),
            ),
            [], viewport_rect=viewport,
        )
        actions = {control["action"] for control in result["controls"]}
        self.assertTrue(
            {"assign_player", "add_partner", "add_npc", "add_prop"}
            <= actions,
        )
        self.assertTrue(
            all(viewport.contains(control["rect"]) for control in result["controls"])
        )
        for language in ("ko", "en"):
            for key in (
                "selection.assign_player", "selection.add_partner",
                "selection.add_npc", "selection.add_prop",
            ):
                self.assertTrue(ase_viewer.tr(key, language=language))

    def test_partner_kind_is_optional_and_backward_compatible_on_load(self):
        source_path = os.path.join(self.temp_dir.name, "Shared.aseprite")
        with open(source_path, "wb") as source_file:
            source_file.write(b"fixture")
        self.source.file_path = source_path
        self.player.profiles = [
            ase_viewer.AseProfile("PLAYER", 0, kind="player"),
            ase_viewer.AseProfile("SWAP", 0, kind="partner"),
        ]
        self.player.save_project()
        with open(self.player.project_path, "r", encoding="utf-8") as project_file:
            saved = json.load(project_file)
        self.assertEqual(
            [profile["kind"] for profile in saved["profiles"]],
            ["player", "partner"],
        )

        loaded = ase_viewer.AsepritePlayer(
            project_path=self.player.project_path,
            settings_path=os.path.join(self.temp_dir.name, "loaded-settings.json"),
        )
        loaded_source = source_stub()
        with (
            mock.patch.object(loaded, "_create_source", return_value=loaded_source),
            mock.patch.object(ase_viewer, "ensure_source_slice_analysis", return_value={
                "valid_parts_slices": [], "valid_particle_slices": [],
            }),
        ):
            self.assertTrue(loaded.load_project())
        self.assertEqual(
            [ase_viewer.profile_kind(profile, index) for index, profile in enumerate(loaded.profiles)],
            ["player", "partner"],
        )
        self.assertEqual(len(loaded.partner_profiles), 1)
        self.assertEqual(loaded.partner_list, [])


if __name__ == "__main__":
    unittest.main()
