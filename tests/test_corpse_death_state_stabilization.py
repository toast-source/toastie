import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


class DeathSource:
    def __init__(self):
        image = pygame.Surface((8, 12), pygame.SRCALPHA)
        image.fill((255, 255, 255, 255))
        self.id = 0
        self.name = "Death.aseprite"
        self.file_path = self.name
        self.kind = "npc"
        self.is_prop_source = False
        self.tags = {"Idle": (0, 0), "Dead_(Loop)": (0, 0)}
        self.tag_list = list(self.tags)
        self.tag_metadata = {"Dead_(Loop)": {"repeat": "1"}}
        self.frames = [{"img": image, "ox": -4, "oy": -6, "duration": 100}]
        self.slices = {}
        self.orig_w = 8
        self.orig_h = 12

    def get_frame(self, frame_index, zoom, facing_right):
        return self.frames[frame_index]["img"]


class CorpseDeathStateStabilizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def make_actor(self, y=180.0):
        player = ase_viewer.AsepritePlayer(
            project_path="unused-project.json",
            settings_path="unused-settings.json",
        )
        source = DeathSource()
        profile = ase_viewer.AseProfile("NPC", 0, kind="npc")
        profile.mappings["IDLE"] = [[0, "Idle"]]
        profile.mappings["DEAD_LOOP"] = [[0, "Dead_(Loop)"]]
        player.sources = [source]
        player.profiles = [profile]
        player.platforms = [pygame.Rect(80, 340, 160, 20)]
        player.world_ground_y = 500.0
        actor = ase_viewer.AseAI(player, profile, hp=2)
        actor.x = 120.0
        actor.y = y
        actor.vy = -14.0
        actor.grounded = False
        player.ai_list = [actor]
        player.target_ai_count = 1
        return player, actor

    def test_death_clears_intro_combo_attack_and_hit_runtime(self):
        player, actor = self.make_actor()
        actor.intro_locked = True
        actor.intro_elapsed = 25
        actor.npc_attack_locked = True
        actor.npc_attack_slot = "ComboAttack_2"
        actor.npc_attack_has_hit = True
        actor.npc_attack_cooldown = 400
        actor.npc_combo_actions = ["ComboAttack_1", "ComboAttack_2"]
        actor.npc_combo_index = 1
        actor.pending_execution = 20
        player.trigger_npc_death(actor)
        self.assertFalse(actor.intro_locked)
        self.assertFalse(actor.npc_attack_locked)
        self.assertEqual(actor.npc_combo_actions, [])
        self.assertFalse(actor.npc_attack_has_hit)
        self.assertEqual(actor.npc_attack_cooldown, 0)
        self.assertEqual(actor.pending_execution, 0)

    def test_airborne_combo_death_starts_corpse_on_platform(self):
        player, actor = self.make_actor()
        actor.npc_attack_locked = True
        actor.npc_combo_actions = ["ComboAttack_1", "ComboAttack_2"]
        result = player.trigger_npc_death(actor)
        self.assertEqual(result["corpse_mode"], "dead_loop")
        self.assertTrue(actor.is_dead)
        self.assertTrue(actor.is_corpse)
        self.assertEqual((actor.x, actor.y), (120.0, 340.0))
        self.assertTrue(actor.grounded)
        self.assertEqual(actor.vy, 0)
        self.assertTrue(ase_viewer._is_scene_object_corpse(actor))

    def test_grounded_platform_death_does_not_move_actor(self):
        player, actor = self.make_actor(y=340.0)
        actor.grounded = True
        actor.vy = 0
        player.trigger_npc_death(actor)
        self.assertEqual((actor.x, actor.y), (120.0, 340.0))
        self.assertTrue(actor.grounded)

    def test_intro_death_and_repeated_death_do_not_jitter_or_duplicate(self):
        player, actor = self.make_actor()
        actor.intro_locked = True
        first = player.trigger_npc_death(actor)
        position = (actor.x, actor.y)
        second = player.trigger_npc_death(actor)
        self.assertIsNotNone(first)
        self.assertIsNone(second)
        self.assertEqual((actor.x, actor.y), position)
        self.assertEqual(player.ai_list.count(actor), 1)

    def test_corpse_update_repairs_stale_airborne_position(self):
        player, actor = self.make_actor()
        player.trigger_npc_death(actor)
        actor.y = 210
        actor.vy = -9
        actor.grounded = False
        actor.update(500, 16.6)
        self.assertEqual(actor.y, 340)
        self.assertEqual(actor.vy, 0)
        self.assertTrue(actor.grounded)

    def test_scene_snapshot_preserves_snapped_corpse_position(self):
        player, actor = self.make_actor()
        player.trigger_npc_death(actor)
        snapshot = ase_viewer.snapshot_scene_object_states(player)
        actor.y = 100
        actor.grounded = False
        ase_viewer.restore_scene_object_states(player, snapshot)
        self.assertEqual(actor.y, 340)
        self.assertTrue(actor.grounded)


if __name__ == "__main__":
    unittest.main()
