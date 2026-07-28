import hashlib
import os
import tempfile
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


class SporeHeartNpcRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))
        cls.source_path = os.environ.get(
            "ASE_VIEWER_SPOREHEART_FIXTURE",
            os.path.join(
                os.path.dirname(ase_viewer.__file__),
                "SporeHeart.aseprite",
            ),
        )
        if not os.path.isfile(cls.source_path):
            pygame.quit()
            raise unittest.SkipTest(
                "SporeHeart runtime fixture not available; "
                "skipping integration test. "
                "Set ASE_VIEWER_SPOREHEART_FIXTURE to enable it."
            )

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    @staticmethod
    def part_signature(analysis):
        return [
            (
                item["slice_name"],
                dict(item["bounds"]),
                hashlib.sha256(pygame.image.tostring(item["image"], "RGBA")).hexdigest(),
            )
            for item in analysis["valid_parts_slices"]
        ]

    def test_actual_registration_death_update_render_spawn_and_ui_selection(self):
        original_hash = ase_viewer.file_sha256(self.source_path)
        with tempfile.TemporaryDirectory(prefix="sporeheart_runtime_test_") as temp_dir:
            player = ase_viewer.AsepritePlayer(
                project_path=os.path.join(temp_dir, "project.json"),
                settings_path=os.path.join(temp_dir, "settings.json"),
            )
            player.visible = False
            player.show_viewport = False
            registration = player.register_npc_source(self.source_path, profile_name="SporeHeart")
            self.assertIsNotNone(registration)
            source = registration["source"]
            profile = registration["profile"]
            npc = registration["instance"]
            analysis = ase_viewer.ensure_source_slice_analysis(source)

            self.assertEqual(registration["profile_idx"], player.profiles.index(profile))
            self.assertEqual(registration["source_idx"], profile.source_idx)
            self.assertEqual(profile.kind, "npc")
            self.assertIs(npc.profile, profile)
            self.assertEqual(len(analysis["valid_parts_slices"]), 9)
            self.assertEqual(len(analysis["valid_particle_slices"]), 7)
            self.assertEqual(profile.mappings["DEAD_LOOP"], [[profile.source_idx, "Dead_(Loop)"]])

            # The selected UI profile is deliberately not the dying instance's profile.
            other_profile = ase_viewer.AseProfile("Other NPC", registration["source_idx"], kind="npc")
            player.profiles.append(other_profile)
            player.cur_profile_idx = player.profiles.index(other_profile)
            npc.x, npc.y = 400, 400
            npc.facing_right = True
            player.cam_follow = False
            player.cam_x, player.cam_y = npc.x, npc.y

            result = player.trigger_npc_death(npc)
            self.assertIs(result["profile"], profile)
            self.assertEqual(result["source_idx"], profile.source_idx)
            self.assertEqual(result["corpse_mode"], "dead_loop")
            self.assertEqual(result["parts_mode"], "precise")
            self.assertEqual((result["requested"], result["created"]), (9, 9))
            self.assertIn(npc, player.ai_list)
            self.assertTrue(npc.is_corpse)
            self.assertFalse(any(item is npc and not item.is_dead for item in player.ai_list))

            player.update(ase_viewer._SmokeKeys(), 500, 16.6)
            self.assertEqual(result["remaining"], 9)
            self.assertEqual(result["image_particles"], 9)
            self.assertEqual(result["visible"], 9)
            screen = pygame.Surface((800, 570))
            player.draw(screen, 800, 570)
            self.assertEqual(result["rendered"], 9)
            self.assertTrue(all(
                particle.cached_surface is not None
                for particle in player.particles
                if id(particle) in result["particle_ids"]
            ))
            status = ase_viewer.npc_slice_status_data(profile, player.sources, result)
            self.assertEqual(status["death"], "Dead Loop + Precise Parts 9")
            self.assertEqual(status["runtime"], "Last Death: corpse=Dead Loop / parts=9")

            spawned = player.spawn_npc_profile(registration["profile_idx"])
            self.assertIsNotNone(spawned)
            self.assertIs(spawned.profile, profile)
            self.assertEqual(spawned.profile.source_idx, registration["source_idx"])
            spawned.x, spawned.y = 400, 400
            spawned_result = player.trigger_npc_death(spawned)
            self.assertEqual(spawned_result["corpse_mode"], "dead_loop")
            self.assertEqual(spawned_result["parts_mode"], "precise")
            self.assertEqual(spawned_result["created"], 9)
            player.update(ase_viewer._SmokeKeys(), 500, 16.6)
            player.draw(screen, 800, 570)
            self.assertEqual(spawned_result["remaining"], 9)
            self.assertEqual(spawned_result["rendered"], 9)

            prop_profile = ase_viewer.AseProfile("SporeHeart PROP", registration["source_idx"], kind="prop")
            prop_analysis = ase_viewer.ensure_source_slice_analysis(
                player.sources[prop_profile.source_idx],
            )
            self.assertEqual(self.part_signature(analysis), self.part_signature(prop_analysis))
            self.assertEqual(len(prop_analysis["valid_parts_slices"]), 9)

        self.assertEqual(ase_viewer.file_sha256(self.source_path), original_hash)


if __name__ == "__main__":
    unittest.main()
