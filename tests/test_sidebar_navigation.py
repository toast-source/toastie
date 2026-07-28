import os
import unittest
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import ase_viewer


def empty_player(language="ko"):
    return SimpleNamespace(
        sources=[], profiles=[], ai_list=[], prop_list=[],
        partner_profiles=[], partner_list=[],
        cur_profile_idx=0, cur_source_idx=0,
        selected_scene_actor_key=None,
        scene_object_filter=ase_viewer.SCENE_FILTER_ALL,
        language=language, visible=False,
    )


class SidebarNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))
        cls.fonts = (
            ase_viewer.create_ui_font(12),
            ase_viewer.create_ui_font(14, bold=True),
        )

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_four_buttons_are_disjoint_clickable_and_idempotent(self):
        play_width = 650
        buttons = ase_viewer.sidebar_navigation_button_rects(play_width)
        modes = (
            ase_viewer.SIDEBAR_MAPPING,
            ase_viewer.SIDEBAR_SCENE,
            ase_viewer.SIDEBAR_RESOURCES,
            ase_viewer.SIDEBAR_SETTINGS,
        )
        self.assertEqual(len(buttons), 4)
        for index, (button, mode) in enumerate(zip(buttons, modes)):
            self.assertGreaterEqual(button.left, play_width)
            self.assertEqual(
                ase_viewer.sidebar_header_click_target(button.center, *buttons),
                mode,
            )
            self.assertEqual(ase_viewer.set_sidebar_mode(mode, mode), mode)
            for other in buttons[index + 1:]:
                self.assertFalse(button.colliderect(other))

    def test_mapping_is_active_and_reachable_in_empty_project(self):
        width, height = 1100, 720
        play_width = width - ase_viewer.SIDEBAR_WIDTH
        header, content = ase_viewer.sidebar_rects(play_width, height)
        buttons = ase_viewer.sidebar_navigation_button_rects(play_width)
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        regions = []
        result = ase_viewer.draw_sidebar_header(
            surface, empty_player(), ase_viewer.SIDEBAR_MAPPING,
            *buttons, self.fonts, regions, header,
        )
        self.assertEqual(
            surface.get_at(buttons[0].center)[:3], (59, 130, 246),
        )
        self.assertTrue(header.contains(result["mapping_button"]))
        intro = ase_viewer.draw_mapping_workspace_intro(
            surface, empty_player(), self.fonts, content,
        )
        self.assertTrue(intro["empty"])
        self.assertTrue(content.contains(intro["title_rect"]))
        self.assertFalse(header.colliderect(intro["title_rect"]))
        self.assertIn("리소스", " ".join(intro["lines"]))

    def test_placement_labels_keep_internal_scene_mode(self):
        self.assertEqual(ase_viewer.SIDEBAR_SCENE, "scene")
        self.assertEqual(ase_viewer.tr("sidebar.scene", language="ko"), "배치")
        self.assertNotEqual(ase_viewer.tr("sidebar.scene", language="ko"), "장면")
        self.assertEqual(ase_viewer.tr("sidebar.scene", language="en"), "Scene")
        self.assertEqual(
            ase_viewer.tr("selection.scene", language="ko"),
            "배치된 캐릭터·오브젝트",
        )
        self.assertEqual(
            ase_viewer.tr("selection.scene", language="en"),
            "Placed Characters & Objects",
        )

    def test_scene_mode_highlights_placement_button(self):
        width, height = 1100, 720
        play_width = width - ase_viewer.SIDEBAR_WIDTH
        header, _ = ase_viewer.sidebar_rects(play_width, height)
        buttons = ase_viewer.sidebar_navigation_button_rects(play_width)
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        ase_viewer.draw_sidebar_header(
            surface, empty_player(), ase_viewer.SIDEBAR_SCENE,
            *buttons, self.fonts, [], header,
        )
        self.assertEqual(surface.get_at(buttons[1].center)[:3], (59, 130, 246))
        self.assertEqual(
            ase_viewer.sidebar_header_click_target(buttons[1].center, *buttons),
            ase_viewer.SIDEBAR_SCENE,
        )

    def test_first_run_guidance_explains_flow_without_placing_partner(self):
        placement_ko = ase_viewer.tr("selection.empty_scene", language="ko")
        resources_ko = ase_viewer.tr("selection.empty_resources", language="ko")
        mapping_ko = ase_viewer.tr("mapping.empty.import", language="ko")
        self.assertIn("배치", placement_ko)
        self.assertIn("Player/NPC/Prop", placement_ko)
        self.assertNotIn("Partner", placement_ko)
        self.assertIn("태그 등록", resources_ko)
        self.assertIn("Player/NPC/Prop", resources_ko)
        self.assertIn("리소스 탭", mapping_ko)
        self.assertIn("태그와 애니메이션", mapping_ko)

    def test_korean_and_english_labels_fit_minimum_sidebar(self):
        play_width = 650
        buttons = ase_viewer.sidebar_navigation_button_rects(play_width)
        keys = (
            "sidebar.tag_setup", "sidebar.scene",
            "sidebar.resources", "sidebar.options",
        )
        for language in ("ko", "en"):
            for button, key in zip(buttons, keys):
                label = ase_viewer.tr(key, language=language)
                self.assertLessEqual(self.fonts[0].size(label)[0], button.w - 8)

    def test_mapping_copy_guides_source_only_project_to_role_and_tags(self):
        ase_viewer.set_current_language("en")
        player = empty_player("en")
        player.sources = [SimpleNamespace(name="Hero.aseprite")]
        copy_data = ase_viewer.mapping_workspace_copy(player)
        self.assertTrue(copy_data["empty"])
        text = " ".join(copy_data["lines"])
        self.assertIn("Tag Setup", ase_viewer.tr("sidebar.tag_setup", language="en"))
        self.assertIn("role", text.lower())
        self.assertIn("Partner", text)
        ase_viewer.set_current_language("ko")


if __name__ == "__main__":
    unittest.main()
