import re
import unittest
from pathlib import Path

CSS = Path(__file__).resolve().parent.parent / "src" / "css" / "style.css"


def luminance(hex_color):
    value = hex_color.lstrip("#")
    channels = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


class TestPalette(unittest.TestCase):
    def setUp(self):
        self.css = CSS.read_text(encoding="utf-8")

    def token(self, name):
        match = re.search(r"--%s:\s*(#[0-9A-Fa-f]{6})" % name, self.css)
        self.assertIsNotNone(match, "в style.css нет токена --%s" % name)
        return match.group(1)

    def test_body_text_on_cream_is_aaa(self):
        self.assertGreaterEqual(contrast(self.token("ink"), self.token("cream")), 7.0)

    def test_dark_text_on_brand_button_is_aa(self):
        self.assertGreaterEqual(contrast(self.token("ink"), self.token("brand")), 4.5)

    def test_small_brand_text_on_cream_is_aa(self):
        self.assertGreaterEqual(contrast(self.token("brand-text"), self.token("cream")), 4.5)

    def test_small_brand_text_on_white_card_is_aa(self):
        self.assertGreaterEqual(contrast(self.token("brand-text"), self.token("surface")), 4.5)

    def test_large_brand_heading_on_cream_passes_large_threshold(self):
        self.assertGreaterEqual(contrast(self.token("brand-deep"), self.token("cream")), 3.0)

    def test_no_white_text_on_brand_fill(self):
        """Белое по #FF7F17 — 2.53:1. Ловим попытку вернуть это в стили."""
        pattern = re.compile(
            r"\.pill--brand[^{]*\{[^}]*color:\s*(#fff\b|#ffffff|white)", re.I | re.S)
        self.assertIsNone(pattern.search(self.css),
                          "белый текст на брендовой заливке запрещён: контраст 2.53:1")

    def test_kazakh_display_fallback_rule_exists(self):
        """У Playfair нет казахских букв — display на kk обязан быть Manrope."""
        self.assertRegex(self.css, r'data-lang="kk"[^{]*\.display[^{]*\{[^}]*Manrope')


if __name__ == "__main__":
    unittest.main()
