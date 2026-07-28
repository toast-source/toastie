import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


class UiLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))
        cls.font = ase_viewer.create_ui_font(14, bold=True)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_korean_new_project_fits_with_padding(self):
        label = ase_viewer.tr("common.new", language="ko")
        width = ase_viewer.calculate_button_width(label, self.font, 60, horizontal_padding=14)
        text_width, _ = ase_viewer.measure_ui_text(label, self.font)
        self.assertGreaterEqual(width, text_width + 28)

    def test_english_new_project_uses_same_measurement(self):
        label = ase_viewer.tr("common.new", language="en")
        self.assertEqual(label, "New Project")
        width = ase_viewer.calculate_button_width(label, self.font, 60, horizontal_padding=14)
        self.assertGreaterEqual(width, self.font.size(label)[0] + 28)

    def test_minimum_and_maximum_widths(self):
        self.assertEqual(ase_viewer.calculate_button_width("A", self.font, 80), 80)
        self.assertEqual(
            ase_viewer.calculate_button_width("Very long translated label", self.font, 40, maximum_width=90),
            90,
        )

    def test_row_layout_keeps_gap_and_prevents_overlap(self):
        rects = ase_viewer.layout_button_row(
            [("새로 만들기", 60, 125), ("불러오기", 60, 110), ("저장", 60, 100)],
            self.font, 10, 5, gap=5,
        )
        self.assertEqual(len(rects), 3)
        self.assertGreaterEqual(rects[1].left - rects[0].right, 5)
        self.assertGreaterEqual(rects[2].left - rects[1].right, 5)

    def test_wrap_splits_korean_and_long_unbroken_text_safely(self):
        max_width = self.font.size("한국어도")[0]
        lines = ase_viewer.wrap_ui_text("한국어도공백없이안전하게분할", self.font, max_width)
        self.assertGreater(len(lines), 1)
        self.assertTrue(all(self.font.size(line)[0] <= max_width for line in lines))

    def test_path_ellipsis_preserves_filename_end(self):
        shortened = ase_viewer.ellipsize_path(
            r"C:\Users\Artist\Desktop\AI\SporeHeart.aseprite",
            self.font,
            self.font.size(r"...\SporeHeart.aseprite")[0],
        )
        self.assertTrue(shortened.startswith("..."))
        self.assertTrue(shortened.endswith("SporeHeart.aseprite"))

    def test_selection_labels_fit_their_measured_buttons(self):
        for key in (
            "selection.current", "selection.scene", "selection.resources",
            "selection.use_player", "selection.spawn_npc",
            "selection.place_prop", "selection.export_png",
        ):
            label = ase_viewer.tr(key, language="ko")
            width = ase_viewer.calculate_button_width(label, self.font, 60, horizontal_padding=10)
            self.assertGreaterEqual(width, self.font.size(label)[0] + 20)

    def test_visible_row_range_clamps_after_list_shrinks(self):
        _, _, old_offset, _ = ase_viewer.visible_row_range(50, 2000, 420, 42)
        self.assertGreater(old_offset, 0)
        start, end, new_offset, maximum = ase_viewer.visible_row_range(2, old_offset, 420, 42)
        self.assertEqual((start, end, new_offset, maximum), (0, 2, 0, 0))

    def test_sidebar_header_layout_at_minimum_and_reference_window(self):
        for width, height in ((1100, 720), (2048, 1118)):
            play_width = width - ase_viewer.SIDEBAR_WIDTH
            header, content = ase_viewer.sidebar_rects(play_width, height)
            buttons = ase_viewer.sidebar_navigation_button_rects(play_width)
            self.assertTrue(all(header.contains(button) for button in buttons))
            for first, second in zip(buttons, buttons[1:]):
                self.assertLessEqual(first.right, second.left)
            self.assertEqual(content.height, height - ase_viewer.TOP_UI_HEIGHT)


if __name__ == "__main__":
    unittest.main()
