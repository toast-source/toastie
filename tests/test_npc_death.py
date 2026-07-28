import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


class MemorySource:
    def __init__(self, tags=None, slices=None, frames=None):
        self.id = 0
        self.name = "memory.aseprite"
        self.file_path = self.name
        self.kind = "npc"
        self.is_prop_source = False
        self.tags = tags or {"Idle": (0, 0)}
        self.tag_list = list(self.tags)
        self.tag_metadata = {}
        self.orig_w = 6
        self.orig_h = 6
        if frames is None:
            image = pygame.Surface((6, 6), pygame.SRCALPHA)
            image.fill((255, 255, 255, 255))
            frames = [{"img": image, "ox": -3, "oy": -3, "duration": 10}]
        self.frames = frames
        self.slices = slices or {}

    def get_frame(self, frame_index, zoom, facing_right):
        image = self.frames[frame_index]["img"]
        return image if facing_right else pygame.transform.flip(image, True, False)


class NpcDeathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def make_player_and_ai(self, source, profile=None):
        player = ase_viewer.AsepritePlayer(project_path="unused.json", settings_path="unused-settings.json")
        player.sources = [source]
        profile = profile or ase_viewer.AseProfile("NPC", 0, kind="npc")
        profile.mappings["IDLE"] = [[0, next(iter(source.tags))]]
        player.profiles = [profile]
        ai = ase_viewer.AseAI(player, profile, hp=2)
        ai.x = 123
        ai.y = 321
        ai.facing_right = True
        player.ai_list = [ai]
        player.target_ai_count = 1
        return player, ai

    def test_dead_loop_tag_variants_auto_map_without_overwriting_manual_mapping(self):
        variants = ["Dead_(Loop)", "Dead_Loop", "Dead Loop", "DeadLoop", "Death_(Loop)", "DEATHLOOP"]
        for tag in variants:
            with self.subTest(tag=tag):
                source = MemorySource(tags={"Idle": (0, 0), tag: (0, 0), "Dead": (0, 0)})
                player, _ = self.make_player_and_ai(source)
                profile = player.profiles[0]
                player.auto_map_profile(profile)
                self.assertEqual(profile.mappings["DEAD_LOOP"], [[0, tag]])
        source = MemorySource(tags={"ManualDeath": (0, 0), "Dead_(Loop)": (0, 0)})
        player, _ = self.make_player_and_ai(source)
        player.profiles[0].mappings["DEAD_LOOP"] = [[0, "ManualDeath"]]
        player.auto_map_profile(player.profiles[0])
        self.assertEqual(player.profiles[0].mappings["DEAD_LOOP"], [[0, "ManualDeath"]])

    def test_dead_loop_corpse_remains_frozen_and_is_not_targetable(self):
        frames = []
        for color in ((255, 0, 0, 255), (0, 255, 0, 255)):
            image = pygame.Surface((6, 6), pygame.SRCALPHA)
            image.fill(color)
            frames.append({"img": image, "ox": -3, "oy": -3, "duration": 10})
        source = MemorySource(tags={"Idle": (0, 0), "Dead_(Loop)": (0, 1)}, frames=frames)
        source.tag_metadata["Dead_(Loop)"] = {"direction": "forward", "repeat": "1"}
        player, ai = self.make_player_and_ai(source)
        player.auto_map_profile(ai.profile)
        result = player.trigger_npc_death(ai)
        self.assertEqual(result["corpse_mode"], "dead_loop")
        self.assertEqual(result["parts_mode"], "auto_alpha")
        self.assertIn(ai, player.ai_list)
        self.assertTrue(ai.is_corpse)
        self.assertTrue(any(particle.image is not None for particle in player.particles))
        position = (ai.x, ai.y)
        ai.update(500, 15)
        self.assertEqual((ai.x, ai.y), position)
        self.assertEqual(ai.frame_idx, 1)
        ai.update(500, 15)
        self.assertEqual(ai.frame_idx, 0)
        self.assertEqual(player.target_ai_count, 0)

    def test_non_loop_manual_death_mapping_stops_on_last_frame(self):
        frames = []
        for _ in range(2):
            image = pygame.Surface((6, 6), pygame.SRCALPHA)
            image.fill((255, 255, 255, 255))
            frames.append({"img": image, "ox": -3, "oy": -3, "duration": 5})
        source = MemorySource(tags={"Dead": (0, 1)}, frames=frames)
        profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        profile.mappings["DEAD"] = [[0, "Dead"]]
        player, ai = self.make_player_and_ai(source, profile)
        player.trigger_npc_death(ai)
        for _ in range(5):
            ai.update(500, 10)
        self.assertEqual(ai.frame_idx, 1)

    def test_parts_debris_precedes_auto_alpha_and_left_facing_image_is_flipped(self):
        image = pygame.Surface((6, 6), pygame.SRCALPHA)
        image.fill((0, 0, 0, 0))
        image.set_at((0, 0), (255, 0, 0, 255))
        image.set_at((1, 0), (0, 0, 255, 255))
        frames = [{"img": image, "ox": -3, "oy": -3, "duration": 10}]
        slices = {"Slice 1": [{"frame": 0, "bounds": {"x": 0, "y": 0, "w": 2, "h": 1}}]}
        source = MemorySource(tags={"Parts": (0, 0)}, slices=slices, frames=frames)
        player, ai = self.make_player_and_ai(source)
        ai.facing_right = False
        branch = player.trigger_npc_death(ai)
        self.assertEqual(branch["parts_mode"], "precise")
        self.assertNotIn(ai, player.ai_list)
        self.assertEqual(len(player.particles), 1)
        self.assertEqual(player.particles[0].image.get_at((0, 0)), pygame.Color(0, 0, 255, 255))

    def test_missing_parts_uses_auto_alpha_and_save_is_disabled(self):
        source = MemorySource()
        player, ai = self.make_player_and_ai(source)
        branch = player.trigger_npc_death(ai)
        self.assertEqual(branch["parts_mode"], "auto_alpha")
        self.assertGreaterEqual(len(player.particles), 1)
        self.assertLessEqual(len(player.particles), 24)
        self.assertFalse(ase_viewer.evaluate_slice_export(source)["enabled"])

    def test_source_removal_removes_corpse(self):
        source = MemorySource(tags={"Dead_(Loop)": (0, 0)})
        player, ai = self.make_player_and_ai(source)
        player.auto_map_profile(ai.profile)
        player.trigger_npc_death(ai)
        player.remove_source_by_index(0)
        self.assertNotIn(ai, player.ai_list)


if __name__ == "__main__":
    unittest.main()
