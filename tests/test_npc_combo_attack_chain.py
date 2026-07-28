import unittest
from types import SimpleNamespace
from unittest import mock

import ase_viewer


def combo_profile(actions):
    mappings = {action: [[0, action]] for action in actions}
    return SimpleNamespace(
        name="Combo NPC", source_idx=0, kind="npc",
        is_prop_profile=False, ai_behavior="aggressive", mappings=mappings,
    )


def combo_source(count=3, duration=100):
    tags = {f"ComboAttack_{index}": (index - 1, index - 1)
            for index in range(1, count + 1)}
    return SimpleNamespace(
        tags=tags, tag_list=list(tags), frames=[
            {"duration": duration} for _ in range(count)
        ], slices={}, orig_w=64, orig_h=64,
    )


def combo_master(source):
    return SimpleNamespace(
        sources=[source], x=80.0, y=500.0, facing_right=True,
        world_ground_y=500.0, platforms=[], gravity=1.0, jump_power=-18.0,
        npc_max_hp=10, is_paused=False, hp=100, visible=True,
        profiles=[], damage_numbers=[], shake_enabled=False,
        play_sound=lambda name: None,
    )


class NpcComboAttackChainTests(unittest.TestCase):
    def test_detection_is_numeric_contiguous_and_non_mutating(self):
        tags = [
            "ComboAttack_10", "ComboAttack_2", "ComboAttack_1",
            "ComboAttack_3", "Attack_Intro", "ComboAttack_Intro",
            "ComboAttack_X",
        ]
        source = SimpleNamespace(tag_list=list(tags))
        self.assertEqual(
            ase_viewer._detect_npc_combo_actions(source),
            ["ComboAttack_1", "ComboAttack_2", "ComboAttack_3"],
        )
        self.assertEqual(source.tag_list, tags)

        continuous = SimpleNamespace(
            tag_list=[f"ComboAttack_{index}" for index in range(1, 11)],
        )
        self.assertEqual(
            ase_viewer._detect_npc_combo_actions(continuous)[-1],
            "ComboAttack_10",
        )

    def test_gap_or_missing_first_stops_chain(self):
        self.assertEqual(
            ase_viewer._get_npc_combo_chain(
                combo_profile(["ComboAttack_1", "ComboAttack_3"]),
            ),
            ["ComboAttack_1"],
        )
        self.assertEqual(
            ase_viewer._get_npc_combo_chain(
                combo_profile(["ComboAttack_2"]),
            ),
            [],
        )

    def test_auto_map_adds_dynamic_combo_and_plain_attack_fallback(self):
        player = SimpleNamespace()
        source = SimpleNamespace(
            tag_list=["Attack", "ComboAttack_1", "ComboAttack_2",
                      "ComboAttack_3", "ComboAttack_4", "ComboAttack_5"],
        )
        profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        player.sources = [source]
        with mock.patch.object(ase_viewer, "update_profile_ground_alignment"):
            ase_viewer.AsepritePlayer.auto_map_profile(player, profile)
        self.assertIn("ComboAttack_5", profile.mappings)
        self.assertEqual(
            profile.mappings["ComboAttack_5"], [[0, "ComboAttack_5"]],
        )

        attack_only = SimpleNamespace(tag_list=["Attack", "Attack_Intro"])
        profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        player.sources = [attack_only]
        with mock.patch.object(ase_viewer, "update_profile_ground_alignment"):
            ase_viewer.AsepritePlayer.auto_map_profile(player, profile)
        self.assertEqual(profile.mappings["ComboAttack_1"], [[0, "Attack"]])

    def test_three_segments_play_in_order_and_each_can_hit_once(self):
        source = combo_source(3)
        master = combo_master(source)
        profile = combo_profile([
            "ComboAttack_1", "ComboAttack_2", "ComboAttack_3",
        ])
        with mock.patch.object(
            ase_viewer, "ensure_source_slice_analysis", return_value={},
        ):
            npc = ase_viewer.AseAI(master, profile)
        npc.x = 0.0
        npc.y = 500.0
        self.assertTrue(ase_viewer._start_npc_attack(npc, 80))
        self.assertEqual(npc.active_action_slot, "ComboAttack_1")

        npc.update(500.0, 100)
        self.assertEqual(npc.active_action_slot, "ComboAttack_2")
        self.assertEqual(master.hp, 95)
        npc.update(500.0, 100)
        self.assertEqual(npc.active_action_slot, "ComboAttack_3")
        self.assertEqual(master.hp, 90)
        npc.update(500.0, 100)
        self.assertFalse(npc.npc_attack_locked)
        self.assertEqual(master.hp, 85)
        self.assertEqual(
            npc.npc_attack_cooldown, ase_viewer.NPC_ATTACK_RECOVERY_MS,
        )

    def test_combo_lock_blocks_ai_restart(self):
        npc = SimpleNamespace(
            profile=combo_profile(["ComboAttack_1", "ComboAttack_2"]),
            npc_attack_locked=True, intro_locked=False,
            decision="CHASE", vx=4.0,
        )
        ase_viewer.update_npc_behavior(npc, -500, 16.6)
        self.assertEqual(npc.decision, "ATTACK")
        self.assertEqual(npc.vx, 0)


if __name__ == "__main__":
    unittest.main()
