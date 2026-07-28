import os
import tempfile
import unittest
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


class EmptyProjectOptionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))
        cls.font = ase_viewer.create_ui_font(14, bold=True)
        cls.small_font = ase_viewer.create_ui_font(12)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        ase_viewer.set_current_language("ko")
        self.temp_dir = tempfile.TemporaryDirectory()
        self.player = ase_viewer.AsepritePlayer(
            project_path=os.path.join(self.temp_dir.name, "project.json"),
            settings_path=os.path.join(self.temp_dir.name, "settings.json"),
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initial_empty_state_has_clickable_options_rect(self):
        self.assertEqual(self.player.sources, [])
        self.assertEqual(self.player.profiles, [])
        rect = ase_viewer.calculate_options_button_rect(900, self.font)
        self.assertGreater(rect.width, 0)
        self.assertGreater(rect.centerx, 900)
        self.assertTrue(rect.collidepoint(rect.center))
        opened = ase_viewer.toggle_options_panel(False, rect, rect.center)
        self.assertTrue(opened)
        self.assertTrue(ase_viewer.should_render_sidebar(opened, self.player.profiles))

    def test_empty_project_sidebar_modes_are_not_profile_gated(self):
        mode = ase_viewer.SIDEBAR_MAPPING
        mode = ase_viewer.set_sidebar_mode(mode, ase_viewer.SIDEBAR_SETTINGS)
        self.assertEqual(mode, ase_viewer.SIDEBAR_SETTINGS)
        mode = ase_viewer.set_sidebar_mode(mode, ase_viewer.SIDEBAR_SCENE)
        self.assertEqual(mode, ase_viewer.SIDEBAR_SCENE)
        mode = ase_viewer.set_sidebar_mode(mode, ase_viewer.SIDEBAR_RESOURCES)
        self.assertEqual(mode, ase_viewer.SIDEBAR_RESOURCES)

    def test_korean_and_english_options_rects_match_click_geometry(self):
        for language in ("ko", "en"):
            with self.subTest(language=language):
                ase_viewer.set_current_language(language)
                rect = ase_viewer.calculate_options_button_rect(700, self.font)
                self.assertGreater(rect.left, 700)
                self.assertTrue(ase_viewer.toggle_options_panel(False, rect, rect.center))

    def test_global_options_remain_available_and_mutable(self):
        state = ase_viewer.options_availability(self.player)
        self.assertTrue(state["global"])
        self.assertFalse(state["layers"])
        self.player.language = ase_viewer.set_current_language("en")
        self.player.show_viewport = False
        self.player.dash_speed = 18.0
        self.assertEqual(self.player.language, "en")
        self.assertFalse(self.player.show_viewport)
        self.assertEqual(self.player.dash_speed, 18.0)

    def test_resource_options_are_disabled_and_notice_renders(self):
        state = ase_viewer.options_availability(self.player)
        self.assertFalse(state["layers"])
        surface = pygame.Surface((450, 100), pygame.SRCALPHA)
        panel = ase_viewer.draw_resource_required_notice(
            surface, self.small_font, pygame.Rect(20, 10, 410, 48),
        )
        self.assertEqual(panel.size, (410, 48))
        self.assertIn("리소스", ase_viewer.tr("ui.no_resource"))
        self.assertIn("리소스", ase_viewer.tr("tooltip.resource_required"))

    def test_options_state_survives_add_and_remove(self):
        show_options = True
        self.player.sources.append(SimpleNamespace(layers=[]))
        self.player.profiles.append(SimpleNamespace(kind="npc"))
        self.assertTrue(ase_viewer.options_availability(self.player)["layers"])
        self.assertTrue(ase_viewer.options_availability(self.player)["slice_status"])
        self.assertTrue(ase_viewer.should_render_sidebar(show_options, self.player.profiles))
        self.player.sources.clear()
        self.player.profiles.clear()
        self.assertFalse(ase_viewer.options_availability(self.player)["layers"])
        self.assertTrue(ase_viewer.should_render_sidebar(show_options, self.player.profiles))

    def test_empty_settings_height_and_scroll_are_safe(self):
        folds = {
            "LANGUAGE": True, "PROPS": True, "NPCS": True, "PHYSICS": True,
            "AI & COMBAT": True, "JUICE & VFX": True, "LAYERS": True,
            "CAMERA": True, "BG IMAGE": True, "BG COLOR": True,
            "CONTROLS": False,
        }
        height = ase_viewer.settings_content_height(self.player, folds)
        self.assertGreater(height, 0)
        scroll = ase_viewer.clamp_settings_scroll(-99999, height, 720)
        self.assertLessEqual(scroll, 0)
        self.assertGreaterEqual(scroll, -height)


if __name__ == "__main__":
    unittest.main()
