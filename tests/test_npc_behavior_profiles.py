import json
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import ase_viewer


def behavior_ai(behavior, **overrides):
    mappings = {
        f"ComboAttack_{index}": [[0, "Attack"]]
        for index in range(1, 5)
    }
    values = {
        "profile": SimpleNamespace(ai_behavior=behavior, mappings=mappings),
        "ai_timer": 0,
        "decision": "IDLE",
        "active_tag_info": None,
        "active_action_slot": None,
        "facing_right": True,
        "grounded": True,
        "vy": 0.0,
        "vx": 0.0,
        "x": 0.0,
        "spawn_x": 0.0,
        "is_dead": False,
        "is_corpse": False,
        "npc_attack_locked": False,
        "npc_attack_cooldown": 0.0,
        "master": SimpleNamespace(jump_power=-18.0, sources=[]),
        "trigger_action": mock.Mock(return_value=True),
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def source_stub(path):
    return SimpleNamespace(
        id=0,
        name=os.path.basename(path),
        file_path=path,
        kind="generic",
        is_prop_source=False,
        tags={},
        tag_list=[],
        frames=[],
        slices={},
        source_revision=1,
        slice_analysis_revision=None,
        slice_export_analysis=None,
        clear_cache=lambda: None,
    )


class NpcBehaviorProfileTests(unittest.TestCase):
    def test_behavior_normalization_and_cycle(self):
        profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        self.assertEqual(profile.ai_behavior, "balanced")
        cycled = [
            ase_viewer.cycle_npc_behavior(profile)
            for _ in range(len(ase_viewer.NPC_BEHAVIORS))
        ]
        self.assertEqual(cycled[-1], "balanced")
        self.assertEqual(
            ase_viewer.normalize_npc_behavior("unknown"),
            "balanced",
        )

    def test_idle_and_follow_behaviors(self):
        idle = behavior_ai("idle")
        ase_viewer.update_npc_behavior(idle, 400, 16.6)
        self.assertEqual(idle.decision, "IDLE")
        self.assertFalse(idle.trigger_action.called)

        follow = behavior_ai("follow")
        ase_viewer.update_npc_behavior(follow, 400, 16.6)
        self.assertEqual(follow.decision, "CHASE")
        ase_viewer.update_npc_behavior(follow, 80, 16.6)
        self.assertEqual(follow.decision, "IDLE")
        self.assertFalse(follow.trigger_action.called)

    def test_aggressive_chases_then_attacks(self):
        aggressive = behavior_ai("aggressive")
        ase_viewer.update_npc_behavior(aggressive, 400, 16.6)
        self.assertEqual(aggressive.decision, "CHASE")
        aggressive.ai_timer = 0
        ase_viewer.update_npc_behavior(aggressive, 80, 16.6)
        self.assertEqual(aggressive.decision, "ATTACK")
        aggressive.trigger_action.assert_called_once()

    def test_guard_returns_home_and_attacks_nearby(self):
        guard = behavior_ai("guard", x=100.0, spawn_x=0.0)
        ase_viewer.update_npc_behavior(guard, 500, 16.6)
        self.assertEqual(guard.decision, "WALK_L")
        guard.ai_timer = 0
        ase_viewer.update_npc_behavior(guard, 80, 16.6)
        self.assertEqual(guard.decision, "ATTACK")

    def test_patrol_and_flee_directions(self):
        patrol = behavior_ai("patrol", x=250.0, spawn_x=0.0)
        ase_viewer.update_npc_behavior(patrol, 1000, 16.6)
        self.assertEqual(patrol.decision, "WALK_L")

        flee = behavior_ai("flee")
        ase_viewer.update_npc_behavior(flee, 100, 16.6)
        self.assertEqual(flee.decision, "WALK_L")
        ase_viewer.update_npc_behavior(flee, -100, 16.6)
        self.assertEqual(flee.decision, "WALK_R")

    def test_behavior_labels_and_options_height(self):
        player = SimpleNamespace(profiles=[
            ase_viewer.AseProfile("NPC_A", 0, kind="npc"),
            ase_viewer.AseProfile("NPC_B", 0, kind="npc"),
        ])
        height = ase_viewer.ai_combat_content_height(player)
        player.profiles.pop()
        self.assertGreater(
            height,
            ase_viewer.ai_combat_content_height(player),
        )
        for language in ("ko", "en"):
            for behavior in ase_viewer.NPC_BEHAVIORS:
                self.assertTrue(
                    ase_viewer.tr(
                        f"npc_behavior.{behavior}", language=language,
                    )
                )

    def test_behavior_persists_as_optional_profile_field(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = os.path.join(temp_dir, "NPC.aseprite")
            with open(source_path, "wb") as source_file:
                source_file.write(b"fixture")
            project_path = os.path.join(temp_dir, "project.json")
            player = ase_viewer.AsepritePlayer(
                project_path=project_path,
                settings_path=os.path.join(temp_dir, "settings.json"),
            )
            player.sources = [source_stub(source_path)]
            profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
            profile.ai_behavior = "guard"
            player.profiles = [profile]
            player.save_project()
            with open(project_path, "r", encoding="utf-8") as project_file:
                saved = json.load(project_file)
            self.assertEqual(saved["profiles"][0]["ai_behavior"], "guard")

            loaded = ase_viewer.AsepritePlayer(
                project_path=project_path,
                settings_path=os.path.join(temp_dir, "loaded-settings.json"),
            )
            with mock.patch.object(
                loaded, "_create_source",
                return_value=source_stub(source_path),
            ):
                self.assertTrue(loaded.load_project())
            self.assertEqual(loaded.profiles[0].ai_behavior, "guard")


if __name__ == "__main__":
    unittest.main()
