import unittest
from types import SimpleNamespace

import pygame

import ase_viewer


def corpse_actor(x=120.0, y=200.0, platforms=None, world_ground=500.0):
    master = SimpleNamespace(
        platforms=list(platforms or []),
        world_ground_y=world_ground,
    )
    return SimpleNamespace(
        master=master, x=x, y=y, vx=8.0, vy=-12.0,
        grounded=False, is_corpse=True, is_prop=False,
    )


class CorpseGroundSnapTests(unittest.TestCase):
    def test_airborne_and_knockback_corpse_snaps_to_platform(self):
        actor = corpse_actor(
            platforms=[pygame.Rect(80, 350, 120, 20)],
        )
        original_x = actor.x
        self.assertTrue(ase_viewer._snap_npc_corpse_to_ground(actor))
        self.assertEqual((actor.x, actor.y), (original_x, 350.0))
        self.assertEqual((actor.vx, actor.vy), (0, 0))
        self.assertTrue(actor.grounded)

    def test_falling_corpse_without_platform_uses_world_ground(self):
        actor = corpse_actor(y=250, world_ground=620)
        actor.vy = 15
        ase_viewer._snap_npc_corpse_to_ground(actor)
        self.assertEqual(actor.y, 620)
        self.assertEqual(actor.vy, 0)

    def test_nearest_platform_below_current_position_wins(self):
        actor = corpse_actor(
            y=100,
            platforms=[
                pygame.Rect(80, 420, 120, 20),
                pygame.Rect(80, 280, 120, 20),
            ],
        )
        self.assertEqual(
            ase_viewer._find_ground_y_below_actor(actor), 280.0,
        )

    def test_platform_above_actor_is_not_used(self):
        actor = corpse_actor(
            y=400,
            platforms=[pygame.Rect(80, 300, 120, 20)],
        )
        self.assertEqual(
            ase_viewer._find_ground_y_below_actor(actor), 500.0,
        )

    def test_grounded_corpse_is_idempotent_and_does_not_change_spawn(self):
        actor = corpse_actor(y=350, platforms=[pygame.Rect(80, 350, 120, 20)])
        actor.grounded = True
        actor.vx = actor.vy = 0
        actor.spawn_y = 777
        before = (actor.x, actor.y, actor.spawn_y)
        self.assertFalse(ase_viewer._stabilize_corpse_grounding(actor))
        self.assertEqual((actor.x, actor.y, actor.spawn_y), before)

    def test_stale_airborne_corpse_is_repaired_once(self):
        actor = corpse_actor(platforms=[pygame.Rect(80, 350, 120, 20)])
        self.assertTrue(ase_viewer._stabilize_corpse_grounding(actor))
        self.assertFalse(ase_viewer._stabilize_corpse_grounding(actor))
        self.assertEqual(actor.y, 350)

    def test_missing_metadata_and_malformed_platform_are_safe(self):
        actor = SimpleNamespace(
            master=SimpleNamespace(platforms=[object()]),
            is_corpse=True, is_prop=False,
        )
        self.assertTrue(ase_viewer._snap_npc_corpse_to_ground(actor))
        self.assertEqual(actor.y, 500.0)
        self.assertTrue(actor.grounded)

    def test_prop_is_not_changed_by_npc_snap_helper(self):
        prop = corpse_actor()
        prop.is_prop = True
        before = (prop.x, prop.y, prop.vy)
        self.assertFalse(ase_viewer._snap_npc_corpse_to_ground(prop))
        self.assertEqual((prop.x, prop.y, prop.vy), before)


if __name__ == "__main__":
    unittest.main()
