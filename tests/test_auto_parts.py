import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


class AutoPartsSource:
    def __init__(self, width, height, draw):
        self.source_revision = 1
        self.slice_analysis_revision = -1
        self.slice_export_analysis = None
        self.export_status = {}
        self.tags = {"Idle": (0, 0)}
        self.tag_list = ["Idle"]
        self.tag_metadata = {}
        self.slices = {}
        self.orig_w = width
        self.orig_h = height
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        draw(image)
        self.frames = [{"img": image, "ox": -width // 2, "oy": -height // 2, "duration": 10}]

    def get_frame(self, frame_index, zoom, facing_right):
        image = self.frames[frame_index]["img"]
        return image if facing_right else pygame.transform.flip(image, True, False)


class AutoPartsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_medium_silhouette_is_deterministic_trimmed_and_not_fixed_three_by_three(self):
        def draw(image):
            pygame.draw.ellipse(image, (255, 255, 255, 255), (8, 4, 48, 56))

        source = AutoPartsSource(64, 64, draw)
        first = ase_viewer.build_auto_alpha_parts(source, 0)
        second = ase_viewer.build_auto_alpha_parts(source, 0)
        self.assertIs(first, second)
        self.assertEqual(first["mode"], "auto_alpha")
        self.assertGreater(len(first["pieces"]), 9)
        self.assertLessEqual(len(first["pieces"]), 24)
        self.assertTrue(all(piece["image"].get_bounding_rect().size == piece["image"].get_size() for piece in first["pieces"]))
        self.assertTrue(all(piece["image"].get_width() < 22 and piece["image"].get_height() < 22 for piece in first["pieces"]))

    def test_tiny_opaque_source_produces_at_least_one_but_not_too_many_parts(self):
        source = AutoPartsSource(8, 8, lambda image: image.fill((255, 255, 255, 255), (2, 2, 3, 3)))
        plan = ase_viewer.build_auto_alpha_parts(source, 0)
        self.assertGreaterEqual(len(plan["pieces"]), 1)
        self.assertLessEqual(len(plan["pieces"]), 4)
        self.assertTrue(all(ase_viewer._alpha_pixel_count(piece["image"]) > 0 for piece in plan["pieces"]))

    def test_transparent_source_allows_only_colored_fallback(self):
        source = AutoPartsSource(32, 32, lambda image: None)
        plan = ase_viewer.build_auto_alpha_parts(source, 0)
        self.assertEqual(plan["mode"], "colored_fallback")
        self.assertEqual(plan["pieces"], [])

    def test_sparse_pixels_fall_back_to_one_cropped_image_part(self):
        def draw(image):
            for y in (0, 16, 32, 48):
                for x in (0, 16, 32, 48):
                    image.set_at((x, y), (255, 255, 255, 255))

        source = AutoPartsSource(64, 64, draw)
        plan = ase_viewer.build_auto_alpha_parts(source, 0)
        self.assertEqual(plan["mode"], "single_image_fallback")
        self.assertEqual(len(plan["pieces"]), 1)
        self.assertEqual(plan["pieces"][0]["image"].get_size(), (49, 49))
        self.assertEqual(ase_viewer._alpha_pixel_count(plan["pieces"][0]["image"]), 16)

    def test_auto_parts_survive_update_and_are_rendered(self):
        source = AutoPartsSource(64, 64, lambda image: pygame.draw.ellipse(image, (255, 255, 255, 255), (8, 4, 48, 56)))
        player = ase_viewer.AsepritePlayer(project_path="unused.json", settings_path="unused-settings.json")
        player.sources = [source]
        profile = ase_viewer.AseProfile("NoPartsEnemy", 0, kind="npc")
        profile.mappings["IDLE"] = [[0, "Idle"]]
        ai = ase_viewer.AseAI(player, profile)
        ai.x, ai.y = 400, 500
        player.ai_list = [ai]
        player.cam_follow = False
        player.cam_x, player.cam_y = ai.x, ai.y
        self.assertEqual(player.trigger_npc_death(ai)["parts_mode"], "auto_alpha")
        created = len(player.particles)
        self.assertGreater(created, 0)
        player.update(ase_viewer._SmokeKeys(), 500, 16.6)
        self.assertEqual(len(player.particles), created)
        screen = pygame.Surface((800, 570))
        player.draw(screen, 800, 570)
        self.assertTrue(all(particle.cached_surface is not None for particle in player.particles))


if __name__ == "__main__":
    unittest.main()
