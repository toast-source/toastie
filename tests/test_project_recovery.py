import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import ase_viewer


def source_stub(path, source_id):
    return SimpleNamespace(id=source_id, file_path=path, name=Path(path).name, is_prop_source=False, tag_list=[])


class ProjectRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.project_path = self.root / "project.json"
        self.settings_path = self.root / "settings.json"
        self.player = ase_viewer.AsepritePlayer(project_path=str(self.project_path), settings_path=str(self.settings_path))
        self.original_source = source_stub("original.aseprite", 0)
        self.player.sources = [self.original_source]

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_project(self, sources, profiles=None, schema_version=None):
        data = {"sources": sources, "profiles": profiles or [], "ai_count": 0, "platforms": [], "solid_boxes": []}
        if schema_version is not None: data["schema_version"] = schema_version
        self.project_path.write_text(json.dumps(data), encoding="utf-8")

    def test_canceling_one_of_multiple_replacements_preserves_current_project(self):
        self.write_project(["missing-a.aseprite", "missing-b.aseprite"])
        with mock.patch("ase_viewer.show_user_error"), mock.patch("ase_viewer.select_file", side_effect=["replacement-a.aseprite", ""]), mock.patch.object(self.player, "_create_source") as create_source:
            self.assertFalse(self.player.load_project())
        self.assertEqual(self.player.sources, [self.original_source])
        create_source.assert_not_called()

    def test_duplicate_missing_path_is_requested_only_once(self):
        replacement = self.root / "replacement.aseprite"; replacement.touch()
        profiles = [{"name": "PLAYER", "source_idx": 0, "mappings": {}}, {"name": "NPC", "source_idx": 1, "mappings": {}}]
        self.write_project(["same-missing.aseprite", "same-missing.aseprite"], profiles, schema_version=2)
        with mock.patch("ase_viewer.show_user_error"), mock.patch("ase_viewer.select_file", return_value=str(replacement)) as select_file, mock.patch.object(self.player, "_create_source", side_effect=lambda path, idx: source_stub(path, idx)):
            self.assertTrue(self.player.load_project())
        select_file.assert_called_once()
        self.assertEqual([source.id for source in self.player.sources], [0, 1])
        self.assertEqual([profile.source_idx for profile in self.player.profiles], [0, 1])

    def test_source_preparation_failure_preserves_current_project(self):
        source = self.root / "source.aseprite"; source.touch()
        self.write_project([str(source)])
        with mock.patch("ase_viewer.show_user_error"), mock.patch.object(self.player, "_create_source", side_effect=ase_viewer.AsepriteError("metadata failure")):
            self.assertFalse(self.player.load_project())
        self.assertEqual(self.player.sources, [self.original_source])

    def test_legacy_and_schema_v2_projects_are_both_accepted(self):
        source = self.root / "source.aseprite"; source.touch()
        for schema_version in (None, 2):
            with self.subTest(schema_version=schema_version):
                self.write_project([str(source)], [{"name": "PLAYER", "source_idx": 0, "mappings": {}}], schema_version)
                with mock.patch.object(self.player, "_create_source", side_effect=lambda path, idx: source_stub(path, idx)):
                    self.assertTrue(self.player.load_project())

    def test_empty_project_lists_are_safe(self):
        self.write_project([], [], schema_version=2)
        self.assertTrue(self.player.load_project())
        self.assertEqual(self.player.sources, [])
        self.assertEqual(self.player.profiles, [])

    def test_mixed_relative_and_absolute_sources_resolve(self):
        relative = self.root / "assets" / "relative.aseprite"; relative.parent.mkdir(); relative.touch()
        absolute = self.root / "absolute.aseprite"; absolute.touch()
        self.write_project(["assets/relative.aseprite", str(absolute)])
        with mock.patch.object(self.player, "_create_source", side_effect=lambda path, idx: source_stub(path, idx)):
            self.assertTrue(self.player.load_project())
        self.assertTrue(Path(self.player.sources[0].file_path).samefile(relative))
        self.assertTrue(Path(self.player.sources[1].file_path).samefile(absolute))


if __name__ == "__main__":
    unittest.main()
