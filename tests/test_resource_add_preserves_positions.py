import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


def source_stub(source_id, kind):
    return SimpleNamespace(
        id=source_id,
        name=f"{kind}_{source_id}.aseprite",
        file_path=f"{kind}_{source_id}.aseprite",
        kind=kind,
        is_prop_source=kind == "prop",
        tag_list=[],
        tags={},
        slices={},
        frames=[],
        source_revision=1,
        slice_analysis_revision=None,
        slice_export_analysis=None,
        export_and_load=lambda: True,
        clear_cache=lambda: None,
    )


class ResourceAddPreservesPositionsTests(unittest.TestCase):
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
        existing_profile = ase_viewer.AseProfile("Existing", -1, kind="npc")
        self.player.profiles = [existing_profile]
        self.existing = ase_viewer.AseAI(self.player, existing_profile)
        self.existing.x = 913.25
        self.existing.y = 347.5
        self.existing.spawn_x = 901
        self.existing.spawn_y = 333
        self.existing.vx = 4.5
        self.existing.vy = -2.5
        self.existing.facing_right = False
        self.existing.frame_idx = 7
        self.existing.decision = "CHASE"
        self.player.ai_list = [self.existing]
        self.player.target_ai_count = 1
        self.player.selected_scene_actor_key = ("npc", id(self.existing))

    def tearDown(self):
        self.temp_dir.cleanup()

    def assert_existing_unchanged(self):
        self.assertEqual(
            (
                self.existing.x, self.existing.y,
                self.existing.spawn_x, self.existing.spawn_y,
                self.existing.vx, self.existing.vy,
                self.existing.facing_right, self.existing.frame_idx,
                self.existing.decision,
            ),
            (913.25, 347.5, 901, 333, 4.5, -2.5, False, 7, "CHASE"),
        )
        self.assertEqual(
            self.player.selected_scene_actor_key, ("npc", id(self.existing)),
        )

    def analysis(self):
        return {"valid_parts_slices": [], "valid_particle_slices": []}

    def test_npc_resource_add_only_initializes_new_object(self):
        with (
            mock.patch.object(
                self.player, "_create_source",
                side_effect=lambda path, source_id, is_prop, kind: source_stub(source_id, kind),
            ),
            mock.patch.object(self.player, "auto_map_profile"),
            mock.patch.object(
                ase_viewer, "ensure_source_slice_analysis",
                side_effect=lambda source: self.analysis(),
            ),
        ):
            result = self.player.register_npc_source("new_npc.aseprite")
        self.assertIsNotNone(result)
        self.assertEqual(len(self.player.ai_list), 2)
        self.assert_existing_unchanged()

    def test_prop_resource_add_preserves_existing_npc(self):
        with (
            mock.patch.object(
                self.player, "_create_source",
                side_effect=lambda path, source_id, is_prop, kind: source_stub(source_id, kind),
            ),
            mock.patch.object(self.player, "auto_map_profile"),
            mock.patch.object(
                ase_viewer, "ensure_source_slice_analysis",
                side_effect=lambda source: self.analysis(),
            ),
        ):
            result = self.player.register_prop_source("new_prop.aseprite")
        self.assertIsNotNone(result)
        self.assertEqual(len(self.player.prop_list), 1)
        self.assert_existing_unchanged()

    def test_resource_refresh_restores_transform_even_if_callback_mutates_it(self):
        source = source_stub(0, "npc")
        profile = self.player.profiles[0]
        profile.source_idx = 0
        self.player.sources = [source]

        def mutating_refresh():
            self.existing.x = 0
            self.existing.y = 0
            self.existing.facing_right = True
            return True

        source.export_and_load = mutating_refresh
        with mock.patch.object(self.player, "auto_map_profile"):
            self.assertTrue(
                ase_viewer.activate_resource_action(
                    self.player, "refresh", 0,
                )
            )
        self.assert_existing_unchanged()

    def test_f5_refresh_path_preserves_existing_transform_and_selection(self):
        source = source_stub(0, "npc")
        self.player.profiles[0].source_idx = 0
        self.player.sources = [source]

        def mutating_refresh():
            self.existing.x = -500
            self.existing.y = -600
            self.existing.frame_idx = 0
            self.player.selected_scene_actor_key = None
            return True

        source.export_and_load = mutating_refresh
        with mock.patch.object(self.player, "auto_map_profile"):
            self.assertTrue(
                ase_viewer.refresh_all_sources_preserving_scene(self.player),
            )
        self.assert_existing_unchanged()


if __name__ == "__main__":
    unittest.main()
