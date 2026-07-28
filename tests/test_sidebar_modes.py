import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


class SidebarModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))
        cls.font = ase_viewer.create_ui_font(14, bold=True)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_sidebar_buttons_are_in_sidebar_and_clickable_from_mapping(self):
        play_width = 1598
        buttons = ase_viewer.sidebar_navigation_button_rects(play_width)
        expected = (
            ase_viewer.SIDEBAR_MAPPING,
            ase_viewer.SIDEBAR_SCENE,
            ase_viewer.SIDEBAR_RESOURCES,
            ase_viewer.SIDEBAR_SETTINGS,
        )
        self.assertTrue(all(rect.centerx > play_width for rect in buttons))
        for button, mode in zip(buttons, expected):
            self.assertEqual(
                ase_viewer.sidebar_header_click_target(
                    button.center, *buttons,
                ),
                mode,
            )

    def test_modes_are_exclusive_and_same_button_stays_open(self):
        mode = ase_viewer.SIDEBAR_MAPPING
        for requested in (
            ase_viewer.SIDEBAR_SCENE,
            ase_viewer.SIDEBAR_RESOURCES,
            ase_viewer.SIDEBAR_SETTINGS,
        ):
            mode = ase_viewer.set_sidebar_mode(mode, requested)
            self.assertEqual(mode, requested)
            self.assertIn(mode, ase_viewer.SIDEBAR_MODES)
            mode = ase_viewer.set_sidebar_mode(mode, requested)
            self.assertEqual(mode, requested)

    def test_switching_between_open_modes_never_combines_state(self):
        mode = ase_viewer.set_sidebar_mode(
            ase_viewer.SIDEBAR_SETTINGS, ase_viewer.SIDEBAR_SCENE,
        )
        self.assertEqual(mode, ase_viewer.SIDEBAR_SCENE)
        mode = ase_viewer.set_sidebar_mode(
            mode, ase_viewer.SIDEBAR_RESOURCES,
        )
        self.assertEqual(mode, ase_viewer.SIDEBAR_RESOURCES)

    def test_empty_project_does_not_gate_header_clicks(self):
        play_width = 650
        buttons = ase_viewer.sidebar_navigation_button_rects(play_width)
        for rect, expected in zip(buttons, (
            ase_viewer.SIDEBAR_MAPPING,
            ase_viewer.SIDEBAR_SCENE,
            ase_viewer.SIDEBAR_RESOURCES,
            ase_viewer.SIDEBAR_SETTINGS,
        )):
            self.assertEqual(
                ase_viewer.sidebar_header_click_target(
                    rect.center, *buttons,
                ),
                expected,
            )


if __name__ == "__main__":
    unittest.main()
