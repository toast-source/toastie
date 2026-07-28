import unittest
from types import SimpleNamespace

import ase_viewer


def dash_actor(**overrides):
    values = {
        "x": 120.0,
        "y": 500.0,
        "vx": 12.0,
        "vy": 0.0,
        "grounded": True,
        "dash_started_grounded": True,
        "dash_timer": 180,
        "particles": [],
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class GroundedDashDustTests(unittest.TestCase):
    def test_grounded_dash_emits_dust_without_changing_motion(self):
        actor = dash_actor()
        motion_before = (actor.x, actor.y, actor.vx, actor.vy, actor.grounded)
        self.assertTrue(ase_viewer.emit_ground_dash_dust(actor, chance_value=0.0))
        self.assertEqual(len(actor.particles), 1)
        self.assertEqual(
            (actor.x, actor.y, actor.vx, actor.vy, actor.grounded),
            motion_before,
        )

    def test_airborne_jumping_and_falling_dash_emit_no_dust(self):
        for vy in (-12.0, 8.0, 0.0):
            with self.subTest(vy=vy):
                actor = dash_actor(grounded=False, vy=vy)
                self.assertFalse(
                    ase_viewer.emit_ground_dash_dust(actor, chance_value=0.0)
                )
                self.assertEqual(actor.particles, [])

    def test_air_dash_does_not_emit_after_landing_during_same_dash(self):
        actor = dash_actor(
            grounded=True,
            dash_started_grounded=False,
        )
        self.assertFalse(
            ase_viewer.emit_ground_dash_dust(actor, chance_value=0.0)
        )
        self.assertEqual(actor.particles, [])

    def test_missing_grounded_state_is_safe_and_emits_no_dust(self):
        actor = SimpleNamespace(
            x=0.0, y=0.0, dash_timer=100, particles=[],
        )
        self.assertFalse(ase_viewer.can_emit_ground_dash_dust(actor))
        self.assertFalse(
            ase_viewer.emit_ground_dash_dust(actor, chance_value=0.0)
        )

    def test_inactive_dash_and_failed_chance_emit_no_dust(self):
        inactive = dash_actor(dash_timer=0)
        self.assertFalse(
            ase_viewer.emit_ground_dash_dust(inactive, chance_value=0.0)
        )
        actor = dash_actor()
        self.assertFalse(
            ase_viewer.emit_ground_dash_dust(actor, chance_value=0.9)
        )
        self.assertEqual(actor.particles, [])


if __name__ == "__main__":
    unittest.main()
