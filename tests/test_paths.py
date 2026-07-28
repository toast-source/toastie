import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import ase_viewer


class PathTests(unittest.TestCase):
    def test_project_asset_on_same_drive_is_saved_relative(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "프로젝트 폴더" / "project.json"
            asset = project.parent / "애셋 폴더" / "player one.aseprite"
            asset.parent.mkdir(parents=True)
            asset.touch()

            stored = ase_viewer.portable_path(str(asset), str(project))

            self.assertEqual(stored, "애셋 폴더/player one.aseprite")

    def test_relative_path_failure_keeps_absolute_path(self):
        absolute = os.path.abspath("asset.aseprite")
        with mock.patch("ase_viewer.os.path.relpath", side_effect=ValueError("different drive")):
            self.assertEqual(ase_viewer.portable_path(absolute, "project.json"), absolute)

    def test_relative_path_resolves_from_project_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project.json"
            asset = Path(temp_dir) / "assets" / "hero.aseprite"
            asset.parent.mkdir(); asset.touch()

            resolved, _ = ase_viewer.resolve_stored_path("assets/hero.aseprite", str(project), app_root="C:\\unrelated")

            self.assertTrue(os.path.samefile(resolved, asset))

    def test_existing_absolute_path_remains_compatible(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            asset = Path(temp_dir) / "legacy.aseprite"; asset.touch()
            resolved, _ = ase_viewer.resolve_stored_path(str(asset), str(Path(temp_dir) / "project.json"))
            self.assertTrue(os.path.samefile(resolved, asset))

    def test_missing_path_returns_checked_locations(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            resolved, checked = ase_viewer.resolve_stored_path("missing.aseprite", str(Path(temp_dir) / "project.json"), app_root=temp_dir)
            self.assertIsNone(resolved)
            self.assertTrue(checked)

    def test_example_path_does_not_depend_on_current_working_directory(self):
        previous = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                resolved, _ = ase_viewer.resolve_stored_path("Testfiles/Test01.aseprite", str(Path(temp_dir) / "project.json"), app_root=str(PROJECT_ROOT))
            finally:
                os.chdir(previous)
        self.assertEqual(resolved, str((PROJECT_ROOT / "Testfiles" / "Test01.aseprite").resolve()))

    def test_project_save_uses_relative_source_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "project.json"
            settings_path = Path(temp_dir) / "settings.json"
            asset = Path(temp_dir) / "assets" / "hero.aseprite"
            asset.parent.mkdir(); asset.touch()
            player = ase_viewer.AsepritePlayer(project_path=str(project_path), settings_path=str(settings_path))
            player.sources = [SimpleNamespace(file_path=str(asset))]

            player.save_project()

            with project_path.open("r", encoding="utf-8") as project_file:
                data = json.load(project_file)
            self.assertEqual(data["schema_version"], 2)
            self.assertEqual(data["sources"], ["assets/hero.aseprite"])

    def test_invalid_project_json_is_reported_without_overwrite(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "project.json"
            project_path.write_text("{invalid", encoding="utf-8")
            player = ase_viewer.AsepritePlayer(project_path=str(project_path), settings_path=str(Path(temp_dir) / "settings.json"))
            with mock.patch("ase_viewer.show_user_error") as show_error:
                self.assertFalse(player.load_project())
            show_error.assert_called_once()
            self.assertEqual(project_path.read_text(encoding="utf-8"), "{invalid")

    def test_missing_required_project_fields_are_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "project.json"
            project_path.write_text('{"sources": []}', encoding="utf-8")
            player = ase_viewer.AsepritePlayer(project_path=str(project_path), settings_path=str(Path(temp_dir) / "settings.json"))
            with mock.patch("ase_viewer.show_user_error") as show_error:
                self.assertFalse(player.load_project())
            show_error.assert_called_once()


if __name__ == "__main__":
    unittest.main()
