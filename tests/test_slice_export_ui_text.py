import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer
from tests.test_slice_export import MemorySource


class SliceExportUiTextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        ase_viewer.set_current_language(ase_viewer.LANG_KO)

    def test_core_keys_exist_in_both_languages(self):
        keys = {
            "common.confirm", "common.cancel", "common.save", "common.spawn",
            "category.language", "category.npcs", "category.props", "category.layers",
            "status.detected_slices", "status.parts", "status.particles",
            "export.confirm", "export.auto_desc", "export.name_desc",
            "export.use_asset_desc", "export.keep_slice_desc",
            "export.independent_hint", "export.preview", "export.enter_asset",
            "export.completed", "export.failed",
            "export.preview_total", "export.preview_status", "export.preview_empty",
            "export.folder_collision_hint", "tooltip.export.preview_list",
            "tooltip.export.collision", "tooltip.export.parts_group",
            "tooltip.export.particles_group", "tooltip.export.continue_disabled",
        }
        for language in (ase_viewer.LANG_KO, ase_viewer.LANG_EN):
            with self.subTest(language=language):
                self.assertFalse(keys - ase_viewer.TRANSLATIONS[language].keys())

    def test_korean_and_english_option_explanations(self):
        self.assertIn("실제 이미지 데이터", ase_viewer.tr("export.auto_desc"))
        self.assertIn("슬라이스 이름", ase_viewer.tr("export.name_desc"))
        self.assertIn("번호", ase_viewer.tr("export.use_asset_desc"))
        self.assertIn("파일명", ase_viewer.tr("export.keep_slice_desc"))
        self.assertIn("이름만", ase_viewer.tr("export.independent_hint"))
        self.assertIn("actual image data", ase_viewer.tr("export.auto_desc", language="en"))
        self.assertIn("slice names", ase_viewer.tr("export.name_desc", language="en"))

    def test_target_name_preview_and_blank_warning(self):
        source = MemorySource()
        options = {
            "classification": "auto",
            "naming_mode": "target",
            "target_name": "SporeHeart",
        }
        self.assertEqual(
            ase_viewer.slice_export_filename_preview(source, options),
            [
                "SporeHeart_Parts_01.png",
                "SporeHeart_Particle_01.png",
                "SporeHeart_Particle_02.png",
            ],
        )
        options["target_name"] = ""
        self.assertEqual(
            ase_viewer.slice_export_filename_preview(source, options),
            [ase_viewer.tr("export.enter_asset")],
        )

    def test_slice_name_preview_uses_real_first_valid_slice_names(self):
        source = MemorySource()
        preview = ase_viewer.slice_export_filename_preview(source, {
            "classification": "name",
            "naming_mode": "slice",
            "target_name": "Remember This",
        })
        self.assertEqual(preview, ["한글 파츠.png", "Particle Smoke.png"])

    def test_switching_naming_mode_does_not_clear_entered_name(self):
        target_name = "SporeHeart"
        source = MemorySource()
        ase_viewer.slice_export_filename_preview(source, {
            "classification": "auto", "naming_mode": "slice", "target_name": target_name,
        })
        preview = ase_viewer.slice_export_filename_preview(source, {
            "classification": "auto", "naming_mode": "target", "target_name": target_name,
        })
        self.assertEqual(target_name, "SporeHeart")
        self.assertEqual(preview[0], "SporeHeart_Parts_01.png")

    def test_plan_contains_all_groups_in_export_order(self):
        source = MemorySource()
        plan = ase_viewer.build_slice_export_plan(source, {
            "classification": "name",
            "naming_mode": "target",
            "target_name": "SporeHeart",
        })
        self.assertEqual((plan["parts"], plan["particles"]), (1, 1))
        self.assertEqual(
            [entry["filename"] for entry in plan["entries"]],
            ["SporeHeart_Parts_01.png", "SporeHeart_Particle_01.png"],
        )
        self.assertEqual(
            [entry["group"] for entry in plan["entries"]],
            ["Parts", "Particles"],
        )

    def test_slice_names_are_sanitized_and_internal_collisions_numbered(self):
        source = MemorySource()
        source.tags = {"Parts": (0, 0)}
        source.slices = {
            "a:b": [{"frame": 0, "bounds": {"x": 0, "y": 0, "w": 2, "h": 2}}],
            "a?b": [{"frame": 0, "bounds": {"x": 2, "y": 0, "w": 2, "h": 2}}],
        }
        plan = ase_viewer.build_slice_export_plan(source, {
            "classification": "name", "naming_mode": "slice", "target_name": "",
        })
        self.assertEqual(
            [entry["filename"] for entry in plan["entries"]],
            ["ab.png", "ab_2.png"],
        )

    def test_one_hundred_names_reuse_classification_for_name_edits(self):
        source = MemorySource()
        source.tags = {"Parts": (0, 0)}
        source.slices = {
            f"Part {index:03d}": [{
                "frame": 0,
                "bounds": {"x": (index % 4) * 2, "y": 0, "w": 2, "h": 2},
            }]
            for index in range(100)
        }
        first = ase_viewer.build_slice_export_plan(source, {
            "classification": "name", "naming_mode": "target", "target_name": "One",
        })
        cached = source._classification_mode_cache[(
            getattr(source, "source_revision", None), "name",
        )]
        second = ase_viewer.build_slice_export_plan(source, {
            "classification": "name", "naming_mode": "target", "target_name": "Two",
        })
        self.assertEqual(len(first["entries"]), 100)
        self.assertEqual(len(second["entries"]), 100)
        self.assertIs(
            cached,
            source._classification_mode_cache[(
                getattr(source, "source_revision", None), "name",
            )],
        )


if __name__ == "__main__":
    unittest.main()
