import unittest

import ase_viewer


class SettingsViewDebugSectionTests(unittest.TestCase):
    def test_view_section_keeps_real_app_shortcuts_discoverable(self):
        model = ase_viewer.settings_section_model(
            ase_viewer.SETTINGS_SECTION_VIEW_BACKGROUND,
        )
        self.assertEqual(
            model["categories"],
            ("BG IMAGE", "BG COLOR", "CAMERA"),
        )
        text = " ".join(
            ase_viewer.tr(key, language="en")
            for key in model["info_keys"]
        )
        for shortcut in ("F10", "H", "Right-drag", "F"):
            self.assertIn(shortcut, text)

    def test_quick_and_advanced_are_not_exposed_tabs(self):
        self.assertNotIn("quick", ase_viewer.SETTINGS_SECTIONS)
        self.assertNotIn("advanced", ase_viewer.SETTINGS_SECTIONS)


if __name__ == "__main__":
    unittest.main()
