import os
import sys
import tempfile
import unittest
import hashlib
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import ase_viewer


def all_example_resources_available():
    resources = {
        resource["path"]
        for variant in (1, 2)
        for resource in (
            ase_viewer.example_preset(variant)["sources"]
            + ase_viewer.example_preset(variant)["bg_layers"]
        )
    }
    return all(Path(ase_viewer.app_resource_path(path)).is_file() for path in resources)


requires_internal_examples = unittest.skipUnless(
    all_example_resources_available(),
    "Internal resources/examples assets are not checked into the repository.",
)


def fake_source(path="fixture.aseprite", source_id=0):
    profile = ase_viewer.example_preset(1)["profiles"][source_id]
    tags = {mapping[1]: (0, 0) for entries in profile["mappings"].values() for mapping in entries}
    return SimpleNamespace(id=source_id, file_path=path, name=Path(path).name, is_prop_source=False, tags=tags, tag_list=sorted(tags), frames=[], slices={}, orig_w=16, orig_h=16, layers=[], visible_layers=set())


class ExampleTests(unittest.TestCase):
    def setUp(self):
        ase_viewer.pygame.init()
        ase_viewer.pygame.display.set_mode((1, 1))
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = str(Path(self.temp_dir.name) / "project.json")
        self.settings_path = str(Path(self.temp_dir.name) / "settings.json")
        self.player = ase_viewer.AsepritePlayer(project_path=self.project_path, settings_path=self.settings_path)
        self.original_source = fake_source("original.aseprite")
        self.player.sources = [self.original_source]

    def tearDown(self):
        self.temp_dir.cleanup()
        ase_viewer.pygame.quit()

    def test_example_presets_have_intentional_differences(self):
        first = ase_viewer.example_preset(1)
        second = ase_viewer.example_preset(2)
        self.assertNotEqual(first["bg_color"], second["bg_color"])
        self.assertNotEqual(first["cam_v_offset"], second["cam_v_offset"])
        self.assertNotEqual(first["purpose"], second["purpose"])
        self.assertEqual(len(first["bg_layers"]), 1)
        self.assertEqual(len(second["bg_layers"]), 6)

    @requires_internal_examples
    def test_example_success_applies_only_after_source_preparation(self):
        created = [fake_source("Cailin.aseprite", 0), fake_source("Nisariel.aseprite", 1)]
        factory = mock.Mock(side_effect=created)
        self.assertTrue(self.player._load_example(1, persist=False, source_factory=factory))
        self.assertEqual(self.player.sources, created)
        self.assertEqual([source.id for source in created], [0, 1])
        self.assertEqual([profile.name for profile in self.player.profiles], ["PLAYER", "NPC_1"])
        self.assertEqual([profile.source_idx for profile in self.player.profiles], [0, 1])
        self.assertEqual(len(self.player.ai_list), 0)
        self.assertEqual(len(self.player.partner_profiles), 1)
        self.assertEqual(len(self.player.partner_list), 0)
        self.assertEqual(len(self.player.prop_list), 0)
        self.assertEqual(len(self.player.platforms), 6)
        self.assertEqual(len(self.player.solid_boxes), 2)
        self.assertEqual(len(self.player.bg_layers), 1)
        self.assertFalse(Path(self.project_path).exists())
        self.assertFalse(Path(self.settings_path).exists())

    def test_missing_example_resource_preserves_current_state(self):
        original_layers = [{"path": "original.png"}]
        self.player.bg_layers = original_layers
        real_resolver = ase_viewer.app_resource_path
        def missing_one(path):
            if path.endswith("00.png"):
                return str(Path(self.temp_dir.name) / "missing.png")
            return real_resolver(path)
        with mock.patch("ase_viewer.app_resource_path", side_effect=missing_one), mock.patch("ase_viewer.show_user_error"):
            self.assertFalse(self.player._load_example(2, persist=False, source_factory=fake_source))
        self.assertEqual(self.player.sources, [self.original_source])
        self.assertIs(self.player.bg_layers, original_layers)

    @requires_internal_examples
    def test_background_decode_failure_preserves_current_state(self):
        original_layers = [{"path": "original.png"}]
        self.player.bg_layers = original_layers
        with mock.patch("ase_viewer.pygame.image.load", side_effect=ase_viewer.pygame.error("decode failure")), mock.patch("ase_viewer.show_user_error"):
            self.assertFalse(self.player._load_example(1, persist=False, source_factory=fake_source))
        self.assertEqual(self.player.sources, [self.original_source])
        self.assertIs(self.player.bg_layers, original_layers)

    def test_example_export_failure_preserves_current_state(self):
        def failing_factory(path, source_id):
            raise ase_viewer.AsepriteError("mock export failure")
        with mock.patch("ase_viewer.show_user_error"):
            self.assertFalse(self.player._load_example(2, persist=False, source_factory=failing_factory))
        self.assertEqual(self.player.sources, [self.original_source])

    def test_ex2_restores_historical_parallax_order_and_values(self):
        preset = ase_viewer.example_preset(2)
        names = [Path(layer["path"]).name for layer in preset["bg_layers"]]
        self.assertEqual(names, ["00.png", "01.png", "# 2번_완성본.png", "# 3번_완성본.png", "# 4번_완성본.png", "레이어 3.png"])
        self.assertEqual([layer["parallax"] for layer in preset["bg_layers"]], [0.0, 0.05, 0.06, 0.5344827586206895, 0.703448275862069, 1.0])
        self.assertEqual([layer["loop_x"] for layer in preset["bg_layers"]], [False, False, False, True, True, True])
        self.assertEqual([layer["off_y"] for layer in preset["bg_layers"]], [-13, -27, -137, -220, -234, 137])

    @requires_internal_examples
    def test_all_bundled_example_resources_match_restored_hashes(self):
        resources = {}
        for variant in (1, 2):
            preset = ase_viewer.example_preset(variant)
            for resource in preset["sources"] + preset["bg_layers"]:
                resources[resource["path"]] = resource["sha256"]
        self.assertEqual(len(resources), 9)
        for stored_path, expected_hash in resources.items():
            resolved = ase_viewer.app_resource_path(stored_path)
            self.assertTrue(Path(resolved).is_file(), stored_path)
            self.assertEqual(ase_viewer.file_sha256(resolved), expected_hash, stored_path)
            self.assertNotIn("/build/", resolved.replace("\\", "/").lower())
            self.assertNotIn("/desktop/ase_viewer/", resolved.replace("\\", "/").lower())

    @requires_internal_examples
    def test_resources_resolve_from_korean_space_working_directory(self):
        previous = os.getcwd()
        work_dir = Path(self.temp_dir.name) / "한글 작업 폴더"
        work_dir.mkdir()
        try:
            os.chdir(work_dir)
            for layer in ase_viewer.example_preset(2)["bg_layers"]:
                self.assertTrue(Path(ase_viewer.app_resource_path(layer["path"])).is_file())
        finally:
            os.chdir(previous)

    @requires_internal_examples
    def test_ex2_applies_six_loaded_layers_and_historical_profiles(self):
        self.assertTrue(self.player._load_example(2, persist=False, source_factory=fake_source))
        self.assertEqual(len(self.player.sources), 2)
        self.assertEqual(len(self.player.profiles), 2)
        self.assertEqual(len(self.player.ai_list), 0)
        self.assertEqual(len(self.player.partner_profiles), 1)
        self.assertEqual(len(self.player.partner_list), 0)
        self.assertEqual(len(self.player.prop_list), 0)
        self.assertEqual(len(self.player.bg_layers), 6)
        self.assertTrue(all(layer["img"] is not None for layer in self.player.bg_layers))
        self.assertEqual(self.player.profiles[0].mappings["POWERBOMB"][-1], [0, "PowerBomb_End"])
        self.assertEqual(self.player.profiles[1].mappings["ComboAttack_4"][-1], [1, "ComboAttack_4"])
        self.assertEqual(self.player.cam_v_offset, -100.0)

    def test_distinct_parallax_factors_produce_distinct_camera_deltas(self):
        layers = ase_viewer.example_preset(2)["bg_layers"]
        camera_delta = 120
        deltas = [camera_delta * layer["parallax"] for layer in layers]
        self.assertEqual(len(set(deltas)), 6)
        self.assertEqual(deltas[0], 0)
        self.assertEqual(deltas[-1], camera_delta)

    def test_add_source_distinguishes_index_zero_from_failure(self):
        with mock.patch.object(self.player, "_create_source", return_value=fake_source("ok.aseprite", 0)):
            self.player.sources = []
            self.assertEqual(self.player.add_source("ok.aseprite"), 0)
        with mock.patch.object(self.player, "_create_source", side_effect=ase_viewer.AsepriteError("failed")), mock.patch("ase_viewer.show_user_error"):
            self.assertIsNone(self.player.add_source("bad.aseprite"))
        self.assertEqual(len(self.player.sources), 1)


