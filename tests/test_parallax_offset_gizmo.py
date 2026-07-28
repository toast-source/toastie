import os
import json
import tempfile
import unittest
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


def gizmo_player(**overrides):
    image = pygame.Surface((80, 40), pygame.SRCALPHA)
    values = {
        "bg_layers": [{
            "path": "background.png",
            "off_x": 0.0,
            "off_y": 0.0,
            "parallax": 1.0,
            "img": image,
            "cached_bg": image,
            "needs_update": False,
        }],
        "active_bg_layer": 0,
        "parallax_gizmo_enabled": False,
        "parallax_gizmo_dragging": False,
        "parallax_gizmo_drag_layer": None,
        "parallax_gizmo_drag_last": None,
        "parallax_gizmo_drag_dirty": False,
        "zoom": 2.0,
        "spawn_x": 400.0,
        "spawn_y": 300.0,
        "cam_x": 400.0,
        "cam_y": 300.0,
        "x": 100.0,
        "y": 500.0,
        "vx": 0.0,
        "vy": 0.0,
        "ai_list": [],
        "prop_list": [],
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class ParallaxOffsetGizmoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_default_off_and_localized_labels(self):
        player = gizmo_player()
        self.assertIsNone(
            ase_viewer.build_parallax_gizmo_rect(player, 700, 650)
        )
        self.assertEqual(
            ase_viewer.tr("ui.parallax_gizmo", language="ko"),
            "패럴렉스 기즈모",
        )
        self.assertEqual(
            ase_viewer.tr("ui.parallax_gizmo", language="en"),
            "Parallax Gizmo",
        )
        self.assertTrue(ase_viewer.set_parallax_gizmo_enabled(player, True))
        self.assertFalse(ase_viewer.set_parallax_gizmo_enabled(player, False))

    def test_selected_layer_draws_handle_inside_play_view(self):
        player = gizmo_player(parallax_gizmo_enabled=True)
        rect = ase_viewer.build_parallax_gizmo_rect(player, 700, 650)
        self.assertIsNotNone(rect)
        self.assertTrue(
            pygame.Rect(0, ase_viewer.TOP_UI_HEIGHT, 700, 650).contains(rect)
        )
        surface = pygame.Surface((1000, 720), pygame.SRCALPHA)
        self.assertEqual(
            ase_viewer.draw_parallax_offset_gizmo(
                surface, player, 700, 650,
            ),
            rect,
        )
        self.assertLess(rect.right, 700)

    def test_drag_updates_same_offset_fields_in_intuitive_direction(self):
        player = gizmo_player(parallax_gizmo_enabled=True)
        rect = ase_viewer.build_parallax_gizmo_rect(player, 700, 650)
        camera_before = (player.cam_x, player.cam_y)
        actor_before = (player.x, player.y, player.vx, player.vy)
        source_path = player.bg_layers[0]["path"]
        self.assertTrue(
            ase_viewer.begin_parallax_gizmo_drag(
                player, rect.center, 700, 650,
            )
        )
        self.assertTrue(
            ase_viewer.update_parallax_gizmo_drag(
                player, (rect.centerx + 20, rect.centery + 10),
            )
        )
        self.assertEqual(player.bg_layers[0]["off_x"], 10.0)
        self.assertEqual(player.bg_layers[0]["off_y"], 5.0)
        self.assertTrue(ase_viewer.end_parallax_gizmo_drag(player))
        self.assertEqual((player.cam_x, player.cam_y), camera_before)
        self.assertEqual(
            (player.x, player.y, player.vx, player.vy),
            actor_before,
        )
        self.assertEqual(player.bg_layers[0]["path"], source_path)

    def test_slider_field_change_moves_gizmo(self):
        player = gizmo_player(parallax_gizmo_enabled=True)
        before = ase_viewer.build_parallax_gizmo_rect(player, 700, 650)
        ase_viewer.set_parallax_layer_offset(
            player.bg_layers[0], 15.0, -10.0,
        )
        after = ase_viewer.build_parallax_gizmo_rect(player, 700, 650)
        self.assertEqual(after.centerx - before.centerx, 30)
        self.assertEqual(after.centery - before.centery, -20)

    def test_off_invalid_hidden_and_outside_handle_are_safe(self):
        player = gizmo_player()
        original = ase_viewer.get_parallax_layer_offset(player.bg_layers[0])
        self.assertFalse(
            ase_viewer.begin_parallax_gizmo_drag(
                player, (100, 100), 700, 650,
            )
        )
        self.assertEqual(
            ase_viewer.get_parallax_layer_offset(player.bg_layers[0]),
            original,
        )
        player.parallax_gizmo_enabled = True
        player.bg_layers[0]["visible"] = False
        self.assertIsNone(
            ase_viewer.build_parallax_gizmo_rect(player, 700, 650)
        )
        player.bg_layers = []
        self.assertIsNone(
            ase_viewer.build_parallax_gizmo_rect(player, 700, 650)
        )

    def test_missing_image_and_extreme_zoom_are_safe(self):
        player = gizmo_player(parallax_gizmo_enabled=True, zoom=0.0)
        player.bg_layers[0]["img"] = None
        player.bg_layers[0]["cached_bg"] = None
        self.assertIsNone(
            ase_viewer.build_parallax_gizmo_rect(player, 700, 650)
        )
        self.assertEqual(
            ase_viewer.parallax_offset_delta_from_screen(10, -4, 0),
            (10.0, -4.0),
        )

    def test_existing_settings_persist_offsets_but_not_session_toggle(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_path = os.path.join(temp_dir, "settings.json")
            player = ase_viewer.AsepritePlayer(settings_path=settings_path)
            player.bg_layers = [{
                "path": "",
                "off_x": 12.5,
                "off_y": -8.0,
                "zoom": 1.0,
                "alpha": 255,
                "parallax": 0.5,
                "loop_x": False,
            }]
            player.parallax_gizmo_enabled = True
            player.save_settings()
            with open(settings_path, "r", encoding="utf-8") as saved_file:
                saved = json.load(saved_file)
        self.assertEqual(saved["bg"]["layers"][0]["off_x"], 12.5)
        self.assertEqual(saved["bg"]["layers"][0]["off_y"], -8.0)
        self.assertNotIn("parallax_gizmo_enabled", saved)
        self.assertNotIn("parallax_offset_history", saved)
        self.assertNotIn("parallax_offset_redo_stack", saved)


if __name__ == "__main__":
    unittest.main()
