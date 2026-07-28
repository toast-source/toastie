import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer
from tests.test_parallax_offset_gizmo import gizmo_player


class ParallaxOffsetUndoRedoTests(unittest.TestCase):
    def test_slider_style_edit_commits_once_and_undo_redo(self):
        player = gizmo_player()
        layer = player.bg_layers[0]
        self.assertTrue(
            ase_viewer.begin_parallax_offset_edit(
                player, layer, "slider_off_x",
            )
        )
        for value in (4.0, 8.0, 12.0):
            ase_viewer.set_parallax_layer_offset(layer, value, 0.0)
        self.assertEqual(
            getattr(player, "parallax_offset_history", []),
            [],
        )
        self.assertTrue(ase_viewer.commit_parallax_offset_edit(player))
        self.assertEqual(len(player.parallax_offset_history), 1)
        self.assertTrue(ase_viewer.undo_parallax_offset(player))
        self.assertEqual(
            ase_viewer.get_parallax_layer_offset(layer),
            (0.0, 0.0),
        )
        self.assertTrue(ase_viewer.redo_parallax_offset(player))
        self.assertEqual(
            ase_viewer.get_parallax_layer_offset(layer),
            (12.0, 0.0),
        )

    def test_y_edit_preserves_x_through_undo_redo(self):
        player = gizmo_player()
        layer = player.bg_layers[0]
        ase_viewer.set_parallax_layer_offset(layer, 9.0, 2.0)
        ase_viewer.begin_parallax_offset_edit(
            player, layer, "slider_off_y",
        )
        ase_viewer.set_parallax_layer_offset(layer, 9.0, 20.0)
        ase_viewer.commit_parallax_offset_edit(player)
        ase_viewer.undo_parallax_offset(player)
        self.assertEqual(
            ase_viewer.get_parallax_layer_offset(layer),
            (9.0, 2.0),
        )
        ase_viewer.redo_parallax_offset(player)
        self.assertEqual(
            ase_viewer.get_parallax_layer_offset(layer),
            (9.0, 20.0),
        )

    def test_shortcuts_match_ctrl_z_ctrl_y_and_ctrl_shift_z(self):
        player = gizmo_player()
        layer = player.bg_layers[0]
        ase_viewer.push_parallax_offset_history(
            player, layer, (0.0, 0.0), (10.0, 5.0), "test",
        )
        ase_viewer.set_parallax_layer_offset(layer, 10.0, 5.0)
        self.assertEqual(
            ase_viewer.handle_parallax_history_shortcut(
                player, pygame.K_z, pygame.KMOD_CTRL,
            ),
            ("undo", True),
        )
        self.assertEqual(
            ase_viewer.handle_parallax_history_shortcut(
                player, pygame.K_y, pygame.KMOD_CTRL,
            ),
            ("redo", True),
        )
        ase_viewer.undo_parallax_offset(player)
        self.assertEqual(
            ase_viewer.handle_parallax_history_shortcut(
                player,
                pygame.K_z,
                pygame.KMOD_CTRL | pygame.KMOD_SHIFT,
            ),
            ("redo", True),
        )

    def test_empty_history_and_deleted_layer_are_safe(self):
        player = gizmo_player()
        self.assertFalse(ase_viewer.undo_parallax_offset(player))
        self.assertFalse(ase_viewer.redo_parallax_offset(player))
        layer = player.bg_layers[0]
        ase_viewer.push_parallax_offset_history(
            player, layer, (0.0, 0.0), (2.0, 3.0), "deleted",
        )
        player.bg_layers.clear()
        self.assertFalse(ase_viewer.undo_parallax_offset(player))

    def test_new_edit_after_undo_clears_redo(self):
        player = gizmo_player()
        layer = player.bg_layers[0]
        ase_viewer.push_parallax_offset_history(
            player, layer, (0.0, 0.0), (5.0, 0.0), "first",
        )
        ase_viewer.set_parallax_layer_offset(layer, 5.0, 0.0)
        ase_viewer.undo_parallax_offset(player)
        self.assertEqual(len(player.parallax_offset_redo_stack), 1)
        ase_viewer.push_parallax_offset_history(
            player, layer, (0.0, 0.0), (0.0, 7.0), "second",
        )
        self.assertEqual(player.parallax_offset_redo_stack, [])

    def test_no_change_pushes_no_command(self):
        player = gizmo_player()
        layer = player.bg_layers[0]
        ase_viewer.begin_parallax_offset_edit(player, layer, "no_change")
        self.assertFalse(ase_viewer.commit_parallax_offset_edit(player))
        self.assertEqual(player.parallax_offset_history, [])

    def test_history_is_capped(self):
        player = gizmo_player()
        layer = player.bg_layers[0]
        for index in range(ase_viewer.PARALLAX_HISTORY_LIMIT + 7):
            ase_viewer.push_parallax_offset_history(
                player,
                layer,
                (float(index), 0.0),
                (float(index + 1), 0.0),
                "cap",
            )
        self.assertEqual(
            len(player.parallax_offset_history),
            ase_viewer.PARALLAX_HISTORY_LIMIT,
        )


if __name__ == "__main__":
    unittest.main()
