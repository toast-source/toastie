import unittest
from types import SimpleNamespace

import ase_viewer


class SwapDrawOrderTests(unittest.TestCase):
    def test_departing_swap_visual_is_below_player_layer(self):
        npc = SimpleNamespace(name="npc")
        prop = SimpleNamespace(name="prop")
        departure = SimpleNamespace(
            name="old-player", render_below_player=True,
        )
        assist = SimpleNamespace(
            name="assist", render_below_player=False,
        )
        player = SimpleNamespace(
            ai_list=[npc], prop_list=[prop],
            temp_ai_list=[departure, assist],
        )

        below, foreground = ase_viewer.split_actor_render_layers(player)

        self.assertEqual(below, [departure])
        self.assertEqual(foreground, [npc, prop, assist])
        self.assertNotIn(departure, foreground)

    def test_unmarked_transient_keeps_existing_foreground_policy(self):
        transient = SimpleNamespace(name="legacy-temp")
        player = SimpleNamespace(
            ai_list=[], prop_list=[], temp_ai_list=[transient],
        )

        below, foreground = ase_viewer.split_actor_render_layers(player)

        self.assertEqual(below, [])
        self.assertEqual(foreground, [transient])


if __name__ == "__main__":
    unittest.main()
