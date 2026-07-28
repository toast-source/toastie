import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import ase_viewer


class FakeClipboardRoot:
    def __init__(self, fail=False):
        self.fail = fail
        self.value = ""
        self.destroyed = False

    def withdraw(self):
        pass

    def clipboard_clear(self):
        self.value = ""

    def clipboard_append(self, text):
        if self.fail:
            raise OSError("clipboard unavailable")
        self.value = text

    def update(self):
        pass

    def destroy(self):
        self.destroyed = True


class ClipboardExportTests(unittest.TestCase):
    def test_copy_text_success_preserves_complete_text(self):
        root = FakeClipboardRoot()
        text = "Unity\n한글\n0.25"
        success, error = ase_viewer.copy_text_to_clipboard(text, tk_factory=lambda: root)
        self.assertTrue(success)
        self.assertEqual(error, "")
        self.assertEqual(root.value, text)
        self.assertTrue(root.destroyed)

    def test_copy_text_failure_is_caught_and_root_is_destroyed(self):
        root = FakeClipboardRoot(fail=True)
        success, error = ase_viewer.copy_text_to_clipboard("data", tk_factory=lambda: root)
        self.assertFalse(success)
        self.assertIn("clipboard unavailable", error)
        self.assertTrue(root.destroyed)

    def test_perform_export_passes_exact_generated_text_to_writer(self):
        captured = {}

        def writer(text):
            captured["text"] = text
            return True, ""

        layers = [{"name": "Sky", "path": "Sky.png", "parallax": 0.25, "zoom": 2}]
        result = ase_viewer.perform_unity_parallax_clipboard_export(
            layers, 100, language="en", clipboard_writer=writer,
        )
        self.assertTrue(result["success"])
        self.assertEqual(captured["text"], result["text"])
        self.assertIn("Sky", result["text"])
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["output_format"], "detailed")

    def test_selected_share_format_is_copied_without_text_loss(self):
        for output_format, marker in (
            ("slack", "```"),
            ("markdown", "## Unity Parallax Handoff"),
            ("tsv", "Layer\tOrder\tEnabled"),
        ):
            captured = {}

            def writer(text):
                captured["text"] = text
                return True, ""

            with self.subTest(output_format=output_format):
                result = ase_viewer.perform_unity_parallax_clipboard_export(
                    [{"name": "한글 Sky", "parallax": 0.25}],
                    100,
                    output_format=output_format,
                    language="en",
                    clipboard_writer=writer,
                )
                self.assertTrue(result["success"])
                self.assertEqual(result["output_format"], output_format)
                self.assertEqual(captured["text"], result["text"])
                self.assertIn(marker, result["text"])

    def test_writer_failure_and_empty_layers_do_not_raise(self):
        result = ase_viewer.perform_unity_parallax_clipboard_export(
            [{"name": "Sky"}], 100, clipboard_writer=lambda _text: (False, "busy"),
        )
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "busy")
        empty = ase_viewer.perform_unity_parallax_clipboard_export([], 100, language="en")
        self.assertFalse(empty["success"])
        self.assertIn("no background layers", empty["error"].lower())

    def test_invalid_ppu_does_not_call_writer(self):
        calls = []
        result = ase_viewer.perform_unity_parallax_clipboard_export(
            [{"name": "Sky"}], "NaN", clipboard_writer=lambda text: calls.append(text),
        )
        self.assertFalse(result["success"])
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
