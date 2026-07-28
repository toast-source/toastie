import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer
from tests.test_npc_death import MemorySource


class PropDeathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def make_prop(self, source):
        player = ase_viewer.AsepritePlayer(project_path="unused.json", settings_path="unused-settings.json")
        player.sources = [source]
        profile = ase_viewer.AseProfile("PROP", 0, kind="prop")
        player.profiles = [profile]
        player.auto_map_profile(profile)
        prop = ase_viewer.AseAI(player, profile, is_prop=True, hp=3)
        prop.x, prop.y = 200, 500
        player.prop_list = [prop]
        return player, prop

    def test_dead_loop_prop_remains_without_debris_and_cannot_die_twice(self):
        source = MemorySource(tags={"Idle": (0, 0), "Dead_(Loop)": (0, 0)})
        player, prop = self.make_prop(source)
        self.assertEqual(player.trigger_prop_death(prop), "corpse_loop")
        self.assertIn(prop, player.prop_list)
        self.assertTrue(prop.is_corpse)
        self.assertFalse(player.particles)
        self.assertIsNone(player.trigger_prop_death(prop))
        self.assertFalse(player.particles)

    def test_dead_prop_plays_once_and_stops_on_last_frame(self):
        frames = []
        for color in ((255, 0, 0, 255), (0, 255, 0, 255)):
            image = pygame.Surface((6, 6), pygame.SRCALPHA)
            image.fill(color)
            frames.append({"img": image, "ox": -3, "oy": -3, "duration": 5})
        source = MemorySource(tags={"Idle": (0, 0), "Dead": (0, 1)}, frames=frames)
        player, prop = self.make_prop(source)
        self.assertEqual(player.trigger_prop_death(prop), "corpse_dead")
        for _ in range(4):
            prop.update(500, 10)
        self.assertEqual(prop.frame_idx, 1)
        self.assertIn(prop, player.prop_list)

    def test_airborne_prop_corpse_falls_and_lands(self):
        source = MemorySource(tags={"Idle": (0, 0), "Death": (0, 0)})
        player, prop = self.make_prop(source)
        prop.y = 100
        self.assertEqual(player.trigger_prop_death(prop), "corpse_dead")
        for _ in range(120):
            prop.update(500, 16.6)
            if prop.grounded:
                break
        self.assertTrue(prop.grounded)
        self.assertIn(prop.y, [platform.top for platform in player.platforms] + [500])
        self.assertEqual(prop.vy, 0)

    def test_prop_without_death_tag_keeps_existing_precise_parts(self):
        image = pygame.Surface((6, 6), pygame.SRCALPHA)
        image.set_at((0, 0), (255, 255, 255, 255))
        source = MemorySource(
            tags={"Idle": (0, 0), "Parts": (0, 0)},
            slices={"Slice 1": [{"frame": 0, "bounds": {"x": 0, "y": 0, "w": 1, "h": 1}}]},
            frames=[{"img": image, "ox": -3, "oy": -3, "duration": 10}],
        )
        player, prop = self.make_prop(source)
        self.assertEqual(player.trigger_prop_death(prop), "parts")
        self.assertNotIn(prop, player.prop_list)
        self.assertEqual(len(player.particles), 1)


if __name__ == "__main__":
    unittest.main()
