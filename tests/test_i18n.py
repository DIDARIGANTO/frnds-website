import unittest

from build.i18n import LANGS, alternate_urls, output_path, t, url


class TestUrl(unittest.TestCase):
    def test_russian_is_at_root(self):
        self.assertEqual(url("ru", ""), "/")
        self.assertEqual(url("ru", "menu"), "/menu/")

    def test_other_languages_get_prefix(self):
        self.assertEqual(url("kk", ""), "/kz/")
        self.assertEqual(url("kk", "menu"), "/kz/menu/")
        self.assertEqual(url("en", "contacts"), "/en/contacts/")

    def test_nested_path(self):
        self.assertEqual(url("ru", "menu/pizza-pepperoni"), "/menu/pizza-pepperoni/")
        self.assertEqual(url("en", "menu/pizza-pepperoni"), "/en/menu/pizza-pepperoni/")


class TestOutputPath(unittest.TestCase):
    def test_maps_url_to_file(self):
        self.assertEqual(output_path("ru", ""), "index.html")
        self.assertEqual(output_path("ru", "menu"), "menu/index.html")
        self.assertEqual(output_path("kk", "menu"), "kz/menu/index.html")
        self.assertEqual(output_path("en", "menu/pizza-cheese"), "en/menu/pizza-cheese/index.html")


class TestAlternates(unittest.TestCase):
    def test_lists_every_language_plus_default(self):
        alts = alternate_urls("https://frnds.kz", "menu")
        self.assertEqual(alts["ru"], "https://frnds.kz/menu/")
        self.assertEqual(alts["kk"], "https://frnds.kz/kz/menu/")
        self.assertEqual(alts["en"], "https://frnds.kz/en/menu/")
        self.assertEqual(alts["x-default"], "https://frnds.kz/menu/")


class TestStrings(unittest.TestCase):
    def test_every_ui_string_exists_in_every_language(self):
        from build.i18n import UI
        for key, translations in UI.items():
            for lang in LANGS:
                self.assertIn(lang, translations, "нет %s для строки %r" % (lang, key))
                self.assertTrue(translations[lang].strip(), "пустая строка %r/%s" % (key, lang))

    def test_lookup(self):
        self.assertEqual(t("nav.menu", "ru"), "Меню")
        self.assertEqual(t("nav.menu", "kk"), "Мәзір")
        self.assertEqual(t("nav.menu", "en"), "Menu")

    def test_unknown_key_raises(self):
        with self.assertRaises(KeyError):
            t("no.such.key", "ru")


if __name__ == "__main__":
    unittest.main()
