import unittest
from types import SimpleNamespace
from unittest import mock

import ase_viewer


def profile(name="NPC", intro=True, kind="npc"):
    return SimpleNamespace(
        name=name, source_idx=0, kind=kind,
        is_prop_profile=kind == "prop",
        mappings={"INTRO": [[0, "Intro"]]} if intro else {"INTRO": []},
    )


def npc_for(npc_profile, **overrides):
    values = {
        "profile": npc_profile,
        "x": 120.0, "y": 500.0, "visible": True,
        "is_dead": False, "is_corpse": False,
        "npc_attack_locked": False,
        "trigger_action": mock.Mock(return_value=True),
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def player_with(profiles, npcs=None, props=None):
    return SimpleNamespace(
        profiles=profiles, sources=[], ai_list=npcs or [],
        prop_list=props or [], partner_profiles=[],
        selected_scene_actor_key=None, cur_profile_idx=0,
        npc_intro_replay_status="", target_ai_count=len(npcs or []),
    )


class NpcIntroReplayTests(unittest.TestCase):
    def test_selected_npc_replays_without_moving_or_spawning(self):
        npc_profile = profile()
        npc = npc_for(npc_profile)
        player = player_with([npc_profile], [npc])
        player.selected_scene_actor_key = ("npc", id(npc))
        before = (npc.x, npc.y, len(player.ai_list), player.target_ai_count)
        result = ase_viewer.replay_npc_intro(player)
        self.assertEqual(result["status_key"], "status.npc_intro_selected")
        npc.trigger_action.assert_called_once_with("INTRO")
        self.assertEqual(
            (npc.x, npc.y, len(player.ai_list), player.target_ai_count), before,
        )

    def test_no_selection_replays_current_profile_live_npcs_only(self):
        npc_profile = profile()
        first = npc_for(npc_profile)
        second = npc_for(npc_profile)
        other_profile = profile("Other")
        other = npc_for(other_profile)
        player = player_with([npc_profile, other_profile], [first, second, other])
        result = ase_viewer.replay_npc_intro(player)
        self.assertEqual(result["count"], 2)
        first.trigger_action.assert_called_once_with("INTRO")
        second.trigger_action.assert_called_once_with("INTRO")
        other.trigger_action.assert_not_called()

    def test_missing_intro_and_no_npc_are_safe(self):
        missing = profile(intro=False)
        player = player_with([missing])
        self.assertEqual(
            ase_viewer.replay_npc_intro(player)["status_key"],
            "status.npc_intro_missing",
        )
        player.profiles = []
        self.assertEqual(
            ase_viewer.replay_npc_intro(player)["status_key"],
            "status.npc_intro_no_target",
        )

    def test_attack_locked_selected_npc_is_not_interrupted(self):
        npc_profile = profile()
        npc = npc_for(npc_profile, npc_attack_locked=True)
        player = player_with([npc_profile], [npc])
        player.selected_scene_actor_key = ("npc", id(npc))
        result = ase_viewer.replay_npc_intro(player)
        self.assertEqual(
            result["status_key"], "status.npc_intro_attack_locked",
        )
        npc.trigger_action.assert_not_called()

    def test_prop_and_partner_are_not_affected(self):
        npc_profile = profile()
        prop_profile = profile("Prop", kind="prop")
        prop = npc_for(prop_profile)
        partner = profile("Partner", kind="partner")
        player = player_with([npc_profile, prop_profile, partner], props=[prop])
        player.partner_profiles = [partner]
        ase_viewer.replay_npc_intro(player)
        prop.trigger_action.assert_not_called()
        self.assertEqual(player.partner_profiles, [partner])

    def test_bilingual_button_status_and_tooltip_strings_exist(self):
        keys = (
            "ui.replay_npc_intro", "tooltip.replay_npc_intro",
            "status.npc_intro_selected", "status.npc_intro_profile",
            "status.npc_intro_no_target", "status.npc_intro_missing",
            "status.npc_intro_attack_locked",
        )
        for language in ("ko", "en"):
            for key in keys:
                self.assertNotEqual(ase_viewer.tr(key, language=language), key)


if __name__ == "__main__":
    unittest.main()
