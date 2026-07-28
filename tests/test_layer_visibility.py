import json
import os
import struct
import subprocess
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


def read_aseprite_layer_chunks(path):
    data = Path(path).read_bytes()
    if len(data) < 144 or struct.unpack_from("<H", data, 4)[0] != 0xA5E0:
        raise ValueError("not an Aseprite file")
    frame_count = struct.unpack_from("<H", data, 6)[0]
    position = 128
    layers = []
    for _ in range(frame_count):
        frame_size, frame_magic, old_chunk_count = struct.unpack_from("<IHH", data, position)
        if frame_magic != 0xF1FA:
            raise ValueError("invalid Aseprite frame")
        new_chunk_count = struct.unpack_from("<I", data, position + 12)[0]
        chunk_count = new_chunk_count or old_chunk_count
        chunk_position = position + 16
        for _ in range(chunk_count):
            chunk_size, chunk_type = struct.unpack_from("<IH", data, chunk_position)
            if chunk_type == 0x2004:
                payload = chunk_position + 6
                flags, layer_type, depth = struct.unpack_from("<HHH", data, payload)
                name_length = struct.unpack_from("<H", data, payload + 16)[0]
                name_start = payload + 18
                name = data[name_start:name_start + name_length].decode("utf-8")
                layers.append({
                    "name": name,
                    "depth": depth,
                    "is_group": layer_type == 1,
                    "visible": bool(flags & 1),
                    "is_reference": bool(flags & 64),
                    "is_tilemap": layer_type == 2,
                })
            chunk_position += chunk_size
        position += frame_size
    return layers


class LayerVisibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def make_source(self):
        source = ase_viewer.AseSource.__new__(ase_viewer.AseSource)
        source.file_path = "memory.aseprite"
        source.name = "memory.aseprite"
        source.layers = []
        source.visible_layer_keys = set()
        source.visible_layers = set()
        return source

    def entry(self, name, uuid, path=None, depth=0, visible=True, group=False, image=True):
        return {
            "name": name,
            "uuid": uuid,
            "path": path or name,
            "depth": depth,
            "stackIndex": 1,
            "visible": visible,
            "isGroup": group,
            "isImage": image,
            "isTilemap": False,
            "isReference": False,
        }

    def test_inventory_preserves_complete_original_order_and_hierarchy(self):
        source = self.make_source()
        inventory = [
            self.entry("Bottom", "1"),
            self.entry("Character", "2", group=True, image=False),
            self.entry("Body", "3", "Character/Body", 1),
            self.entry("Effects", "4", "Character/Effects", 1, visible=False),
            self.entry("Nested", "5", "Character/Nested", 1, group=True, image=False),
            self.entry("Empty", "6", "Character/Nested/Empty", 2),
            self.entry("Top", "7"),
        ]
        source._apply_layer_inventory(inventory)
        self.assertEqual([layer["path"] for layer in source.layers], [item["path"] for item in inventory])
        self.assertEqual([layer["depth"] for layer in source.layers], [0, 0, 1, 1, 1, 2, 0])
        self.assertEqual(len(source.layers), 7)
        self.assertNotIn("uuid:4", source.visible_layer_keys)
        self.assertIn("uuid:6", source.visible_layer_keys)

    def test_thirty_five_rows_keep_first_middle_last_and_scroll_to_end(self):
        source = self.make_source()
        inventory = [self.entry(f"Layer {index:02}", str(index)) for index in range(35)]
        source._apply_layer_inventory(inventory)
        self.assertEqual(source.layers[0]["name"], "Layer 00")
        self.assertEqual(source.layers[17]["name"], "Layer 17")
        self.assertEqual(source.layers[-1]["name"], "Layer 34")
        content_height = 60 + ase_viewer.layer_list_height(len(source.layers))
        viewport_height = 400
        minimum = ase_viewer.clamp_settings_scroll(
            -100000, content_height, viewport_height,
        )
        self.assertGreater(content_height, viewport_height)
        self.assertEqual(minimum, -(content_height - viewport_height))
        self.assertEqual(content_height + minimum, viewport_height)
        shrunk_height = 60 + ase_viewer.layer_list_height(2)
        self.assertEqual(
            ase_viewer.clamp_settings_scroll(
                minimum, shrunk_height, viewport_height,
            ),
            0,
        )

    def test_duplicate_names_toggle_independently_without_reordering(self):
        source = self.make_source()
        inventory = [
            self.entry("Effects", "a", "Character/Effects", 1),
            self.entry("Effects", "b", "Weapon/Effects", 1),
        ]
        source._apply_layer_inventory(inventory)
        original_order = [layer["key"] for layer in source.layers]
        source.set_layer_visibility("uuid:a", False)
        self.assertNotIn("uuid:a", source.visible_layer_keys)
        self.assertIn("uuid:b", source.visible_layer_keys)
        self.assertEqual([layer["key"] for layer in source.layers], original_order)
        source.set_layer_visibility("uuid:a", True)
        source.set_layer_visibility("uuid:b", False)
        self.assertIn("uuid:a", source.visible_layer_keys)
        self.assertNotIn("uuid:b", source.visible_layer_keys)
        source.set_layer_visibility("uuid:b", True)
        self.assertEqual(source.visible_layer_keys, {"uuid:a", "uuid:b"})

    def test_sources_with_same_layer_uuid_do_not_share_state(self):
        inventory = [self.entry("Effects", "same")]
        first = self.make_source()
        second = self.make_source()
        first._apply_layer_inventory(inventory)
        second._apply_layer_inventory(inventory)
        first.set_layer_visibility("uuid:same", False)
        self.assertNotIn("uuid:same", first.visible_layer_keys)
        self.assertIn("uuid:same", second.visible_layer_keys)

    def test_refresh_uses_uuid_for_rename_add_remove_and_preserves_order(self):
        source = self.make_source()
        source._apply_layer_inventory([
            self.entry("Old", "stable"),
            self.entry("Removed", "removed"),
        ])
        source.set_layer_visibility("uuid:stable", False)
        source._apply_layer_inventory([
            self.entry("Renamed", "stable"),
            self.entry("New", "new"),
        ])
        self.assertEqual([layer["name"] for layer in source.layers], ["Renamed", "New"])
        self.assertNotIn("uuid:stable", source.visible_layer_keys)
        self.assertIn("uuid:new", source.visible_layer_keys)
        self.assertNotIn("uuid:removed", source.visible_layer_keys)

    def test_refresh_falls_back_to_index_and_path_when_legacy_uuid_changes(self):
        source = self.make_source()
        source._apply_layer_inventory([self.entry("Body", "first-open", "Character/Body", 1)])
        source.set_layer_visibility("uuid:first-open", False)
        source._apply_layer_inventory([self.entry("Body", "second-open", "Character/Body", 1)])
        self.assertEqual(source.layers[0]["key"], "uuid:second-open")
        self.assertNotIn("uuid:second-open", source.visible_layer_keys)

    def test_fallback_key_uses_inventory_index_and_path(self):
        source = self.make_source()
        source._apply_layer_inventory([
            self.entry("Effects", "", "Character/Effects", 1),
            self.entry("Effects", "", "Weapon/Effects", 1),
        ])
        self.assertEqual(
            [layer["key"] for layer in source.layers],
            ["stack:0:Character/Effects", "stack:1:Weapon/Effects"],
        )

    def test_ambiguous_legacy_hidden_name_keeps_duplicates_visible(self):
        source = self.make_source()
        source.visible_layers = {"Body"}
        source._apply_layer_inventory([
            self.entry("Body", "body"),
            self.entry("Effects", "a"),
            self.entry("Effects", "b"),
        ])
        self.assertIn("uuid:body", source.visible_layer_keys)
        self.assertIn("uuid:a", source.visible_layer_keys)
        self.assertIn("uuid:b", source.visible_layer_keys)

    def test_invalid_key_is_ignored(self):
        source = self.make_source()
        source._apply_layer_inventory([self.entry("Body", "body")])
        self.assertFalse(source.set_layer_visibility("uuid:missing", False))
        self.assertEqual(source.visible_layer_keys, {"uuid:body"})

    def test_export_failure_preserves_previous_frames_inventory_and_mtime(self):
        source = self.make_source()
        old_surface = pygame.Surface((2, 2), pygame.SRCALPHA)
        source.frames = [{"img": old_surface, "ox": 0, "oy": 0, "duration": 100}]
        source.tags = {"Idle": (0, 0)}
        source.tag_metadata = {}
        source.slices = {}
        source.tag_list = ["Idle"]
        source.orig_w = source.orig_h = 2
        source.export_status = {"enabled": False, "reason": "test"}
        source.last_mtime = 1
        source._apply_layer_inventory([self.entry("Body", "body")])
        old_layers = list(source.layers)
        with mock.patch("ase_viewer.export_aseprite", side_effect=ase_viewer.AsepriteError("failure")):
            self.assertFalse(source.export_and_load())
        self.assertIs(source.frames[0]["img"], old_surface)
        self.assertEqual(source.layers, old_layers)
        with mock.patch("ase_viewer.os.path.getmtime", return_value=2), mock.patch.object(source, "export_and_load", return_value=False):
            self.assertFalse(source.check_for_reload())
        self.assertEqual(source.last_mtime, 1)

    def test_lua_inventory_is_separate_from_visibility_filter(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "source.aseprite"
            png_path = Path(temp_dir) / "sheet.png"
            json_path = Path(temp_dir) / "sheet.json"
            inventory_path = Path(temp_dir) / "layers.json"
            source_path.write_bytes(b"original")
            captured = {}

            def fake_run(arguments, executable=None, expected_files=(), timeout=None):
                captured["arguments"] = list(arguments)
                script_path = Path(arguments[arguments.index("--script") + 1])
                captured["script"] = script_path.read_text(encoding="utf-8")
                png_path.touch()
                json_path.write_text(json.dumps({"frames": [{"frame": {}, "spriteSourceSize": {}, "sourceSize": {}}]}), encoding="utf-8")
                inventory_path.write_text("[]", encoding="utf-8")
                return subprocess.CompletedProcess(arguments, 0)

            with mock.patch("ase_viewer.run_aseprite", side_effect=fake_run):
                ase_viewer.export_aseprite(
                    str(source_path),
                    str(png_path),
                    str(json_path),
                    executable="fake.exe",
                    layer_visibility={"uuid:a": False, "uuid:b": True},
                    inventory_path=str(inventory_path),
                )
            self.assertIn("table.insert(inventory, entry)", captured["script"])
            self.assertLess(captured["script"].index("table.insert(inventory, entry)"), captured["script"].index("item.layer.isVisible = desired"))
            self.assertNotIn("not hidden", captured["script"])
            visibility_arg = next(arg for arg in captured["arguments"] if arg.startswith("layer_visibility="))
            self.assertEqual(json.loads(visibility_arg.split("=", 1)[1]), {"uuid:a": False, "uuid:b": True})
            self.assertEqual(source_path.read_bytes(), b"original")

    def test_inventory_to_toggle_to_export_flow_keeps_rows_and_changes_only_requested_key(self):
        source = self.make_source()
        source.frames = []
        source.tags = {}
        source.tag_metadata = {}
        source.slices = {}
        source.tag_list = []
        source.orig_w = source.orig_h = 2
        source.export_status = {"enabled": False, "reason": "test"}
        inventory = [
            self.entry("Effects", "a", "Character/Effects", 1),
            self.entry("Effects", "b", "Weapon/Effects", 1),
        ]
        source._apply_layer_inventory(inventory)
        calls = []

        def fake_export(source_path, png_path, json_path, **kwargs):
            visibility = kwargs["layer_visibility"]
            calls.append(dict(visibility))
            image = pygame.Surface((2, 1), pygame.SRCALPHA)
            image.fill((0, 0, 0, 0))
            if visibility.get("uuid:a", True):
                image.set_at((0, 0), (255, 0, 0, 255))
            if visibility.get("uuid:b", True):
                image.set_at((1, 0), (0, 255, 0, 255))
            pygame.image.save(image, png_path)
            Path(kwargs["inventory_path"]).write_text(json.dumps(inventory), encoding="utf-8")
            return {
                "frames": [{
                    "frame": {"x": 0, "y": 0, "w": 2, "h": 1},
                    "spriteSourceSize": {"x": 0, "y": 0},
                    "sourceSize": {"w": 2, "h": 1},
                    "duration": 100,
                }],
                "meta": {},
            }

        with mock.patch("ase_viewer.export_aseprite", side_effect=fake_export):
            self.assertTrue(source.export_and_load())
            original = ase_viewer._source_render_digest(source)
            original_order = [layer["path"] for layer in source.layers]
            source.set_layer_visibility("uuid:a", False)
            self.assertTrue(source.export_and_load())
            self.assertEqual(calls[-1], {
                "uuid:a": False,
                "stack:0:Character/Effects": False,
                "uuid:b": True,
                "stack:1:Weapon/Effects": True,
            })
            self.assertEqual([layer["path"] for layer in source.layers], original_order)
            self.assertNotEqual(ase_viewer._source_render_digest(source), original)
            self.assertEqual(source.frames[0]["img"].get_at((0, 0)).a, 0)
            self.assertEqual(source.frames[0]["img"].get_at((1, 0)), pygame.Color(0, 255, 0, 255))
            source.set_layer_visibility("uuid:a", True)
            self.assertTrue(source.export_and_load())
            self.assertEqual(ase_viewer._source_render_digest(source), original)

    def test_source_removal_discards_only_removed_source_state(self):
        player = ase_viewer.AsepritePlayer(project_path="unused.json", settings_path="unused-settings.json")
        first = types.SimpleNamespace(id=0, kind="generic", is_prop_source=False, layers=[], visible_layer_keys={"uuid:first"})
        second = types.SimpleNamespace(id=1, kind="generic", is_prop_source=False, layers=[], visible_layer_keys={"uuid:second"})
        player.sources = [first, second]
        player.profiles = []
        player.remove_source_by_index(0)
        self.assertEqual(player.sources, [second])
        self.assertEqual(second.id, 0)
        self.assertEqual(second.visible_layer_keys, {"uuid:second"})


class LayerFixtureIntegrationTests(unittest.TestCase):
    def test_real_fixture_lua_inventory_matches_ordered_file_layer_chunks(self):
        fixture = Path(ase_viewer.APP_ROOT) / "resources" / "examples" / "shared" / "sources" / "Cailin_00_Public.aseprite"
        if not fixture.is_file():
            self.skipTest("Cailin fixture is unavailable")
        raw_layers = read_aseprite_layer_chunks(fixture)
        self.assertGreater(len(raw_layers), 0)
        try:
            ase_viewer.ase_manager.get_path(allow_prompt=False)
        except ase_viewer.AsepriteError:
            self.skipTest("Aseprite executable is unavailable")
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        pygame.init()
        pygame.display.set_mode((1, 1))
        try:
            source = ase_viewer.AseSource(str(fixture), 0)
        finally:
            pygame.quit()
        self.assertEqual(len(source.layers), len(raw_layers))
        self.assertEqual(
            [(layer["name"], layer["depth"], layer["is_group"]) for layer in source.layers],
            [(layer["name"], layer["depth"], layer["is_group"]) for layer in raw_layers],
        )
        self.assertEqual(ase_viewer.layer_inventory_summary(source.layers)["duplicate_keys"], 0)


if __name__ == "__main__":
    unittest.main()
