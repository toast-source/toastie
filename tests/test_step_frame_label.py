import unittest

import ase_viewer


class StepFrameLabelTests(unittest.TestCase):
    def tearDown(self):
        ase_viewer.set_current_language(ase_viewer.LANG_KO)

    def test_o_guide_names_single_frame_and_has_help_in_both_languages(self):
        for language, expected in (
            (ase_viewer.LANG_KO, "1프레임 진행"),
            (ase_viewer.LANG_EN, "Step 1 frame"),
        ):
            ase_viewer.set_current_language(language)
            groups = ase_viewer.bottom_key_guide_groups(
                type("Player", (), {"key_map": {}})(),
            )
            app = next(group for group in groups if group["id"] == "app")
            item = next(item for item in app["items"] if item[0] == "O")
            self.assertEqual(item[1], expected)
            self.assertEqual(item[2], "tooltip.guide.step")
            self.assertTrue(ase_viewer.tr("tooltip.guide.step"))


if __name__ == "__main__":
    unittest.main()
