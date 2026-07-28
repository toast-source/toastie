import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


class RenderCacheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_cached_font_reuses_surface_and_is_bounded(self):
        cached = ase_viewer.CachedFont(pygame.font.Font(None, 14), max_cache_size=8)
        first = cached.render("same", True, (255, 255, 255))
        second = cached.render("same", True, (255, 255, 255))
        self.assertIs(first, second)
        for index in range(50):
            cached.render(f"FPS {index}", True, (255, 255, 255))
        self.assertLessEqual(len(cached.cache), 8)

    def test_language_change_clears_text_and_layout_caches(self):
        original = ase_viewer._CURRENT_LANGUAGE
        font = ase_viewer.create_ui_font(13)
        font.render("cached", True, (255, 255, 255))
        ase_viewer.measure_ui_text("cached", font)
        self.assertGreater(len(font.cache), 0)
        self.assertGreater(len(ase_viewer._UI_LAYOUT_CACHE), 0)
        try:
            next_language = "en" if original == "ko" else "ko"
            ase_viewer.set_current_language(next_language)
            self.assertEqual(len(font.cache), 0)
            self.assertEqual(len(ase_viewer._UI_LAYOUT_CACHE), 0)
        finally:
            ase_viewer.set_current_language(original)

    def test_window_size_change_invalidates_layout_once(self):
        font = ase_viewer.create_ui_font(12)
        ase_viewer.invalidate_ui_layout_for_window_size((800, 600))
        ase_viewer.measure_ui_text("layout", font)
        self.assertGreater(len(ase_viewer._UI_LAYOUT_CACHE), 0)
        self.assertFalse(ase_viewer.invalidate_ui_layout_for_window_size((800, 600)))
        self.assertGreater(len(ase_viewer._UI_LAYOUT_CACHE), 0)
        self.assertTrue(ase_viewer.invalidate_ui_layout_for_window_size((801, 600)))
        self.assertEqual(len(ase_viewer._UI_LAYOUT_CACHE), 0)

    def test_source_revision_is_part_of_bounded_animation_cache_key(self):
        source = ase_viewer.AseSource.__new__(ase_viewer.AseSource)
        source.frames = [{"img": pygame.Surface((4, 4), pygame.SRCALPHA)}]
        source.source_revision = 1
        source.cache = ase_viewer.LimitedLRU(3)
        first = source.get_frame(0, 2, True)
        self.assertIs(first, source.get_frame(0, 2, True))
        source.source_revision = 2
        second = source.get_frame(0, 2, True)
        self.assertIsNot(first, second)
        for zoom in (1, 2, 3, 4, 5):
            source.get_frame(0, zoom, True)
        self.assertLessEqual(len(source.cache), 3)

    def test_layout_helpers_reuse_cached_results(self):
        font = ase_viewer.create_ui_font(12)
        ase_viewer._UI_LAYOUT_CACHE.clear()
        first = ase_viewer.wrap_ui_text("same wrapped label", font, 80)
        cache_size = len(ase_viewer._UI_LAYOUT_CACHE)
        second = ase_viewer.wrap_ui_text("same wrapped label", font, 80)
        self.assertEqual(first, second)
        self.assertEqual(len(ase_viewer._UI_LAYOUT_CACHE), cache_size)


if __name__ == "__main__":
    unittest.main()
