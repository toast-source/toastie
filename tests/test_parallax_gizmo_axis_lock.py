import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer
from tests.test_parallax_offset_gizmo import gizmo_player


class ParallaxGizmoAxisLockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def enabled_player(self):
        return gizmo_player(parallax_gizmo_enabled=True)

    def drag(self, player, axis, dx, dy, shift=False):
        handles = ase_viewer.parallax_gizmo_handle_rects(player, 700, 650)
        start = handles[axis].center
        self.assertEqual(
            ase_viewer.parallax_gizmo_hit_axis(
                player, start, 700, 650,
            ),
            axis,
        )
        self.assertTrue(
            ase_viewer.begin_parallax_gizmo_drag(
                player, start, 700, 650,
            )
        )
        self.assertTrue(
            ase_viewer.update_parallax_gizmo_drag(
                player, (start[0] + dx, start[1] + dy), shift,
            )
        )
        return ase_viewer.end_parallax_gizmo_drag(player)

    def test_handle_hit_test_distinguishes_free_x_and_y(self):
        player = self.enabled_player()
        handles = ase_viewer.parallax_gizmo_handle_rects(player, 700, 650)
        self.assertEqual(set(handles), {"free", "x", "y"})
        for first_name, first_rect in handles.items():
            for second_name, second_rect in handles.items():
                if first_name != second_name:
                    self.assertFalse(first_rect.colliderect(second_rect))

    def test_free_handle_changes_both_axes(self):
        player = self.enabled_player()
        self.assertTrue(self.drag(player, "free", 20, 10))
        self.assertEqual(
            ase_viewer.get_parallax_layer_offset(player.bg_layers[0]),
            (10.0, 5.0),
        )

    def test_x_handle_changes_only_x(self):
        player = self.enabled_player()
        self.assertTrue(self.drag(player, "x", 20, 14))
        self.assertEqual(
            ase_viewer.get_parallax_layer_offset(player.bg_layers[0]),
            (10.0, 0.0),
        )

    def test_y_handle_changes_only_y(self):
        player = self.enabled_player()
        self.assertTrue(self.drag(player, "y", 18, 20))
        self.assertEqual(
            ase_viewer.get_parallax_layer_offset(player.bg_layers[0]),
            (0.0, 10.0),
        )

    def test_shift_free_drag_locks_dominant_axis(self):
        player_x = self.enabled_player()
        self.assertTrue(self.drag(player_x, "free", 30, 8, shift=True))
        self.assertEqual(
            ase_viewer.get_parallax_layer_offset(player_x.bg_layers[0]),
            (15.0, 0.0),
        )
        player_y = self.enabled_player()
        self.assertTrue(self.drag(player_y, "free", 6, 28, shift=True))
        self.assertEqual(
            ase_viewer.get_parallax_layer_offset(player_y.bg_layers[0]),
            (0.0, 14.0),
        )

    def test_releasing_shift_returns_free_drag_in_same_command(self):
        player = self.enabled_player()
        start = ase_viewer.parallax_gizmo_handle_rects(
            player, 700, 650,
        )["free"].center
        ase_viewer.begin_parallax_gizmo_drag(player, start, 700, 650)
        ase_viewer.update_parallax_gizmo_drag(
            player, (start[0] + 20, start[1] + 8), shift_pressed=True,
        )
        self.assertEqual(
            ase_viewer.get_parallax_layer_offset(player.bg_layers[0]),
            (10.0, 0.0),
        )
        ase_viewer.update_parallax_gizmo_drag(
            player, (start[0] + 20, start[1] + 8), shift_pressed=False,
        )
        self.assertEqual(
            ase_viewer.get_parallax_layer_offset(player.bg_layers[0]),
            (10.0, 4.0),
        )
        self.assertTrue(ase_viewer.end_parallax_gizmo_drag(player))
        self.assertEqual(len(player.parallax_offset_history), 1)

    def test_gizmo_drag_without_motion_pushes_no_command(self):
        player = self.enabled_player()
        start = ase_viewer.parallax_gizmo_handle_rects(
            player, 700, 650,
        )["free"].center
        self.assertTrue(
            ase_viewer.begin_parallax_gizmo_drag(
                player, start, 700, 650,
            )
        )
        self.assertFalse(ase_viewer.end_parallax_gizmo_drag(player))
        self.assertEqual(
            getattr(player, "parallax_offset_history", []),
            [],
        )

    def test_layer_change_during_drag_cancels_and_restores(self):
        player = self.enabled_player()
        second = dict(player.bg_layers[0])
        player.bg_layers.append(second)
        start = ase_viewer.parallax_gizmo_handle_rects(
            player, 700, 650,
        )["free"].center
        ase_viewer.begin_parallax_gizmo_drag(player, start, 700, 650)
        ase_viewer.update_parallax_gizmo_drag(
            player, (start[0] + 20, start[1] + 10),
        )
        player.active_bg_layer = 1
        self.assertTrue(
            ase_viewer.update_parallax_gizmo_drag(
                player, (start[0] + 30, start[1] + 20),
            )
        )
        self.assertEqual(
            ase_viewer.get_parallax_layer_offset(player.bg_layers[0]),
            (0.0, 0.0),
        )
        self.assertFalse(player.parallax_gizmo_dragging)

    def test_multiple_moves_create_one_history_command(self):
        player = self.enabled_player()
        start = ase_viewer.parallax_gizmo_handle_rects(
            player, 700, 650,
        )["free"].center
        ase_viewer.begin_parallax_gizmo_drag(player, start, 700, 650)
        for dx, dy in ((4, 2), (12, 6), (20, 10)):
            ase_viewer.update_parallax_gizmo_drag(
                player, (start[0] + dx, start[1] + dy),
            )
        self.assertEqual(
            getattr(player, "parallax_offset_history", []),
            [],
        )
        self.assertTrue(ase_viewer.end_parallax_gizmo_drag(player))
        self.assertEqual(len(player.parallax_offset_history), 1)

    def test_turning_gizmo_off_cancels_and_restores_drag(self):
        player = self.enabled_player()
        start = ase_viewer.parallax_gizmo_handle_rects(
            player, 700, 650,
        )["free"].center
        ase_viewer.begin_parallax_gizmo_drag(player, start, 700, 650)
        ase_viewer.update_parallax_gizmo_drag(
            player, (start[0] + 20, start[1] + 10),
        )
        self.assertFalse(
            ase_viewer.set_parallax_gizmo_enabled(player, False)
        )
        self.assertEqual(
            ase_viewer.get_parallax_layer_offset(player.bg_layers[0]),
            (0.0, 0.0),
        )
        self.assertEqual(
            getattr(player, "parallax_offset_history", []),
            [],
        )


if __name__ == "__main__":
    unittest.main()
