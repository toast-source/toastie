import unittest
from types import SimpleNamespace

import ase_viewer


def fixture():
    sources = [
        SimpleNamespace(name="Hero.aseprite"),
        SimpleNamespace(name="SporeHeart.aseprite"),
        SimpleNamespace(name="Barrel.aseprite"),
    ]
    profiles = [
        SimpleNamespace(name="PLAYER", source_idx=0, kind="player"),
        SimpleNamespace(name="PARTNER_1", source_idx=1, kind="partner"),
        SimpleNamespace(name="NPC_2", source_idx=1, kind="npc"),
        SimpleNamespace(name="PROP_3", source_idx=2, kind="prop", is_prop_profile=True),
    ]
    partner = SimpleNamespace(
        profile=profiles[1], visible=True, is_dead=False,
        is_corpse=False, decision="IDLE", is_partner=True,
    )
    living = SimpleNamespace(
        profile=profiles[2], visible=True, is_dead=False,
        is_corpse=False, decision="IDLE",
    )
    corpse = SimpleNamespace(
        profile=profiles[2], visible=True, is_dead=True,
        is_corpse=True, decision="DEAD",
    )
    prop = SimpleNamespace(
        profile=profiles[3], visible=True, is_dead=False, is_corpse=False,
    )
    player = SimpleNamespace(
        sources=sources, profiles=profiles,
        partner_list=[partner], ai_list=[living, corpse], prop_list=[prop],
        cur_profile_idx=2, cur_source_idx=1,
        selected_scene_actor_key=("npc", id(living)),
        scene_object_filter=ase_viewer.SCENE_FILTER_ALL,
        scene_status_message="", language="ko", visible=True,
    )
    return player, partner, living, corpse, prop


class SceneObjectFilterTests(unittest.TestCase):
    def test_each_filter_returns_only_its_display_rows(self):
        player, _partner, _living, _corpse, _prop = fixture()
        all_rows = ase_viewer.build_scene_actor_rows(player)
        expected = {
            "all": ["player", "npc", "npc", "prop"],
            "player": ["player"],
            "npc": ["npc"],
            "prop": ["prop"],
            "corpse": ["npc"],
        }
        for filter_name, kinds in expected.items():
            with self.subTest(filter_name=filter_name):
                rows = ase_viewer.filter_scene_actor_rows(all_rows, filter_name)
                self.assertEqual([row["kind"] for row in rows], kinds)
                if filter_name == "npc":
                    self.assertFalse(rows[0]["is_corpse"])
                if filter_name == "corpse":
                    self.assertTrue(rows[0]["is_corpse"])

    def test_filter_does_not_mutate_data_names_or_global_numbering(self):
        player, partner, living, corpse, prop = fixture()
        original_ai = list(player.ai_list)
        original_props = list(player.prop_list)
        original_names = [profile.name for profile in player.profiles]
        rows = ase_viewer.build_scene_actor_rows(player)
        corpse_row = ase_viewer.filter_scene_actor_rows(rows, "corpse")[0]
        self.assertEqual(corpse_row["badge_text"], "NPC 02 · CORPSE")
        self.assertEqual(player.ai_list, original_ai)
        self.assertEqual(player.prop_list, original_props)
        self.assertEqual(player.partner_list, [partner])
        self.assertEqual([profile.name for profile in player.profiles], original_names)

    def test_hidden_selection_is_retained_across_filter_changes(self):
        player, _partner, living, _corpse, _prop = fixture()
        selected_key = ("npc", id(living))
        ase_viewer.set_scene_object_filter(player, "prop")
        self.assertEqual(player.selected_scene_actor_key, selected_key)
        self.assertEqual(
            player.scene_status_message,
            ase_viewer.tr("selection.hidden_by_filter"),
        )
        ase_viewer.set_scene_object_filter(player, "all")
        self.assertEqual(player.selected_scene_actor_key, selected_key)
        self.assertEqual(player.scene_status_message, "")

    def test_empty_project_filters_and_bilingual_labels_are_safe(self):
        player = SimpleNamespace(
            sources=[], profiles=[], ai_list=[], prop_list=[],
            cur_profile_idx=0, cur_source_idx=0,
            selected_scene_actor_key=None, scene_status_message="",
            language="ko", visible=False,
        )
        for filter_name in ase_viewer.SCENE_OBJECT_FILTERS:
            self.assertEqual(
                ase_viewer.set_scene_object_filter(player, filter_name),
                filter_name,
            )
            self.assertEqual(ase_viewer.scene_rows_for_current_filter(player), [])
            self.assertTrue(ase_viewer.tr(f"selection.filter.{filter_name}", language="ko"))
            self.assertTrue(ase_viewer.tr(f"selection.filter.{filter_name}", language="en"))


if __name__ == "__main__":
    unittest.main()
