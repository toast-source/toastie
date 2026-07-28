import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


class TransitionSource:
    def __init__(self):
        self.id = 0
        self.name = "transition.aseprite"
        self.file_path = self.name
        self.kind = "generic"
        self.is_prop_source = False
        self.orig_w = self.orig_h = 4
        self.tags = {
            "Idle": (0, 1),
            "Attack1": (2, 3),
            "Attack2": (4, 5),
            "Attack3": (6, 7),
        }
        self.tag_list = list(self.tags)
        self.tag_metadata = {}
        self.slices = {}
        self.frames = []
        for index in range(8):
            image = pygame.Surface((4, 4), pygame.SRCALPHA)
            image.fill((index * 20, 100, 200, 255))
            self.frames.append({"img": image, "ox": -2, "oy": -4, "duration": 10})

    def get_frame(self, frame_index, zoom, facing_right):
        return self.frames[frame_index]["img"]

    def clear_cache(self):
        pass

    def check_for_reload(self):
        return False


class AnimationTransitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def make_player(self):
        player = ase_viewer.AsepritePlayer(project_path="unused.json", settings_path="unused-settings.json")
        source = TransitionSource()
        profile = ase_viewer.AseProfile("PLAYER", 0, kind="player")
        profile.mappings["IDLE"] = [[0, "Idle"]]
        profile.mappings["ComboAttack_1"] = [[0, "Attack1"]]
        profile.mappings["ComboAttack_2"] = [[0, "Attack2"]]
        profile.mappings["ComboAttack_3"] = [[0, "Attack3"]]
        player.sources = [source]
        player.profiles = [profile]
        player.grounded = True
        player.y = 500
        return player

    def finish_current_tag(self, player):
        player.frame_idx = player.action_end_frame
        player.anim_timer = player.sources[0].frames[player.frame_idx]["duration"]
        player.update(ase_viewer._SmokeKeys(), 500, 0)

    def test_single_attack_transitions_directly_to_idle_first_frame(self):
        player = self.make_player()
        player.trigger_action("ComboAttack_1", ase_viewer._SmokeKeys())
        self.finish_current_tag(player)
        self.assertIsNone(player.active_action_slot)
        self.assertIsNone(player.active_tag_info)
        self.assertEqual(player.frame_idx, 0)
        self.assertIn(player.frame_idx, range(0, 2))

    def test_three_attack_chain_has_no_out_of_range_frame_before_idle(self):
        player = self.make_player()
        player.trigger_action("ComboAttack_1", ase_viewer._SmokeKeys())
        observed = []
        for expected_slot, expected_start in (
            ("ComboAttack_2", 4),
            ("ComboAttack_3", 6),
        ):
            player.attack_buffer = 1
            self.finish_current_tag(player)
            observed.append(player.frame_idx)
            self.assertEqual(player.active_action_slot, expected_slot)
            self.assertEqual(player.frame_idx, expected_start)
        self.finish_current_tag(player)
        observed.append(player.frame_idx)
        self.assertEqual(observed, [4, 6, 0])
        self.assertIsNone(player.active_action_slot)
        self.assertEqual(player.attack_buffer, 0)
        self.assertEqual(player.combo_step, 3)


if __name__ == "__main__":
    unittest.main()
