import sys
from pathlib import Path

# Thêm project root vào sys.path để tìm thấy package 'src'
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest

from src.html_cleaner import clean_html
from src.utils import slugify, count_tokens
from src.markdown_converter import strip_boilerplate_sections

class TestTextProcessing(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(slugify("How to Install OptiSigns"), "how-to-install-optisigns")
        self.assertEqual(slugify("Chào Thế Giới 123!"), "chao-the-gioi-123")
        
    def test_clean_html_strips_script(self):
        raw = "<p>Hello</p><script>alert('xss')</script>"
        self.assertNotIn("script", clean_html(raw))
        
    def test_strip_boilerplate_sections(self):
        raw_md = "## Intro\nSome text\n\n## Need Help?\nContact support@optisigns.com"
        cleaned = strip_boilerplate_sections(raw_md)
        self.assertNotIn("Need Help", cleaned)

if __name__ == "__main__":
    unittest.main()
