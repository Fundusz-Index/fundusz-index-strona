import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import zbuduj_sitemap as S  # noqa: E402


class TestSitemap(unittest.TestCase):
    def test_aktualna(self):
        self.assertEqual((ROOT / "sitemap.xml").read_text(encoding="utf-8"), S.tresc(),
                         "sitemap.xml jest nieaktualny: uruchom python3 scripts/zbuduj_sitemap.py")

    def test_bez_404(self):
        self.assertNotIn("404.html", S.tresc())

    def test_robots_wskazuje_sitemap(self):
        self.assertIn("Sitemap: https://fundusz.knrkindex.pl/sitemap.xml", (ROOT / "robots.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
