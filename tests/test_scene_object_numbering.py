import os
import unittest
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import ase_viewer


def make_player():
    sources = [
        SimpleNamespace(name="Hero.aseprite"),
        SimpleNamespace(name="SporeHeart.aseprite"),
        SimpleNamespace(name="Pivot.aseprite"),
        SimpleNamespace(name="Barrel.aseprite"),
    ]
    profiles = [
        SimpleNamespace(name="PLAYER", source_idx=0, kind="player"),
        SimpleNamespace(name="NPC_1", source_idx=1, kind="npc"),
        SimpleNamespace(name="SporeHeart_04_pivot", source_idx=2, kind="npc"),
        SimpleNamespace(name="PROP_3", source_idx=3, kind="prop", is_prop_profile=True),
    ]
    ai_list = [
        SimpleNamespace(profile=profiles[1], visible=True, is_dead=False, is_corpse=False),
        SimpleNamespace(profile=profiles[2], visible=True, is_dead=False, is_corpse=False),
    ]
    prop_list = [
        SimpleNamespace(profile=profiles[3], visible=True, is_dead=False, is_corpse=False),
    ]
    return SimpleNamespace(
        sources=sources, profiles=profiles, ai_list=ai_list, prop_list=prop_list,
        cur_profile_idx=0, cur_source_idx=0, language="ko", visible=True,
    )


class SceneObjectNumberingTests(unittest.TestCase):
    def test_player_npc_and_prop_badges_use_scene_order(self):
        player = make_player()
        rows = ase_viewer.build_scene_actor_rows(player)
        self.assertEqual(
            [row["badge_text"] for row in rows],
            ["PLAYER", "NPC 01", "NPC 02", "PROP 01"],
        )

    def test_deleting_row_compacts_display_number_only(self):
        player = make_player()
        original_name = player.profiles[2].name
        original_source = player.sources[2].name
        player.ai_list.pop(0)
        rows = ase_viewer.build_scene_actor_rows(player)
        npc = next(row for row in rows if row["kind"] == "npc")
        self.assertEqual(npc["badge_text"], "NPC 01")
        self.assertEqual(player.profiles[2].name, original_name)
        self.assertEqual(player.sources[2].name, original_source)

    def test_corpse_badge_and_languages_keep_internal_data(self):
        player = make_player()
        player.ai_list[1].is_dead = True
        original_profile_names = [profile.name for profile in player.profiles]
        for language in ("ko", "en"):
            player.language = language
            rows = ase_viewer.build_scene_actor_rows(player)
            self.assertEqual(rows[2]["badge_text"], "NPC 02 · CORPSE")
        self.assertEqual(
            [profile.name for profile in player.profiles], original_profile_names,
        )


if __name__ == "__main__":
    unittest.main()
