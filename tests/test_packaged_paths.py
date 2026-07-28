import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import ase_viewer


class PackagedPathTests(unittest.TestCase):
    def test_bundle_resource_has_priority_over_executable_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir); bundle = root / "bundle"; app = root / "app"
            (bundle / "data").mkdir(parents=True); (app / "data").mkdir(parents=True)
            bundled = bundle / "data" / "fixture.txt"; bundled.write_text("bundle", encoding="utf-8")
            (app / "data" / "fixture.txt").write_text("app", encoding="utf-8")
            with mock.patch.object(ase_viewer, "RESOURCE_ROOT", str(bundle)), mock.patch.object(ase_viewer, "APP_ROOT", str(app)):
                self.assertTrue(Path(ase_viewer.app_resource_path("data/fixture.txt")).samefile(bundled))

    def test_external_resource_next_to_executable_is_supported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir); bundle = root / "bundle"; app = root / "한글 배포 폴더"
            bundle.mkdir(); (app / "Testfiles").mkdir(parents=True)
            external = app / "Testfiles" / "Test01.aseprite"; external.touch()
            with mock.patch.object(ase_viewer, "RESOURCE_ROOT", str(bundle)), mock.patch.object(ase_viewer, "APP_ROOT", str(app)):
                self.assertTrue(Path(ase_viewer.app_resource_path("Testfiles/Test01.aseprite")).samefile(external))

    def test_missing_packaged_resource_returns_predictable_external_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            app = Path(temp_dir) / "app with spaces"; app.mkdir()
            with mock.patch.object(ase_viewer, "RESOURCE_ROOT", str(Path(temp_dir) / "bundle")), mock.patch.object(ase_viewer, "APP_ROOT", str(app)):
                result = Path(ase_viewer.app_resource_path("Testfiles/Test01.aseprite"))
                self.assertEqual(result.name, "Test01.aseprite")
                self.assertEqual(result.parent.name, "Testfiles")
                self.assertEqual(result.parent.parent.name, "app with spaces")

    def test_spec_does_not_bundle_fixture_with_unknown_distribution_rights(self):
        spec_text = (PROJECT_ROOT / "ase_viewer.spec").read_text(encoding="utf-8")
        self.assertNotIn("Test01.aseprite", spec_text)
        self.assertNotIn("Testfiles", spec_text)


if __name__ == "__main__":
    unittest.main()
