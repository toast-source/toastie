import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import ase_viewer


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.previous_cwd = os.getcwd()
        self.temp_dir = tempfile.TemporaryDirectory()
        os.chdir(self.temp_dir.name)
        self.project_path = str(Path(self.temp_dir.name) / "ase_project.json")
        self.settings_path = str(Path(self.temp_dir.name) / "ase_settings.json")

    def tearDown(self):
        os.chdir(self.previous_cwd)
        self.temp_dir.cleanup()

    def test_new_player_can_save_project_without_loading_existing_data(self):
        player = ase_viewer.AsepritePlayer(project_path=self.project_path, settings_path=self.settings_path)

        player.save_project()

        with open(self.project_path, "r", encoding="utf-8") as project_file:
            project = json.load(project_file)
        self.assertEqual(project["solid_boxes"], [])

    def test_custom_controls_round_trip_through_settings(self):
        player = ase_viewer.AsepritePlayer(project_path=self.project_path, settings_path=self.settings_path)
        player.key_map["ATTACK"] = ase_viewer.pygame.K_q
        player.save_settings()

        restored_player = ase_viewer.AsepritePlayer(project_path=self.project_path, settings_path=self.settings_path)
        restored_player.load_settings()

        self.assertEqual(restored_player.key_map["ATTACK"], ase_viewer.pygame.K_q)

    def test_failed_json_serialization_preserves_existing_file(self):
        with open("existing.json", "w", encoding="utf-8") as existing_file:
            json.dump({"status": "original"}, existing_file)

        with self.assertRaises(TypeError):
            ase_viewer.save_json("existing.json", {"invalid": object()})

        with open("existing.json", "r", encoding="utf-8") as existing_file:
            self.assertEqual(json.load(existing_file), {"status": "original"})
        self.assertEqual(list(Path.cwd().glob(".existing.json.*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
