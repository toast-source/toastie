import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


class SidebarClippingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))
        cls.font = ase_viewer.create_ui_font(12)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_header_and_content_are_disjoint_at_supported_sizes(self):
        for size in ((1100, 720), (2048, 1118), (1350, 760)):
            with self.subTest(size=size):
                play_width = size[0] - ase_viewer.SIDEBAR_WIDTH
                header, content = ase_viewer.sidebar_rects(play_width, size[1])
                self.assertEqual(header.bottom, ase_viewer.TOP_UI_HEIGHT)
                self.assertEqual(content.top, ase_viewer.TOP_UI_HEIGHT)
                self.assertFalse(header.colliderect(content))
                self.assertEqual(content.bottom, size[1])

    def test_scrolled_controls_and_tooltips_are_clipped_below_header(self):
        surface = pygame.Surface((2048, 1118), pygame.SRCALPHA)
        play_width = 2048 - ase_viewer.SIDEBAR_WIDTH
        header, content = ase_viewer.sidebar_rects(play_width, 1118)
        for scroll in (0, -100, -600):
            with self.subTest(scroll=scroll):
                regions = []
                controls = ase_viewer._draw_sidebar_check_settings(
                    surface, content, scroll, self.font, regions,
                )
                self.assertTrue(all(content.contains(rect) for rect in controls))
                self.assertTrue(all(not header.colliderect(rect) for rect in controls))
                self.assertTrue(all(content.contains(rect) for rect, _key in regions))
                self.assertTrue(all(not header.colliderect(rect) for rect, _key in regions))

    def test_hidden_control_cannot_be_hit_through_header(self):
        play_width = 650
        header, content = ase_viewer.sidebar_rects(play_width, 720)
        hidden_local = pygame.Rect(10, -30, 200, 20)
        self.assertIsNone(
            ase_viewer.clipped_global_rect(
                hidden_local, content.topleft, content,
            )
        )
        self.assertFalse(
            ase_viewer.sidebar_control_hit(
                hidden_local, (play_width + 20, 20),
                content.topleft, content,
            )
        )
        self.assertTrue(header.collidepoint(play_width + 20, 20))

    def test_scroll_clamp_uses_content_viewport_height(self):
        content_height = 1800
        for window_height in (720, 1118, 800):
            viewport_height = window_height - ase_viewer.TOP_UI_HEIGHT
            minimum = -(content_height - viewport_height)
            self.assertEqual(
                ase_viewer.clamp_settings_scroll(
                    -99999, content_height, viewport_height,
                ),
                minimum,
            )
            self.assertEqual(
                ase_viewer.clamp_settings_scroll(
                    100, content_height, viewport_height,
                ),
                0,
            )


if __name__ == "__main__":
    unittest.main()
