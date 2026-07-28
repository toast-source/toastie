import os
import sys
import unittest
from pathlib import Path


os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import ase_viewer


class GuiSmokeTests(unittest.TestCase):
    def test_full_headless_gui_check(self):
        self.assertEqual(ase_viewer.check_gui(), 0)


if __name__ == "__main__":
    unittest.main()
