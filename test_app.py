import tempfile
import unittest
from pathlib import Path
import app


class Tests(unittest.TestCase):
    def test_fences_and_headings(self):
        r = app.inspect("# Intro\n```md\n# Hidden\n[x](missing)\n```\n## Visible\n")
        self.assertEqual([h["text"] for h in r["headings"]], ["Intro", "Visible"])
        self.assertEqual(r["links"], [])

    def test_local_links_and_boundary(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "a.md").write_text(
                "[ok](b.md#part) [bad](gone.md) [escape](../outside.md) [web](https://example.com)"
            )
            (p / "b.md").write_text("# B")
            r = app.index(p)
            self.assertEqual(len(r["documents"]), 2)
            self.assertEqual(
                {x["reason"] for x in r["broken_links"]},
                {"missing target", "outside workspace"},
            )

    def test_search_and_encoded_names(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "a.md").write_text("# Café\n[here](a%20b.md)")
            (p / "a b.md").write_text("hello")
            r = app.index(p, "CAFÉ")
            self.assertEqual(len(r["documents"]), 1)
            self.assertEqual(r["broken_links"], [])

    def test_symlink_documents_are_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "a.md").write_text("# A")
            (p / "copy.md").symlink_to(p / "a.md")
            self.assertEqual(len(app.index(p)["documents"]), 1)


if __name__ == "__main__":
    unittest.main()
