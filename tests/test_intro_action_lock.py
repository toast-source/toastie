import unittest
from types import SimpleNamespace
from unittest import mock

import ase_viewer


def intro_actor(is_prop=False):
    source = SimpleNamespace(
        name="Intro.aseprite",
        tags={"Intro": (0, 1), "Idle": (2, 2)},
        tag_list=["Intro", "Idle"],
        frames=[{"duration": 100}, {"duration": 100}, {"duration": 100}],
        slices={}, orig_w=32, orig_h=32,
    )
    master = SimpleNamespace(
        sources=[source], x=0.0, y=100.0, facing_right=True,
        world_ground_y=500.0, platforms=[], gravity=1.0,
        jump_power=-18.0, npc_max_hp=10, is_paused=False,
        hp=100, visible=True, profiles=[], damage_numbers=[],
        shake_enabled=False, play_sound=lambda name: None,
    )
    profile = SimpleNamespace(
        name="Intro", source_idx=0,
        kind="prop" if is_prop else "npc",
        is_prop_profile=is_prop, ai_behavior="aggressive",
        mappings={
            "INTRO": [[0, "Intro"]], "IDLE": [[0, "Idle"]],
            "ComboAttack_1": [[0, "Intro"]],
        },
    )
    with mock.patch.object(
        ase_viewer, "ensure_source_slice_analysis", return_value={},
    ):
        return ase_viewer.AseAI(master, profile, is_prop=is_prop)


class IntroActionLockTests(unittest.TestCase):
    def test_spawn_intro_stays_grounded_and_blocks_actions(self):
        actor = intro_actor()
        self.assertTrue(actor.intro_locked)
        self.assertEqual(actor.y, 500.0)
        actor.vy = -20
        actor.decision = "JUMP"
        self.assertFalse(actor.trigger_action("ComboAttack_1"))
        actor.update(500.0, 80)
        self.assertEqual((actor.y, actor.vy), (500.0, 0))
        self.assertEqual(actor.decision, "IDLE")

    def test_intro_finishes_then_ai_can_resume(self):
        actor = intro_actor()
        actor.update(500.0, 100)
        actor.update(500.0, 100)
        self.assertFalse(actor.intro_locked)
        self.assertIsNone(actor.active_action_slot)
        actor.ai_timer = 100
        actor.update(500.0, 16.6)
        self.assertIn(actor.decision, {"IDLE", "CHASE"})

    def test_prop_intro_uses_same_no_jump_lock(self):
        prop = intro_actor(is_prop=True)
        prop.vy = -12
        prop.update(500.0, 80)
        self.assertTrue(prop.intro_locked)
        self.assertEqual((prop.y, prop.vy), (500.0, 0))

    def test_replaying_an_active_intro_is_a_safe_noop(self):
        actor = intro_actor()
        player = actor.master
        player.profiles = [actor.profile]
        player.ai_list = [actor]
        player.prop_list = []
        player.partner_profiles = []
        player.selected_scene_actor_key = ("npc", id(actor))
        player.cur_profile_idx = 0
        result = ase_viewer.replay_npc_intro(player)
        self.assertEqual(
            result["status_key"], "status.npc_intro_already_playing",
        )
        self.assertEqual(actor.active_action_slot, "INTRO")


if __name__ == "__main__":
    unittest.main()
