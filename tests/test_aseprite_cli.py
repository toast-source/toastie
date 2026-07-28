import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import ase_viewer


class AsepriteCliTests(unittest.TestCase):
    def test_invalid_executable_path_is_rejected(self):
        with self.assertRaisesRegex(ase_viewer.AsepriteError, "executable does not exist"):
            ase_viewer.run_aseprite(["--version"], executable="missing-aseprite.exe")

    def test_missing_source_is_rejected_before_process_start(self):
        with self.assertRaisesRegex(ase_viewer.AsepriteError, "Source file does not exist"):
            ase_viewer.export_aseprite("missing.aseprite", "sheet.png", "data.json", executable="unused.exe")

    def test_invalid_configured_path_is_not_silently_used(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(json.dumps({"aseprite_path": str(Path(temp_dir) / "missing.exe")}), encoding="utf-8")
            with mock.patch.object(ase_viewer.AsePathManager, "find_aseprite", return_value=None):
                manager = ase_viewer.AsePathManager(config_path=str(config_path))
                with self.assertRaisesRegex(ase_viewer.AsepriteError, "could not be found"):
                    manager.get_path(allow_prompt=False)

    def test_process_timeout_is_reported(self):
        with tempfile.NamedTemporaryFile(suffix=".exe") as executable, mock.patch("ase_viewer.subprocess.run", side_effect=subprocess.TimeoutExpired([], 1)):
            with self.assertRaisesRegex(ase_viewer.AsepriteError, "within 1 seconds"):
                ase_viewer.run_aseprite(["--version"], executable=executable.name, timeout=1)

    def test_nonzero_return_code_has_user_safe_error(self):
        completed = subprocess.CompletedProcess([], 2, stdout="", stderr="technical detail")
        with tempfile.NamedTemporaryFile(suffix=".exe") as executable, mock.patch("ase_viewer.subprocess.run", return_value=completed):
            with self.assertRaisesRegex(ase_viewer.AsepriteError, "exit code 2"):
                ase_viewer.run_aseprite(["--version"], executable=executable.name)

    def test_missing_export_result_is_reported(self):
        completed = subprocess.CompletedProcess([], 0, stdout="", stderr="")
        with tempfile.NamedTemporaryFile(suffix=".exe") as executable, tempfile.TemporaryDirectory() as temp_dir, mock.patch("ase_viewer.subprocess.run", return_value=completed):
            with self.assertRaisesRegex(ase_viewer.AsepriteError, "did not create"):
                ase_viewer.run_aseprite([], executable=executable.name, expected_files=(str(Path(temp_dir) / "sheet.png"),))

    def test_invalid_export_metadata_is_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source.aseprite"; source.touch()
            png_path = Path(temp_dir) / "sheet.png"
            json_path = Path(temp_dir) / "data.json"

            def fake_run(arguments, executable=None, expected_files=(), timeout=ase_viewer.ASEPRITE_TIMEOUT_SECONDS):
                png_path.touch(); json_path.write_text("{}", encoding="utf-8")
                return subprocess.CompletedProcess([], 0)

            with mock.patch("ase_viewer.run_aseprite", side_effect=fake_run):
                with self.assertRaisesRegex(ase_viewer.AsepriteError, "frames"):
                    ase_viewer.export_aseprite(str(source), str(png_path), str(json_path), executable="fake.exe")


class AsepriteIntegrationTests(unittest.TestCase):
    def test_installed_aseprite_exports_repository_fixture(self):
        executable = ase_viewer.ase_manager.find_aseprite()
        fixture = PROJECT_ROOT / "Testfiles" / "Test01.aseprite"
        if not executable:
            self.skipTest("Aseprite CLI is not installed in a known location")
        if not fixture.is_file():
            self.skipTest("Testfiles/Test01.aseprite is not available")
        with tempfile.TemporaryDirectory() as temp_dir:
            png_path = Path(temp_dir) / "sheet.png"
            json_path = Path(temp_dir) / "data.json"
            data = ase_viewer.export_aseprite(str(fixture), str(png_path), str(json_path), executable=executable)
            self.assertTrue(png_path.is_file())
            self.assertTrue(json_path.is_file())
            self.assertGreater(len(data["frames"]), 0)


if __name__ == "__main__":
    unittest.main()
