import unittest
from types import SimpleNamespace

import ase_viewer


def actor(**overrides):
    values = {
        "x": 10, "y": 20, "hp": 10, "visible": True,
        "is_prop": False, "is_partner": False, "is_temp": False,
        "is_corpse": False, "is_dead": False, "actions": [],
    }
    values.update(overrides)
    result = SimpleNamespace(**values)
    result.trigger_action = result.actions.append
    return result


class RecallExcludesCorpsesTests(unittest.TestCase):
    def test_recall_moves_only_living_npcs(self):
        living = actor()
        corpse = actor(x=300, y=500, hp=0, is_dead=True, is_corpse=True)
        dead_npc = actor(x=400, y=450, hp=0, is_dead=True)
        decision_dead = actor(x=500, y=425, decision="DEAD")
        player = SimpleNamespace(
            x=100, y=200,
            ai_list=[living, corpse, dead_npc, decision_dead],
            scene_status_message="", target_ai_count=4,
        )

        count = ase_viewer.recall_live_npcs(
            player, direction_picker=lambda choices: choices[1],
        )

        self.assertEqual(count, 1)
        self.assertEqual((living.x, living.y), (180, 200))
        self.assertEqual(living.actions, ["Swap_Enter"])
        self.assertEqual((corpse.x, corpse.y), (300, 500))
        self.assertEqual((dead_npc.x, dead_npc.y), (400, 450))
        self.assertEqual((decision_dead.x, decision_dead.y), (500, 425))
        self.assertTrue(corpse.is_dead)
        self.assertTrue(corpse.is_corpse)
        self.assertEqual(player.target_ai_count, 4)
        self.assertIn("1", player.scene_status_message)

    def test_no_living_npcs_is_safe_no_op_with_status(self):
        corpse = actor(x=300, y=500, hp=0, is_dead=True, is_corpse=True)
        player = SimpleNamespace(
            x=100, y=200, ai_list=[corpse], scene_status_message="",
        )

        count = ase_viewer.recall_live_npcs(player)

        self.assertEqual(count, 0)
        self.assertEqual((corpse.x, corpse.y), (300, 500))
        self.assertEqual(
            player.scene_status_message,
            ase_viewer.tr("status.recall_no_live_npcs"),
        )

    def test_missing_player_is_safe_no_op(self):
        self.assertEqual(ase_viewer.recall_live_npcs(None), 0)

    def test_partner_and_prop_are_not_recall_targets(self):
        partner = actor(x=250, y=350, is_partner=True)
        prop = actor(x=450, y=500, is_prop=True)
        player = SimpleNamespace(
            x=100, y=200, ai_list=[partner, prop],
            scene_status_message="",
        )

        self.assertEqual(ase_viewer.recall_live_npcs(player), 0)
        self.assertEqual((partner.x, partner.y), (250, 350))
        self.assertEqual((prop.x, prop.y), (450, 500))


if __name__ == "__main__":
    unittest.main()
