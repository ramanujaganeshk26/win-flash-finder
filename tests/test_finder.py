import os
import shutil
import tempfile
import unittest
from win_flash_finder.finder import FlashFinder

class TestFlashFinder(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.test_dir, "subdir", "nested"))

        self.pdf_file = os.path.join(self.test_dir, "doc.pdf")
        self.pth_file = os.path.join(self.test_dir, "subdir", "package.pth")
        self.txt_file = os.path.join(self.test_dir, "subdir", "nested", "notes.txt")
        self.hidden_file = os.path.join(self.test_dir, ".hidden.pdf")

        with open(self.pdf_file, "w") as f:
            f.write("pdf data")
        with open(self.pth_file, "w") as f:
            f.write("/path/to/site-packages")
        with open(self.txt_file, "w") as f:
            f.write("some notes")
        with open(self.hidden_file, "w") as f:
            f.write("secret pdf")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_find_pdf_preset(self):
        finder = FlashFinder(skip_hidden=True)
        results = finder.find(self.test_dir, target_preset="pdf")
        paths = [r["path"] for r in results]
        self.assertIn(os.path.abspath(self.pdf_file), paths)
        self.assertNotIn(os.path.abspath(self.hidden_file), paths)
        self.assertEqual(len(results), 1)

    def test_find_pth_preset(self):
        finder = FlashFinder(skip_hidden=True)
        results = finder.find(self.test_dir, target_preset="pth")
        paths = [r["path"] for r in results]
        self.assertIn(os.path.abspath(self.pth_file), paths)
        self.assertEqual(len(results), 1)

    def test_include_hidden(self):
        finder = FlashFinder(skip_hidden=False)
        results = finder.find(self.test_dir, target_preset="pdf")
        self.assertEqual(len(results), 2)

    def test_name_pattern(self):
        finder = FlashFinder(skip_hidden=True)
        results = finder.find(self.test_dir, pattern_str="note")
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]["name"].endswith("notes.txt"))

    def test_max_depth(self):
        finder = FlashFinder(skip_hidden=True)
        results = finder.find(self.test_dir, max_depth=1)
        paths = [r["path"] for r in results]
        self.assertIn(os.path.abspath(self.pdf_file), paths)
        self.assertIn(os.path.abspath(self.pth_file), paths)
        self.assertNotIn(os.path.abspath(self.txt_file), paths)

if __name__ == "__main__":
    unittest.main()
