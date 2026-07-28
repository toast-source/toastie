import unittest
from types import SimpleNamespace

import ase_viewer


class PartnerNotSceneActorTests(unittest.TestCase):
    def test_partner_profile_is_never_returned_by_scene_filters(self):
        player_profile = SimpleNamespace(
            name="PLAYER", source_idx=0, kind="player",
        )
        partner_profile = SimpleNamespace(
            name="PARTNER", source_idx=1, kind="partner",
        )
        player = SimpleNamespace(
            profiles=[player_profile, partner_profile],
            sources=[
                SimpleNamespace(name="Hero.aseprite"),
                SimpleNamespace(name="Partner.aseprite"),
            ],
            partner_profiles=[partner_profile], partner_list=[],
            ai_list=[], prop_list=[], visible=True,
        )
        rows = ase_viewer.build_scene_actor_rows(player)
        self.assertEqual([row["kind"] for row in rows], ["player"])
        for filter_name in ase_viewer.SCENE_OBJECT_FILTERS:
            self.assertFalse(any(
                row["profile"] is partner_profile
                for row in ase_viewer.filter_scene_actor_rows(rows, filter_name)
            ))


if __name__ == "__main__":
    unittest.main()
