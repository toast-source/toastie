import hashlib
import os
import tempfile
import unittest
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


class MemorySource:
    def __init__(self):
        self.name = "SporeHeart.aseprite"
        self.file_path = self.name
        self.tags = {"Parts": (0, 0), "Particles": (0, 0)}
        self.orig_w = 8
        self.orig_h = 8
        image = pygame.Surface((8, 8), pygame.SRCALPHA)
        image.fill((0, 0, 0, 0))
        pygame.draw.rect(image, (255, 0, 0, 255), (0, 0, 4, 4))
        pygame.draw.rect(image, (0, 255, 0, 128), (4, 0, 4, 4))
        pygame.draw.rect(image, (0, 0, 255, 255), (0, 4, 4, 4))
        self.frames = [{"img": image, "ox": -4, "oy": -4, "duration": 100}]
        self.slices = {
            "한글 파츠": [{"frame": 0, "bounds": {"x": 0, "y": 0, "w": 4, "h": 4}}],
            "Particle Smoke": [{"frame": 0, "bounds": {"x": 4, "y": 0, "w": 4, "h": 4}}],
        }

    def get_frame(self, frame_index, zoom, facing_right):
        return self.frames[frame_index]["img"]


def digest(path):
    with open(path, "rb") as png_file:
        return hashlib.sha256(png_file.read()).hexdigest()


class SliceExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_parts_and_particles_filters_are_shared_by_npc_and_prop(self):
        source = MemorySource()
        with tempfile.TemporaryDirectory() as npc_dir, tempfile.TemporaryDirectory() as prop_dir:
            npc_result = ase_viewer.export_source_slices(source, npc_dir, mode="name", owner_name="Shared")
            prop_result = ase_viewer.export_source_slices(source, prop_dir, mode="name", owner_name="Shared")

            npc_names = sorted(os.path.basename(path) for path in npc_result["saved"])
            prop_names = sorted(os.path.basename(path) for path in prop_result["saved"])
            self.assertEqual(npc_names, ["Shared_Particle_01.png", "Shared_Parts_01.png"])
            self.assertEqual(npc_names, prop_names)
            self.assertEqual(
                {name: digest(os.path.join(npc_dir, name)) for name in npc_names},
                {name: digest(os.path.join(prop_dir, name)) for name in prop_names},
            )
            part_image = pygame.image.load(os.path.join(npc_dir, "Shared_Parts_01.png"))
            particle_image = pygame.image.load(os.path.join(npc_dir, "Shared_Particle_01.png"))
            self.assertEqual(part_image.get_size(), (4, 4))
            self.assertEqual(particle_image.get_at((0, 0)).a, 128)

    def test_safe_names_empty_names_collisions_and_existing_files_are_renamed(self):
        source = MemorySource()
        source.tags = {"Parts": (0, 0)}
        source.slices = {
            "a:b": [{"frame": 0, "bounds": {"x": 0, "y": 0, "w": 2, "h": 2}}],
            "a?b": [{"frame": 0, "bounds": {"x": 2, "y": 0, "w": 2, "h": 2}}],
            ":::": [{"frame": 0, "bounds": {"x": 4, "y": 0, "w": 2, "h": 2}}],
            "CON": [{"frame": 0, "bounds": {"x": 6, "y": 0, "w": 2, "h": 2}}],
        }
        with tempfile.TemporaryDirectory() as output_dir:
            with open(os.path.join(output_dir, "ab.png"), "wb") as existing:
                existing.write(b"keep")
            result = ase_viewer.export_source_slices(source, output_dir, mode="name", owner_name="CON")
            names = sorted(os.path.basename(path) for path in result["saved"])
            self.assertEqual(names, ["CON_slice_Parts_01.png", "CON_slice_Parts_02.png", "CON_slice_Parts_03.png", "CON_slice_Parts_04.png"])
            with open(os.path.join(output_dir, "ab.png"), "rb") as existing:
                self.assertEqual(existing.read(), b"keep")

    def test_missing_tags_and_empty_bounds_are_reported_without_success(self):
        source = MemorySource()
        source.tags = {}
        with tempfile.TemporaryDirectory() as output_dir:
            result = ase_viewer.export_source_slices(source, output_dir, target_name="Source")
        self.assertFalse(result["saved"])
        self.assertGreaterEqual(len(result["skipped"]), 2)

        source = MemorySource()
        source.tags = {"Parts": (0, 0)}
        source.slices = {
            "empty": [{
                "frame": 0,
                "bounds": {"x": 0, "y": 0, "w": 0, "h": 2},
            }],
        }
        with tempfile.TemporaryDirectory() as output_dir:
            result = ase_viewer.export_source_slices(
                source, output_dir, target_name="Source",
            )
        self.assertFalse(result["saved"])
        self.assertTrue(any(
            "non-empty image" in reason.casefold()
            for reason in result["skipped"]
        ))

    def test_one_png_failure_does_not_stop_later_slices(self):
        source = MemorySource()
        source.tags = {"Parts": (0, 0)}
        source.slices = {
            "bad": [{"frame": 0, "bounds": {"x": 0, "y": 0, "w": 2, "h": 2}}],
            "good": [{"frame": 0, "bounds": {"x": 2, "y": 0, "w": 2, "h": 2}}],
        }
        real_save = pygame.image.save

        def selective_save(surface, path):
            if ".Source_Parts_01.png." in path:
                raise pygame.error("simulated PNG failure")
            return real_save(surface, path)

        with tempfile.TemporaryDirectory() as output_dir, mock.patch("pygame.image.save", side_effect=selective_save):
            result = ase_viewer.export_source_slices(source, output_dir, target_name="Source")
            self.assertEqual([os.path.basename(path) for path in result["saved"]], ["Source_Parts_02.png"])
            self.assertEqual(len(result["failed"]), 1)

    def test_target_name_policy_and_source_filename_suggestion(self):
        source = MemorySource()
        self.assertEqual(ase_viewer.suggested_export_target_name(source), "SporeHeart")
        valid, error = ase_viewer.validate_slice_export_options({
            "classification": "auto",
            "naming_mode": "target",
            "target_name": " SporeHeart ",
        })
        self.assertFalse(error)
        self.assertEqual(valid["target_name"], "SporeHeart")
        invalid, error = ase_viewer.validate_slice_export_options({
            "classification": "auto",
            "naming_mode": "target",
            "target_name": "   ",
        })
        self.assertIsNone(invalid)
        self.assertIn("target name", error.lower())

        with tempfile.TemporaryDirectory() as output_dir:
            result = ase_viewer.export_source_slices(
                source,
                output_dir,
                mode="name",
                naming_mode="target",
                target_name="SporeHeart",
            )
        self.assertEqual(
            [os.path.basename(path) for path in result["saved"]],
            ["SporeHeart_Parts_01.png", "SporeHeart_Particle_01.png"],
        )

    def test_slice_names_are_preserved_safely_and_collisions_never_overwrite(self):
        source = MemorySource()
        source.tags = {"Parts": (0, 0)}
        source.slices = {
            "Head": [{"frame": 0, "bounds": {"x": 0, "y": 0, "w": 2, "h": 2}}],
            "Slice 1": [{"frame": 0, "bounds": {"x": 2, "y": 0, "w": 2, "h": 2}}],
            "한글 파츠": [{"frame": 0, "bounds": {"x": 4, "y": 0, "w": 2, "h": 2}}],
            "a:b": [{"frame": 0, "bounds": {"x": 6, "y": 0, "w": 1, "h": 2}}],
            "a?b": [{"frame": 0, "bounds": {"x": 7, "y": 0, "w": 1, "h": 2}}],
            "CON.txt": [{"frame": 0, "bounds": {"x": 0, "y": 2, "w": 2, "h": 2}}],
            ":::": [{"frame": 0, "bounds": {"x": 2, "y": 2, "w": 2, "h": 2}}],
        }
        with tempfile.TemporaryDirectory() as output_dir:
            with open(os.path.join(output_dir, "Head.png"), "wb") as existing:
                existing.write(b"keep")
            result = ase_viewer.export_source_slices(
                source,
                output_dir,
                mode="name",
                naming_mode="slice",
            )
            names = [os.path.basename(path) for path in result["saved"]]
            with open(os.path.join(output_dir, "Head.png"), "rb") as existing:
                self.assertEqual(existing.read(), b"keep")
        self.assertEqual(
            names,
            [
                "Head_2.png",
                "Slice 1.png",
                "한글 파츠.png",
                "ab.png",
                "ab_2.png",
                "CON.txt_slice.png",
                "Slice_007.png",
            ],
        )
        self.assertEqual(result["renamed_collisions"], 2)

    def test_export_workflow_stops_at_each_cancel_point_and_is_shared(self):
        source = MemorySource()
        options_prompt = mock.Mock(return_value={
            "classification": "auto",
            "naming_mode": "target",
            "target_name": "Goblin",
        })
        folder_prompt = mock.Mock(return_value="C:\\output")
        exporter = mock.Mock(return_value={
            "saved": [], "skipped": [], "failed": [], "entries": [],
            "mode": "auto", "naming_mode": "target", "target_name": "Goblin",
            "renamed_collisions": 0, "output_directory": "C:\\output",
        })
        with mock.patch("ase_viewer.show_user_error"), mock.patch("ase_viewer.show_user_info"):
            self.assertIsNone(ase_viewer.run_slice_export_workflow(
                source, "NPC", confirm=lambda: False,
                options_prompt=options_prompt, folder_prompt=folder_prompt, exporter=exporter,
            ))
            options_prompt.assert_not_called()
            folder_prompt.assert_not_called()

            options_prompt.return_value = None
            self.assertIsNone(ase_viewer.run_slice_export_workflow(
                source, "PROP", confirm=lambda: True,
                options_prompt=options_prompt, folder_prompt=folder_prompt, exporter=exporter,
            ))
            folder_prompt.assert_not_called()

            options_prompt.return_value = {
                "classification": "name", "naming_mode": "slice", "target_name": "",
            }
            folder_prompt.return_value = ""
            self.assertIsNone(ase_viewer.run_slice_export_workflow(
                source, "NPC", confirm=lambda: True,
                options_prompt=options_prompt, folder_prompt=folder_prompt, exporter=exporter,
            ))
            exporter.assert_not_called()

            folder_prompt.return_value = "C:\\output"
            ase_viewer.run_slice_export_workflow(
                source, "NPC", confirm=lambda: True,
                options_prompt=options_prompt, folder_prompt=folder_prompt, exporter=exporter,
            )
            ase_viewer.run_slice_export_workflow(
                source, "PROP", confirm=lambda: True,
                options_prompt=options_prompt, folder_prompt=folder_prompt, exporter=exporter,
            )
        self.assertEqual(exporter.call_count, 2)
        self.assertEqual(
            [call.kwargs["owner_kind"] for call in exporter.call_args_list],
            ["NPC", "PROP"],
        )

    def test_save_confirmation_precedes_options_for_npc_and_prop(self):
        source = MemorySource()
        for owner_kind in ("NPC", "PROP"):
            with self.subTest(owner_kind=owner_kind):
                player = mock.Mock()
                player.popup = None
                with mock.patch("ase_viewer.run_slice_export_workflow") as workflow:
                    self.assertTrue(ase_viewer.begin_slice_export(player, source, owner_kind))
                    self.assertIsNotNone(player.popup)
                    self.assertEqual(ase_viewer.tr("export.confirm"), player.popup["msg"])
                    self.assertIsNone(player.popup["no_cb"])
                    workflow.assert_not_called()
                    player.popup["cb"]()
                    workflow.assert_called_once()
                    self.assertEqual(workflow.call_args.args[:2], (source, owner_kind))

    def test_npc_auto_names_ignore_default_slice_numbers(self):
        source = MemorySource()
        parts_frame = pygame.Surface((8, 8), pygame.SRCALPHA)
        particles_frame = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.rect(parts_frame, (255, 0, 0, 255), (0, 0, 4, 4))
        pygame.draw.rect(particles_frame, (0, 255, 0, 255), (4, 0, 4, 4))
        source.frames = [
            {"img": parts_frame, "ox": -4, "oy": -4, "duration": 100},
            {"img": particles_frame, "ox": -4, "oy": -4, "duration": 100},
        ]
        source.tags = {"Parts": (0, 0), "Particles": (1, 1)}
        source.slices = {
            "Slice 8": [{"frame": 0, "bounds": {"x": 0, "y": 0, "w": 4, "h": 4}}],
            "Slice 1 Particle": [{"frame": 0, "bounds": {"x": 4, "y": 0, "w": 4, "h": 4}}],
        }
        with tempfile.TemporaryDirectory() as output_dir:
            result = ase_viewer.export_source_slices(
                source,
                output_dir,
                mode="auto",
                owner_name="Goblin",
                owner_kind="NPC",
            )
        self.assertEqual(
            [os.path.basename(path) for path in result["saved"]],
            ["Goblin_Parts_01.png", "Goblin_Particle_01.png"],
        )


if __name__ == "__main__":
    unittest.main()
