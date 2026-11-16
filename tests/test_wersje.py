import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import wersje


class TestWersje(unittest.TestCase):
    def test_wersje_css_i_js_sa_aktualne(self):
        self.assertEqual(wersje.nieaktualne(), [], "Uruchom: python3 scripts/wersje.py")


if __name__ == "__main__":
    unittest.main()
