import unittest
from types import SimpleNamespace

import pygame

import ase_viewer


def combat_pair(player_x=80, facing_right=True):
    player = SimpleNamespace(
        x=player_x, y=500.0, visible=True, hp=100,
        profiles=[], damage_numbers=[], shake_enabled=False,
        play_sound=lambda name: None,
    )
    npc = SimpleNamespace(
        x=0.0, y=500.0, master=player,
        facing_right=facing_right,
        npc_attack_facing_right=facing_right,
        npc_attack_locked=True,
        npc_attack_slot="ComboAttack_1",
        active_action_slot="ComboAttack_1",
        active_tag_info=[0, "Attack"],
        npc_attack_elapsed=0.0,
        npc_attack_duration=450.0,
        npc_attack_has_hit=False,
        npc_attack_cooldown=0.0,
    )
    player.sources = []
    return npc, player


class NpcAttackHitboxTests(unittest.TestCase):
    def test_front_target_is_hit_only_when_window_is_reached(self):
        npc, player = combat_pair()
        ase_viewer._update_npc_attack_state(npc, 100)
        self.assertEqual(player.hp, 100)
        ase_viewer._update_npc_attack_state(npc, 60)
        self.assertEqual(player.hp, 95)
        ase_viewer._update_npc_attack_state(npc, 80)
        self.assertEqual(player.hp, 95)
        self.assertTrue(npc.npc_attack_has_hit)

    def test_target_outside_or_behind_is_not_hit(self):
        npc, player = combat_pair(player_x=250)
        ase_viewer._update_npc_attack_state(npc, 200)
        self.assertEqual(player.hp, 100)

        npc, player = combat_pair(player_x=-60, facing_right=True)
        ase_viewer._update_npc_attack_state(npc, 200)
        self.assertEqual(player.hp, 100)

    def test_hitbox_tracks_left_facing_and_ground_y(self):
        npc, player = combat_pair(player_x=-70, facing_right=False)
        hitbox = ase_viewer.npc_attack_hitbox(npc)
        self.assertLess(hitbox.left, npc.x)
        self.assertEqual(hitbox.bottom, npc.y)
        ase_viewer._update_npc_attack_state(npc, 200)
        self.assertEqual(player.hp, 95)

    def test_ground_offset_does_not_shift_world_space_fallback(self):
        npc, player = combat_pair()
        npc.profile = SimpleNamespace(ground_offset_y=240)
        self.assertEqual(ase_viewer.npc_attack_hitbox(npc).bottom, npc.y)

    def test_missing_player_is_safe(self):
        npc, _ = combat_pair()
        npc.master = None
        self.assertFalse(ase_viewer._apply_npc_attack_hit(npc))

    def test_authored_hit_slice_takes_precedence(self):
        npc, player = combat_pair(player_x=35)
        npc.master.sources = [SimpleNamespace(
            slices={"Hit": [{"frame": 0, "bounds": {
                "x": 32, "y": 20, "w": 30, "h": 40,
            }}]},
            orig_w=64, orig_h=64,
        )]
        hitbox = ase_viewer.npc_attack_hitbox(npc)
        self.assertEqual(hitbox.size, (30, 40))
        self.assertTrue(hitbox.colliderect(ase_viewer.player_hurtbox(player)))


if __name__ == "__main__":
    unittest.main()
