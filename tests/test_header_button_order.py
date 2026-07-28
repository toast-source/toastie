import unittest
from types import SimpleNamespace

import pygame

import ase_viewer


class HeaderButtonOrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.font.init()
        cls.fonts = (
            ase_viewer.create_ui_font(12),
            ase_viewer.create_ui_font(14, bold=True),
        )

    @classmethod
    def tearDownClass(cls):
        pygame.font.quit()

    def test_display_order_maps_to_existing_internal_modes(self):
        buttons = ase_viewer.sidebar_navigation_button_rects(650)
        expected = (
            ase_viewer.SIDEBAR_MAPPING,
            ase_viewer.SIDEBAR_SCENE,
            ase_viewer.SIDEBAR_RESOURCES,
            ase_viewer.SIDEBAR_SETTINGS,
        )
        self.assertEqual(
            [
                ase_viewer.sidebar_header_click_target(button.center, *buttons)
                for button in buttons
            ],
            list(expected),
        )
        self.assertTrue(all(
            first.right <= second.left
            for first, second in zip(buttons, buttons[1:])
        ))

    def test_labels_follow_tag_scene_resources_options_order(self):
        keys = (
            "sidebar.tag_setup", "sidebar.scene",
            "sidebar.resources", "sidebar.options",
        )
        self.assertEqual(
            [ase_viewer.tr(key, language="ko") for key in keys],
            ["태그 등록", "배치", "리소스", "옵션"],
        )
        self.assertEqual(
            [ase_viewer.tr(key, language="en") for key in keys],
            ["Tag Setup", "Scene", "Resources", "Options"],
        )

    def test_empty_project_draw_and_reclick_remain_safe(self):
        width, height = 1100, 720
        play_width = width - ase_viewer.SIDEBAR_WIDTH
        header, _content = ase_viewer.sidebar_rects(play_width, height)
        buttons = ase_viewer.sidebar_navigation_button_rects(play_width)
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        player = SimpleNamespace(
            sources=[], profiles=[], ai_list=[], prop_list=[],
            partner_profiles=[], partner_list=[], cur_profile_idx=0,
            cur_source_idx=0, selected_scene_actor_key=None,
            scene_object_filter=ase_viewer.SCENE_FILTER_ALL,
            language="ko", visible=False,
        )
        result = ase_viewer.draw_sidebar_header(
            surface, player, ase_viewer.SIDEBAR_SETTINGS,
            *buttons, self.fonts, [], header,
        )
        self.assertTrue(all(
            header.contains(result[key])
            for key in (
                "mapping_button", "scene_button",
                "resource_button", "settings_button",
            )
        ))
        self.assertEqual(
            ase_viewer.set_sidebar_mode(
                ase_viewer.SIDEBAR_SETTINGS,
                ase_viewer.SIDEBAR_SETTINGS,
            ),
            ase_viewer.SIDEBAR_SETTINGS,
        )


if __name__ == "__main__":
    unittest.main()
