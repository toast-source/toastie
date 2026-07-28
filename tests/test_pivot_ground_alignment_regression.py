import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


def trimmed_source():
    image = pygame.Surface((12, 20), pygame.SRCALPHA)
    image.fill((255, 255, 255, 255))
    source = SimpleNamespace(
        id=0, name="SporeHeart.aseprite", file_path="SporeHeart.aseprite",
        kind="generic", is_prop_source=False,
        orig_w=64, orig_h=64,
        frames=[{"img": image, "ox": -6, "oy": 5, "duration": 100}],
        tags={"Idle": (0, 0)}, tag_list=["Idle"], slices={},
        source_revision=1, slice_analysis_revision=None,
        slice_export_analysis=None, clear_cache=lambda: None,
    )
    source.get_frame = lambda index, zoom, facing: pygame.transform.scale(
        image, (round(image.get_width() * zoom), round(image.get_height() * zoom)),
    )
    return source


class PivotGroundAlignmentRegressionTests(unittest.TestCase):
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
        self.source = trimmed_source()
        self.player.sources = [self.source]
        self.player.x, self.player.y = 80, 100
        self.player.zoom = 1.0
        self.player.show_hitboxes = False
        self.analysis = mock.patch.object(
            ase_viewer, "ensure_source_slice_analysis",
            return_value={"valid_parts_slices": [], "valid_particle_slices": []},
        )
        self.analysis.start()

    def tearDown(self):
        self.analysis.stop()
        self.temp_dir.cleanup()

    def test_profile_uses_visible_bottom_as_stable_ground_anchor(self):
        profile = ase_viewer.AseProfile("SporeHeart", 0, kind="npc")
        self.player.profiles = [profile]
        self.player.auto_map_profile(profile)
        self.assertEqual(profile.ground_offset_y, -25)
        npc = self.player.spawn_npc_profile(0)
        self.assertEqual(
            (npc.x, npc.y),
            (180, self.player.world_ground_y),
        )
        npc.y = 100
        screen = pygame.Surface((240, 160), pygame.SRCALPHA)
        self.player.draw_sprite(
            screen, npc.x, npc.y, 0, 0, True,
            0, 0, 0, 0, entity=npc,
        )
        self.assertEqual(screen.get_bounding_rect().bottom, 100)

    def test_role_profiles_share_alignment_without_spawning_partner(self):
        with mock.patch.object(
            self.player, "auto_map_profile",
            wraps=self.player.auto_map_profile,
        ):
            partner = ase_viewer.assign_resource_role(
                self.player, 0, "partner",
            )
            npc = ase_viewer.assign_resource_role(self.player, 0, "npc")
            player = ase_viewer.assign_resource_role(self.player, 0, "player")
        self.assertIsNone(partner["instance"])
        self.assertEqual(self.player.partner_list, [])
        self.assertEqual(
            {
                partner["profile"].ground_offset_y,
                npc["profile"].ground_offset_y,
                player["profile"].ground_offset_y,
            },
            {-25},
        )
        self.assertEqual(
            npc["instance"].y,
            self.player.world_ground_y,
        )

    def test_explicit_aseprite_pivot_slice_takes_precedence(self):
        self.source.slices = {
            "Ground Pivot": [{
                "frame": 0,
                "bounds": {"x": 0, "y": 40, "w": 8, "h": 8},
                "pivot": {"x": 4, "y": 6},
            }],
        }
        delattr(self.source, "ground_offset_y") if hasattr(self.source, "ground_offset_y") else None
        self.assertEqual(
            ase_viewer.source_ground_alignment_offset(self.source),
            32 - 46,
        )


if __name__ == "__main__":
    unittest.main()
