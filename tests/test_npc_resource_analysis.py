import os
import unittest
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


class AnalysisSource:
    def __init__(self, include_parts=True, include_particles=True):
        self.id = 0
        self.name = "npc.aseprite"
        self.file_path = self.name
        self.kind = "npc"
        self.is_prop_source = False
        self.source_revision = 1
        self.slice_analysis_revision = -1
        self.slice_export_analysis = None
        self.export_status = {"enabled": False, "reason": "not analyzed"}
        self.orig_w = self.orig_h = 4
        part = pygame.Surface((4, 4), pygame.SRCALPHA)
        particle = pygame.Surface((4, 4), pygame.SRCALPHA)
        if include_parts:
            part.set_at((0, 0), (255, 0, 0, 255))
        if include_particles:
            particle.set_at((2, 0), (0, 255, 0, 255))
        self.frames = [
            {"img": part, "ox": -2, "oy": -2, "duration": 10},
            {"img": particle, "ox": -2, "oy": -2, "duration": 10},
        ]
        self.tags = {"Idle": (0, 0), "Parts": (0, 0), "Particles": (1, 1)}
        self.tag_list = list(self.tags)
        self.tag_metadata = {}
        self.slices = {
            "Body piece": [{"frame": 0, "bounds": {"x": 0, "y": 0, "w": 2, "h": 2}}],
            "FX piece": [{"frame": 0, "bounds": {"x": 2, "y": 0, "w": 2, "h": 2}}],
        }

    def get_frame(self, frame_index, zoom, facing_right):
        image = self.frames[frame_index]["img"]
        return image if facing_right else pygame.transform.flip(image, True, False)

    def clear_cache(self):
        pass

    def check_for_reload(self):
        return False


class NpcResourceAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def make_player(self, source):
        player = ase_viewer.AsepritePlayer(project_path="unused.json", settings_path="unused-settings.json")
        player.sources = [source]
        return player

    def test_npc_registration_analyzes_before_spawn_and_reuses_one_source_cache(self):
        source = AnalysisSource()
        player = self.make_player(source)
        with mock.patch(
            "ase_viewer._classify_export_slices_uncached",
            wraps=ase_viewer._classify_export_slices_uncached,
        ) as classify:
            player.add_profile("NPC", 0, is_npc=True)
            analysis = source.slice_export_analysis
            self.assertEqual(source.kind, "npc")
            self.assertEqual(len(analysis["valid_parts_slices"]), 1)
            self.assertEqual(len(analysis["valid_particle_slices"]), 1)
            self.assertEqual(classify.call_count, 1)
            second = ase_viewer.AseAI(player, player.profiles[-1])
            self.assertIs(source.slice_export_analysis, analysis)
            self.assertEqual(classify.call_count, 1)
            self.assertIsNotNone(second)

    def test_runtime_and_auto_save_share_cache_while_name_mode_cannot_change_it(self):
        source = AnalysisSource()
        analysis = ase_viewer.ensure_source_slice_analysis(source)
        auto = ase_viewer.classify_export_slices(source, mode="auto")
        self.assertIs(auto["items"][0], analysis["valid_parts_slices"][0])
        before = source.slice_export_analysis
        ase_viewer.classify_export_slices(source, mode="name")
        self.assertIs(source.slice_export_analysis, before)
        self.assertEqual(
            [(item["group"], item["slice_name"]) for item in auto["items"]],
            [
                ("Parts", "Body piece"),
                ("Particles", "FX piece"),
            ],
        )

    def test_npc_custom_particles_use_auto_analysis_and_empty_particles_fall_back(self):
        source = AnalysisSource()
        player = self.make_player(source)
        created = player.create_custom_hit_particles(source, 10, 20)
        self.assertEqual(created, 1)
        self.assertIsNotNone(player.particles[-1].image)

        empty_source = AnalysisSource(include_particles=False)
        empty_player = self.make_player(empty_source)
        self.assertEqual(empty_player.create_custom_hit_particles(empty_source, 10, 20), 0)
        self.assertFalse(empty_source.slice_export_analysis["has_valid_particles"])

    def test_revision_refresh_replaces_cache_and_failed_export_preserves_it(self):
        source = AnalysisSource()
        old_analysis = ase_viewer.ensure_source_slice_analysis(source)
        source.source_revision += 1
        source.frames[0]["img"].fill((0, 0, 0, 0))
        refreshed = ase_viewer.ensure_source_slice_analysis(source)
        self.assertIsNot(refreshed, old_analysis)
        self.assertFalse(refreshed["has_valid_parts"])

        real_source = ase_viewer.AseSource.__new__(ase_viewer.AseSource)
        real_source.file_path = "memory.aseprite"
        real_source.name = "memory.aseprite"
        real_source.frames = source.frames
        real_source.tags = source.tags
        real_source.tag_metadata = {}
        real_source.slices = source.slices
        real_source.tag_list = list(source.tags)
        real_source.orig_w = real_source.orig_h = 4
        real_source.layers = []
        real_source.visible_layer_keys = set()
        real_source.visible_layers = set()
        real_source.source_revision = source.source_revision
        real_source.slice_analysis_revision = source.source_revision
        real_source.slice_export_analysis = refreshed
        real_source.export_status = {"enabled": False, "reason": refreshed["reason"]}
        with mock.patch("ase_viewer.export_aseprite", side_effect=ase_viewer.AsepriteError("failure")):
            self.assertFalse(real_source.export_and_load())
        self.assertIs(real_source.slice_export_analysis, refreshed)
        self.assertEqual(real_source.source_revision, source.source_revision)

    def test_dead_loop_and_cached_parts_execute_together(self):
        source = AnalysisSource()
        source.tags["Dead_(Loop)"] = (0, 0)
        source.tag_list = list(source.tags)
        player = self.make_player(source)
        profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        player.profiles = [profile]
        player.auto_map_profile(profile)
        ai = ase_viewer.AseAI(player, profile)
        player.ai_list = [ai]
        result = player.trigger_npc_death(ai)
        self.assertEqual(result["corpse_mode"], "dead_loop")
        self.assertEqual(result["parts_mode"], "precise")
        self.assertEqual(result["created"], 1)
        self.assertTrue(ai.is_corpse)
        self.assertEqual(len(player.particles), 1)

    def test_default_slice_names_create_four_precise_parts_without_grid(self):
        source = AnalysisSource()
        source.frames[0]["img"].fill((0, 0, 0, 0))
        source.slices = {}
        for index in range(4):
            source.frames[0]["img"].set_at((index, 0), (255, 0, 0, 255))
            source.slices[f"Slice {index + 1}"] = [{
                "frame": 0,
                "bounds": {"x": index, "y": 0, "w": 1, "h": 1},
            }]
        player = self.make_player(source)
        profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        player.profiles = [profile]
        ai = ase_viewer.AseAI(player, profile)
        player.ai_list = [ai]
        with mock.patch.object(player, "create_auto_alpha_debris", wraps=player.create_auto_alpha_debris) as auto_parts:
            self.assertEqual(player.trigger_npc_death(ai)["parts_mode"], "precise")
        self.assertEqual(len(source.slice_export_analysis["valid_parts_slices"]), 4)
        self.assertEqual(len(player.particles), 4)
        auto_parts.assert_not_called()

    def test_transparent_parts_slice_uses_auto_alpha_and_disables_save(self):
        source = AnalysisSource(include_parts=False)
        source.frames[0]["img"].set_at((2, 2), (255, 255, 255, 255))
        player = self.make_player(source)
        profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        player.profiles = [profile]
        ai = ase_viewer.AseAI(player, profile)
        player.ai_list = [ai]
        self.assertIn(
            player.trigger_npc_death(ai)["parts_mode"],
            {"auto_alpha", "single_image_fallback"},
        )
        self.assertFalse(source.slice_export_analysis["has_valid_parts"])
        self.assertFalse(ase_viewer.slice_export_availability(source)["enabled"])

    def test_precise_parts_creation_failure_still_uses_auto_alpha(self):
        source = AnalysisSource()
        source.frames[0]["img"].fill((255, 255, 255, 255))
        player = self.make_player(source)
        profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        player.profiles = [profile]
        ai = ase_viewer.AseAI(player, profile)
        player.ai_list = [ai]
        with mock.patch.object(player, "create_precise_parts_from_analysis", return_value=0):
            self.assertEqual(player.trigger_npc_death(ai)["parts_mode"], "auto_alpha")

    def test_status_data_reports_precise_and_auto_alpha_modes_with_corpse_notice(self):
        source = AnalysisSource()
        profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        precise = ase_viewer.npc_slice_status_data(profile, [source])
        self.assertEqual((precise["parts"], precise["particles"]), (1, 1))
        self.assertEqual(precise["death"], "Remove + Precise Parts 1")
        self.assertEqual(precise["save"], "Available")

        empty_parts = AnalysisSource(include_parts=False)
        fallback = ase_viewer.npc_slice_status_data(profile, [empty_parts])
        self.assertEqual(fallback["parts"], 0)
        self.assertEqual(fallback["particles"], 1)
        self.assertEqual(fallback["death"], "Remove + Colored Fallback")
        self.assertEqual(fallback["save"], "Disabled — No valid Parts")

        source.tags["Dead_(Loop)"] = (0, 0)
        profile.mappings["DEAD_LOOP"] = [[0, "Dead_(Loop)"]]
        corpse = ase_viewer.npc_slice_status_data(profile, [source])
        self.assertEqual(corpse["death"], "Dead Loop + Precise Parts 1")
        self.assertIn("independently", corpse["reason"].lower())

    def test_precise_parts_survive_update_and_enter_render_path(self):
        source = AnalysisSource()
        player = self.make_player(source)
        profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        profile.mappings["IDLE"] = [[0, "Idle"]]
        player.profiles = [profile]
        ai = ase_viewer.AseAI(player, profile)
        ai.x, ai.y = 400, 500
        player.ai_list = [ai]
        player.cam_follow = False
        player.cam_x, player.cam_y = ai.x, ai.y
        self.assertEqual(player.trigger_npc_death(ai)["parts_mode"], "precise")
        self.assertNotIn(ai, player.ai_list)
        self.assertEqual(len(player.particles), 1)
        lifetime = player.particles[0].lifetime
        player.update(ase_viewer._SmokeKeys(), 500, 16.6)
        self.assertEqual(len(player.particles), 1)
        self.assertLess(player.particles[0].lifetime, lifetime)
        screen = pygame.Surface((800, 570))
        player.draw(screen, 800, 570)
        self.assertIsNotNone(player.particles[0].cached_surface)

    def test_auto_alpha_parts_survive_update_and_enter_render_path(self):
        source = AnalysisSource()
        source.tags = {"Idle": (0, 0)}
        source.tag_list = ["Idle"]
        source.slices = {}
        source.frames[0]["img"].fill((255, 255, 255, 255))
        player = self.make_player(source)
        profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        profile.mappings["IDLE"] = [[0, "Idle"]]
        player.profiles = [profile]
        ai = ase_viewer.AseAI(player, profile)
        ai.x, ai.y = 400, 500
        player.ai_list = [ai]
        player.cam_follow = False
        player.cam_x, player.cam_y = ai.x, ai.y
        self.assertEqual(player.trigger_npc_death(ai)["parts_mode"], "auto_alpha")
        expected = len(player.particles)
        self.assertGreaterEqual(expected, 1)
        self.assertLessEqual(expected, 24)
        player.update(ase_viewer._SmokeKeys(), 500, 16.6)
        self.assertEqual(len(player.particles), expected)
        screen = pygame.Surface((800, 570))
        player.draw(screen, 800, 570)
        self.assertTrue(all(particle.cached_surface is not None for particle in player.particles))


if __name__ == "__main__":
    unittest.main()
