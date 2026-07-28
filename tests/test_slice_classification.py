import os
import tempfile
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


class ClassificationSource:
    def __init__(self):
        self.name = "fallback.aseprite"
        self.file_path = self.name
        self.orig_w = 4
        self.orig_h = 4
        part_frame = pygame.Surface((4, 4), pygame.SRCALPHA)
        particle_frame = pygame.Surface((4, 4), pygame.SRCALPHA)
        part_frame.fill((0, 0, 0, 0))
        particle_frame.fill((0, 0, 0, 0))
        pygame.draw.rect(part_frame, (255, 0, 0, 255), (0, 0, 2, 2))
        pygame.draw.rect(particle_frame, (0, 255, 0, 255), (2, 0, 2, 2))
        self.frames = [
            {"img": part_frame, "ox": -2, "oy": -2, "duration": 10},
            {"img": particle_frame, "ox": -2, "oy": -2, "duration": 10},
        ]
        self.tags = {"Particles": (1, 1), "Parts": (0, 0)}
        self.slices = {
            "Slice 1": [{"frame": 0, "bounds": {"x": 0, "y": 0, "w": 2, "h": 2}}],
            "Slice 2": [{"frame": 0, "bounds": {"x": 2, "y": 0, "w": 2, "h": 2}}],
        }

    def get_frame(self, frame_index, zoom, facing_right):
        return self.frames[frame_index]["img"]


class SliceClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_auto_uses_pixels_not_tag_order_or_default_slice_number(self):
        source = ClassificationSource()
        result = ase_viewer.classify_export_slices(source)
        self.assertEqual(
            [(item["group"], item["slice_name"]) for item in result["items"]],
            [("Parts", "Slice 1"), ("Particles", "Slice 2")],
        )
        self.assertTrue(ase_viewer.evaluate_slice_export(source)["enabled"])

    def test_auto_finds_later_non_empty_frame_and_skips_fully_transparent_slice(self):
        source = ClassificationSource()
        source.tags["Parts"] = (0, 1)
        source.slices["Late"] = [{"frame": 0, "bounds": {"x": 2, "y": 0, "w": 2, "h": 2}}]
        source.slices["Empty"] = [{"frame": 0, "bounds": {"x": 0, "y": 2, "w": 2, "h": 2}}]
        result = ase_viewer.classify_export_slices(source)
        late = [item for item in result["items"] if item["slice_name"] == "Late" and item["group"] == "Parts"]
        self.assertEqual(late[0]["frame"], 1)
        self.assertFalse(any(item["slice_name"] == "Empty" for item in result["items"]))

    def test_same_unhinted_slice_can_exist_in_both_groups_and_reports_duplicate(self):
        source = ClassificationSource()
        source.frames[1]["img"] = source.frames[0]["img"].copy()
        source.slices = {"Slice 1": source.slices["Slice 1"]}
        result = ase_viewer.classify_export_slices(source)
        self.assertEqual([item["group"] for item in result["items"]], ["Parts", "Particles"])
        self.assertTrue(all(item["possible_duplicate"] for item in result["items"]))

    def test_name_mode_preserves_particle_name_filter(self):
        source = ClassificationSource()
        source.slices = {
            "Head": source.slices["Slice 1"],
            "Particle Smoke": source.slices["Slice 2"],
        }
        result = ase_viewer.classify_export_slices(source, mode="name")
        self.assertEqual(
            [(item["group"], item["slice_name"]) for item in result["items"]],
            [("Parts", "Head"), ("Particles", "Particle Smoke")],
        )

    def test_standard_names_are_independent_deterministic_and_collision_safe(self):
        source = ClassificationSource()
        with tempfile.TemporaryDirectory() as output_dir:
            with open(os.path.join(output_dir, "고블린_Parts_01.png"), "wb") as existing:
                existing.write(b"keep")
            result = ase_viewer.export_source_slices(source, output_dir, owner_name="고블린")
            names = [os.path.basename(path) for path in result["saved"]]
            self.assertEqual(names, ["고블린_Parts_01_2.png", "고블린_Particle_01.png"])
            self.assertEqual([entry["slice_name"] for entry in result["entries"]], ["Slice 1", "Slice 2"])


if __name__ == "__main__":
    unittest.main()
