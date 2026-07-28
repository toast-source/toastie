import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import ase_viewer


def layer(name, parallax=0.25, enabled=True, **overrides):
    data = {
        "name": name,
        "path": rf"C:\Art\{name}.png",
        "parallax": parallax,
        "off_x": 120,
        "off_y": -40,
        "zoom": 3,
        "enabled": enabled,
    }
    data.update(overrides)
    return data


class ShareFormatTests(unittest.TestCase):
    def test_slack_uses_two_aligned_tables_with_unicode_width(self):
        text = ase_viewer.build_unity_parallax_export(
            [layer("Sky"), layer("한글 배경"), layer("LongerCloudName")],
            100,
            output_format="slack",
            language="en",
        )
        body = text.split("```", 2)[1]
        sections = body.strip().split("\n\n")
        self.assertGreaterEqual(len(sections), 2)
        first_table = sections[0].splitlines()
        second_table = sections[1].splitlines()
        self.assertEqual(len({ase_viewer.display_width(line) for line in first_table}), 1)
        self.assertEqual(len({ase_viewer.display_width(line) for line in second_table}), 1)
        self.assertIn("P", first_table[0])
        self.assertIn("FOLLOW", first_table[0])
        self.assertIn("OFFSET X/Y", second_table[0])
        self.assertIn("SCALE X/Y", second_table[0])

    def test_slack_long_names_have_mapping_and_very_long_names_use_cards(self):
        long_name = "Very_Long_Background_Layer_Final_V03"
        table_text = ase_viewer.build_unity_parallax_export(
            [layer(long_name)], 100, output_format="slack", language="en",
        )
        self.assertIn("Names", table_text)
        self.assertIn("…", table_text)
        self.assertIn(long_name, table_text)

        very_long_name = "Background_" + ("ExtremelyLong" * 5)
        card_text = ase_viewer.build_unity_parallax_export(
            [layer(very_long_name)], 100, output_format="slack", language="en",
        )
        self.assertIn("[01]", card_text)
        self.assertIn("P 0.25 → Follow 0.75", card_text)
        self.assertNotIn("OFFSET X/Y", card_text)

    def test_slack_fence_survives_backticks_in_layer_name(self):
        text = ase_viewer.build_unity_parallax_export(
            [layer("Sky```Final")], 100, output_format="slack", language="en",
        )
        self.assertIn("````\n", text)
        self.assertTrue(text.endswith("````"))
        self.assertIn("Sky```Final", text)

    def test_slack_independent_axes_use_card_values(self):
        converted = ase_viewer.convert_layer_to_unity_parallax(layer("Split"), 100, 0)
        converted["viewer_parallax_y"] = 0.5
        converted["unity_camera_follow_y"] = 0.5
        text = ase_viewer.build_slack_unity_parallax_export(
            [converted], 100, language="en",
        )
        self.assertIn("[01] Split", text)
        self.assertIn("P X/Y 0.25, 0.5 → Follow X/Y 0.75, 0.5", text)

    def test_markdown_has_two_tables_and_escapes_cells(self):
        text = ase_viewer.build_unity_parallax_export(
            [layer(" Sky | Final\\A\nB\tC ", enabled=False)],
            100,
            output_format="markdown",
            language="en",
        )
        self.assertIn("### Parallax", text)
        self.assertIn("### Transform", text)
        self.assertEqual(text.count("| Layer |"), 2)
        self.assertIn(r"Sky \| Final\\A B C", text)
        self.assertIn("| No |", text)
        self.assertIn("### Sources", text)

    def test_markdown_languages_keep_the_same_numeric_values(self):
        layers = [layer("배경", parallax=0.1234)]
        korean = ase_viewer.build_unity_parallax_export(
            layers, 100, output_format="markdown", language="ko",
        )
        english = ase_viewer.build_unity_parallax_export(
            layers, 100, output_format="markdown", language="en",
        )
        for value in ("0.1234", "0.8766", "1.2", "0.4", "1.5"):
            self.assertIn(value, korean)
            self.assertIn(value, english)

    def test_disabled_filter_applies_to_markdown(self):
        layers = [layer("On"), layer("Off", enabled=False)]
        included = ase_viewer.build_unity_parallax_export(
            layers, 100, output_format="markdown", include_disabled=True,
        )
        active_only = ase_viewer.build_unity_parallax_export(
            layers, 100, output_format="markdown", include_disabled=False,
        )
        self.assertIn("Off", included)
        self.assertNotIn("| Off |", active_only)

    def test_tsv_is_pure_tabular_data_and_normalizes_names(self):
        text = ase_viewer.build_unity_parallax_export(
            [layer("Sky\tFinal\nV2")], 100, output_format="tsv", language="en",
        )
        rows = text.splitlines()
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(rows[0].split("\t")), 9)
        self.assertEqual(len(rows[1].split("\t")), 9)
        self.assertEqual(rows[1].split("\t")[0], "Sky Final V2")
        self.assertEqual(
            rows[1].split("\t")[1:],
            ["0", "Yes", "0.25", "0.75", "1.2", "0.4", "1.5", "1.5"],
        )
        self.assertNotIn("```", text)
        self.assertNotIn("|---", text)
        self.assertNotIn("Pixels Per Unit", text)


if __name__ == "__main__":
    unittest.main()
