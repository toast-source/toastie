import json
import os
import tempfile
import unittest
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


class LocalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        ase_viewer.set_current_language(ase_viewer.LANG_KO)

    def test_korean_english_and_format_values(self):
        self.assertEqual(ase_viewer.tr("common.save"), "저장")
        self.assertEqual(ase_viewer.tr("common.save", language="en"), "Save")
        self.assertIn("3", ase_viewer.tr("status.precise_parts", count=3))

    def test_english_fallback_and_completely_missing_key_are_safe(self):
        fallback_key = "test.english.only"
        missing_key = "test.missing.everywhere"
        ase_viewer.TRANSLATIONS[ase_viewer.LANG_EN][fallback_key] = "English fallback"
        ase_viewer._MISSING_TRANSLATION_KEYS.discard(missing_key)
        try:
            self.assertEqual(ase_viewer.tr(fallback_key, language="ko"), "English fallback")
            with mock.patch("ase_viewer.log_debug") as log:
                self.assertEqual(ase_viewer.tr(missing_key), missing_key)
                self.assertEqual(ase_viewer.tr(missing_key), missing_key)
                log.assert_called_once()
        finally:
            del ase_viewer.TRANSLATIONS[ase_viewer.LANG_EN][fallback_key]
            ase_viewer._MISSING_TRANSLATION_KEYS.discard(missing_key)

    def test_unknown_language_defaults_to_korean(self):
        self.assertEqual(ase_viewer.normalize_language("invalid"), ase_viewer.LANG_KO)
        self.assertEqual(ase_viewer.set_current_language("invalid"), ase_viewer.LANG_KO)

    def test_settings_language_compatibility_without_automatic_save(self):
        cases = [
            ({}, ase_viewer.LANG_KO),
            ({"language": "ko"}, ase_viewer.LANG_KO),
            ({"language": "en"}, ase_viewer.LANG_EN),
            ({"language": "unknown"}, ase_viewer.LANG_KO),
        ]
        for data, expected in cases:
            with self.subTest(data=data), tempfile.TemporaryDirectory() as temp_dir:
                settings_path = os.path.join(temp_dir, "settings.json")
                project_path = os.path.join(temp_dir, "project.json")
                original = json.dumps(data, ensure_ascii=False)
                with open(settings_path, "w", encoding="utf-8") as settings_file:
                    settings_file.write(original)
                player = ase_viewer.AsepritePlayer(
                    settings_path=settings_path,
                    project_path=project_path,
                )
                self.assertTrue(player.load_settings(notify_missing_assets=False))
                self.assertEqual(player.language, expected)
                with open(settings_path, "r", encoding="utf-8") as settings_file:
                    self.assertEqual(settings_file.read(), original)
                self.assertFalse(os.path.exists(project_path))

    def test_system_font_helper_is_cached_and_renders_korean(self):
        first = ase_viewer.create_ui_font(13, bold=True)
        second = ase_viewer.create_ui_font(13, bold=True)
        self.assertIs(first, second)
        self.assertGreater(first.render("한국어 English", True, (255, 255, 255)).get_width(), 0)

    def test_major_tooltip_keys_exist_in_both_languages(self):
        keys = {
            "tooltip.project.new", "tooltip.project.load", "tooltip.project.save",
            "tooltip.npc.add", "tooltip.prop.add", "tooltip.npc.spawn",
            "tooltip.prop.spawn", "tooltip.npc.save", "tooltip.prop.save",
            "tooltip.detected_slices", "tooltip.auto", "tooltip.name",
            "tooltip.naming.target", "tooltip.naming.slice", "tooltip.parallax",
        }
        for language in (ase_viewer.LANG_KO, ase_viewer.LANG_EN):
            self.assertFalse(keys - ase_viewer.TRANSLATIONS[language].keys())

    def test_unity_export_keys_exist_in_both_languages(self):
        keys = {
            "unity.copy_button", "unity.dialog_title", "unity.ppu",
            "unity.detailed", "unity.slack", "unity.markdown", "unity.tsv",
            "unity.include_disabled", "unity.copy_failed", "unity.no_layers",
            "unity.copy_success_detailed", "unity.copy_success_slack",
            "unity.copy_success_markdown", "unity.copy_success_tsv",
            "unity.detailed_help", "unity.slack_help",
            "unity.markdown_help", "unity.tsv_help",
            "tooltip.unity_ppu", "tooltip.unity_copy",
            "tooltip.unity_detailed", "tooltip.unity_slack",
            "tooltip.unity_markdown", "tooltip.unity_tsv",
        }
        for language in (ase_viewer.LANG_KO, ase_viewer.LANG_EN):
            self.assertFalse(keys - ase_viewer.TRANSLATIONS[language].keys())

    def test_unity_export_settings_are_backward_compatible_and_not_auto_saved(self):
        cases = [
            ({}, (100.0, "detailed", True)),
            ({
                "unity_pixels_per_unit": 256,
                "unity_parallax_export_format": "compact",
                "unity_parallax_include_disabled": False,
            }, (256.0, "slack", False)),
            ({"unity_parallax_export_format": "detailed"}, (100.0, "detailed", True)),
            ({"unity_parallax_export_format": "slack"}, (100.0, "slack", True)),
            ({"unity_parallax_export_format": "markdown"}, (100.0, "markdown", True)),
            ({"unity_parallax_export_format": "tsv"}, (100.0, "tsv", True)),
            ({
                "unity_pixels_per_unit": 0,
                "unity_parallax_export_format": "invalid",
            }, (100.0, "detailed", True)),
        ]
        for data, expected in cases:
            with self.subTest(data=data), tempfile.TemporaryDirectory() as temp_dir:
                settings_path = os.path.join(temp_dir, "settings.json")
                original = json.dumps(data)
                with open(settings_path, "w", encoding="utf-8") as settings_file:
                    settings_file.write(original)
                player = ase_viewer.AsepritePlayer(
                    settings_path=settings_path,
                    project_path=os.path.join(temp_dir, "project.json"),
                )
                self.assertTrue(player.load_settings(notify_missing_assets=False))
                self.assertEqual(
                    (
                        player.unity_pixels_per_unit,
                        player.unity_parallax_export_format,
                        player.unity_parallax_include_disabled,
                    ),
                    expected,
                )
                with open(settings_path, "r", encoding="utf-8") as settings_file:
                    self.assertEqual(settings_file.read(), original)

    def test_unity_export_preferences_save_only_to_settings(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_path = os.path.join(temp_dir, "settings.json")
            project_path = os.path.join(temp_dir, "project.json")
            player = ase_viewer.AsepritePlayer(
                settings_path=settings_path, project_path=project_path,
            )
            player.unity_pixels_per_unit = 128
            player.unity_parallax_export_format = "tsv"
            player.unity_parallax_include_disabled = False
            player.save_settings()
            with open(settings_path, "r", encoding="utf-8") as settings_file:
                data = json.load(settings_file)
            self.assertEqual(data["unity_pixels_per_unit"], 128)
            self.assertEqual(data["unity_parallax_export_format"], "tsv")
            self.assertFalse(data["unity_parallax_include_disabled"])
            self.assertFalse(os.path.exists(project_path))


if __name__ == "__main__":
    unittest.main()