@requires_internal_examples
class ExampleIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            ase_viewer.ase_manager.get_path(allow_prompt=False)
        except ase_viewer.AsepriteError as exc:
            raise unittest.SkipTest(str(exc))

    def setUp(self):
        ase_viewer.pygame.init()
        self.screen = ase_viewer.pygame.display.set_mode((960, 640))
        self.temp_dir = tempfile.TemporaryDirectory()
        self.player = ase_viewer.AsepritePlayer(
            project_path=str(Path(self.temp_dir.name) / "project.json"),
            settings_path=str(Path(self.temp_dir.name) / "settings.json"),
        )

    def tearDown(self):
        self.temp_dir.cleanup()
        ase_viewer.pygame.quit()

    def test_real_sources_prepare_both_examples_and_ex2_renders_parallax(self):
        self.assertTrue(self.player._load_example(1, persist=False))
        self.assertEqual(
            (
                len(self.player.sources), len(self.player.profiles),
                len(self.player.partner_profiles), len(self.player.ai_list),
                len(self.player.bg_layers),
            ),
            (2, 2, 1, 0, 1),
        )

        self.assertTrue(self.player._load_example(2, persist=False))
        self.assertEqual(
            (
                len(self.player.sources), len(self.player.profiles),
                len(self.player.partner_profiles), len(self.player.ai_list),
                len(self.player.prop_list), len(self.player.bg_layers),
            ),
            (2, 2, 1, 0, 0, 6),
        )
        self.screen.fill(self.player.bg_color)
        self.player.draw(self.screen, 800, 570)
        before = ase_viewer.pygame.image.tostring(self.screen, "RGB")
        self.player.cam_x += 120
        self.screen.fill(self.player.bg_color)
        self.player.draw(self.screen, 800, 570)
        after = ase_viewer.pygame.image.tostring(self.screen, "RGB")
        self.assertNotEqual(hashlib.sha256(before).digest(), hashlib.sha256(after).digest())
        self.assertFalse(Path(self.player.project_path).exists())
        self.assertFalse(Path(self.player.settings_path).exists())


if __name__ == "__main__":
    unittest.main()
