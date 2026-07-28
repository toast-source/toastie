import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


class TooltipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_hover_delay_then_visibility_and_hover_end(self):
        controller = ase_viewer.TooltipController(delay_ms=400)
        regions = [(pygame.Rect(10, 10, 80, 30), "tooltip.project.new")]
        self.assertIsNone(controller.update(regions, (20, 20), 100))
        self.assertIsNone(controller.update(regions, (20, 20), 499))
        self.assertEqual(controller.update(regions, (20, 20), 500), "tooltip.project.new")
        self.assertIsNone(controller.update(regions, (200, 200), 501))
        self.assertIsNone(controller.hovered_key)

    def test_new_region_restarts_delay(self):
        controller = ase_viewer.TooltipController(delay_ms=400)
        regions = [
            (pygame.Rect(0, 0, 50, 50), "tooltip.project.new"),
            (pygame.Rect(60, 0, 50, 50), "tooltip.project.save"),
        ]
        controller.update(regions, (10, 10), 0)
        self.assertEqual(controller.update(regions, (10, 10), 400), "tooltip.project.new")
        self.assertIsNone(controller.update(regions, (70, 10), 401))
        self.assertIsNone(controller.update(regions, (70, 10), 800))
        self.assertEqual(controller.update(regions, (70, 10), 801), "tooltip.project.save")

    def test_modal_or_drag_block_resets_tooltip(self):
        controller = ase_viewer.TooltipController(delay_ms=0)
        regions = [(pygame.Rect(0, 0, 50, 50), "tooltip.options")]
        controller.update(regions, (10, 10), 0)
        self.assertEqual(controller.update(regions, (10, 10), 1), "tooltip.options")
        self.assertIsNone(controller.update(regions, (10, 10), 2, blocked=True))
        self.assertIsNone(controller.hovered_key)

    def test_tooltip_rect_flips_at_right_and_bottom_edges(self):
        rect = ase_viewer.calculate_tooltip_rect((790, 590), (220, 100), (800, 600))
        self.assertLess(rect.right, 800)
        self.assertLess(rect.bottom, 600)
        self.assertLess(rect.left, 790)
        self.assertLess(rect.top, 590)

    def test_tooltip_rect_is_clamped_for_oversized_content(self):
        rect = ase_viewer.calculate_tooltip_rect((1, 1), (300, 100), (320, 200))
        self.assertGreaterEqual(rect.left, 8)
        self.assertGreaterEqual(rect.top, 8)
        self.assertLessEqual(rect.right, 312)
        self.assertLessEqual(rect.bottom, 192)

    def test_language_change_affects_next_tooltip_text(self):
        korean = ase_viewer.tr("tooltip.project.save", language="ko")
        english = ase_viewer.tr("tooltip.project.save", language="en")
        self.assertIn("JSON", korean)
        self.assertIn("JSON", english)
        self.assertNotEqual(korean, english)

    def test_resource_required_tooltip_exists_in_both_languages(self):
        self.assertIn("리소스", ase_viewer.tr("tooltip.resource_required", language="ko"))
        self.assertIn("resource", ase_viewer.tr("tooltip.resource_required", language="en").lower())

    def test_regions_do_not_accumulate_between_frame_lists(self):
        first_frame = []
        ase_viewer.register_tooltip(
            first_frame, pygame.Rect(0, 0, 20, 20), "tooltip.options",
        )
        second_frame = []
        ase_viewer.register_tooltip(
            second_frame, pygame.Rect(30, 0, 20, 20), "tooltip.project.save",
        )
        self.assertEqual(len(first_frame), 1)
        self.assertEqual(len(second_frame), 1)
        self.assertNotEqual(first_frame[0][1], second_frame[0][1])

    def test_delay_does_not_render_and_same_tooltip_reuses_surfaces(self):
        controller = ase_viewer.TooltipController(delay_ms=400)
        regions = [(pygame.Rect(0, 0, 50, 50), "tooltip.options")]
        font = ase_viewer.CachedFont(pygame.font.Font(None, 14), max_cache_size=32)
        controller.update(regions, (10, 10), 0)
        controller.update(regions, (10, 10), 399)
        self.assertEqual(len(font.cache), 0)

        surface = pygame.Surface((500, 300), pygame.SRCALPHA)
        text = ase_viewer.tr("tooltip.options", language="en")
        ase_viewer.render_tooltip(surface, font, text, (20, 20))
        cache_size = len(font.cache)
        ase_viewer.render_tooltip(surface, font, text, (20, 20))
        self.assertEqual(len(font.cache), cache_size)


if __name__ == "__main__":
    unittest.main()
