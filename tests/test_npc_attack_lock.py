import unittest
from types import SimpleNamespace
from unittest import mock

import ase_viewer


def attack_npc(**overrides):
    mappings = {
        "ComboAttack_1": [[0, "Attack"]],
        "ComboAttack_2": [],
        "ComboAttack_3": [],
        "ComboAttack_4": [],
    }
    values = {
        "profile": SimpleNamespace(ai_behavior="aggressive", mappings=mappings),
        "master": SimpleNamespace(sources=[]),
        "active_action_slot": None,
        "active_tag_info": None,
        "npc_attack_locked": False,
        "npc_attack_cooldown": 0.0,
        "npc_attack_slot": None,
        "npc_attack_elapsed": 0.0,
        "npc_attack_duration": 0.0,
        "npc_attack_has_hit": False,
        "npc_attack_instance_id": 0,
        "is_dead": False,
        "is_corpse": False,
        "decision": "IDLE",
        "facing_right": False,
        "vx": 2.0,
        "x": 20.0,
        "y": 500.0,
        "trigger_action": mock.Mock(return_value=True),
    }
    values.update(overrides)
    npc = SimpleNamespace(**values)

    def trigger(slot):
        npc.active_action_slot = slot
        npc.active_tag_info = [0, "Attack"]
        return True

    if "trigger_action" not in overrides:
        npc.trigger_action = mock.Mock(side_effect=trigger)
    return npc


class NpcAttackLockTests(unittest.TestCase):
    def test_start_locks_attack_and_does_not_move_actor(self):
        npc = attack_npc()
        position = (npc.x, npc.y)
        self.assertTrue(ase_viewer._start_npc_attack(npc, 80))
        self.assertTrue(npc.npc_attack_locked)
        self.assertEqual(npc.decision, "ATTACK")
        self.assertTrue(npc.facing_right)
        self.assertEqual((npc.x, npc.y), position)

    def test_behavior_does_not_restart_or_overwrite_locked_attack(self):
        npc = attack_npc()
        ase_viewer._start_npc_attack(npc, 80)
        npc.trigger_action.reset_mock()
        ase_viewer.update_npc_behavior(npc, -500, 16.6)
        self.assertEqual(npc.decision, "ATTACK")
        self.assertEqual(npc.vx, 0)
        npc.trigger_action.assert_not_called()

    def test_animation_end_starts_recovery_and_cooldown_expires(self):
        npc = attack_npc()
        ase_viewer._start_npc_attack(npc, 80)
        npc.active_tag_info = None
        ase_viewer._update_npc_attack_state(npc, 16.6)
        self.assertFalse(npc.npc_attack_locked)
        self.assertEqual(npc.npc_attack_cooldown, ase_viewer.NPC_ATTACK_RECOVERY_MS)
        self.assertFalse(ase_viewer._start_npc_attack(npc, 80))
        ase_viewer._update_npc_attack_state(
            npc, ase_viewer.NPC_ATTACK_RECOVERY_MS,
        )
        self.assertTrue(ase_viewer._start_npc_attack(npc, 80))

    def test_missing_or_empty_attack_mapping_is_safe(self):
        npc = attack_npc()
        npc.profile.mappings = {}
        self.assertFalse(ase_viewer._start_npc_attack(npc, 80))
        self.assertFalse(npc.npc_attack_locked)

        npc.profile.mappings = {"ComboAttack_1": [[0, "Attack"]]}
        npc.master.sources = [
            SimpleNamespace(tags={"Attack": (0, 0)}, frames=[]),
        ]
        self.assertTrue(ase_viewer._start_npc_attack(npc, 80))
        self.assertEqual(
            npc.npc_attack_duration,
            ase_viewer.NPC_ATTACK_FALLBACK_DURATION_MS,
        )

    def test_fallback_duration_releases_stalled_action(self):
        npc = attack_npc()
        ase_viewer._start_npc_attack(npc, 80)
        ase_viewer._update_npc_attack_state(
            npc,
            ase_viewer.NPC_ATTACK_FALLBACK_DURATION_MS
            + ase_viewer.NPC_ATTACK_FALLBACK_GRACE_MS,
        )
        self.assertFalse(npc.npc_attack_locked)


if __name__ == "__main__":
    unittest.main()
