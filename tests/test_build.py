"""Проверки собранного сайта.

Тест запускает настоящую сборку во временную папку и проверяет результат
целиком: так ловятся ошибки, которые не видны при проверке отдельных
модулей — забытый h1, битая ссылка на картинку, пропавшая страница.
"""

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXPECTED_PAGES = 75          # 25 страниц × 3 языка
EXPECTED_ITEMS = 105
EXPECTED_PIZZAS = 13


def build_once():
    """Собирает сайт один раз на весь набор тестов."""
    result = subprocess.run(
        [sys.executable, "build.py"], cwd=ROOT,
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise AssertionError("сборка упала:\n%s\n%s" % (result.stdout, result.stderr))
    return ROOT / "dist", result.stdout


class TestBuiltSite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dist, cls.output = build_once()
        cls.pages = sorted(cls.dist.rglob("index.html"))
        cls.html = {p.relative_to(cls.dist).as_posix(): p.read_text(encoding="utf-8")
                    for p in cls.pages}

    def test_builds_every_page(self):
        self.assertIn("Собрано страниц: %d" % EXPECTED_PAGES, self.output)
        self.assertEqual(len(self.pages), EXPECTED_PAGES)

    def test_every_page_has_exactly_one_h1(self):
        bad = {name: html.count("<h1") for name, html in self.html.items()
               if html.count("<h1") != 1}
        self.assertEqual(bad, {}, "страницы без ровно одного h1: %s" % bad)

    def test_every_page_has_canonical_and_hreflang(self):
        for name, html in self.html.items():
            self.assertIn('rel="canonical"', html, name)
            self.assertIn('hreflang="x-default"', html, name)
            self.assertIn('hreflang="kk"', html, name)

    def test_no_unfilled_placeholders(self):
        for name, html in self.html.items():
            self.assertNotIn("%(", html, "%s: незаполненный плейсхолдер" % name)
            self.assertNotIn(">None<", html, "%s: None в разметке" % name)

    def test_all_local_assets_exist(self):
        refs = set()
        for html in self.html.values():
            refs |= set(re.findall(
                r'(?:src|href)="(/[^"#?]+\.(?:css|js|png|jpg|webp|svg|woff2))"', html))
        missing = [r for r in sorted(refs) if not (self.dist / r.lstrip("/")).exists()]
        self.assertEqual(missing, [], "битые ссылки на файлы: %s" % missing)

    def test_all_internal_links_resolve(self):
        links = set()
        for html in self.html.values():
            links |= set(re.findall(r'href="(/[^"#?]*/)"', html))
        broken = [l for l in sorted(links)
                  if l != "/" and not (self.dist / l.strip("/") / "index.html").exists()]
        self.assertEqual(broken, [], "битые внутренние ссылки: %s" % broken)

    def test_menu_page_contains_every_item(self):
        from build.data import load_menu
        menu = load_menu(ROOT / "data" / "menu.json")
        self.assertEqual(len(menu.items), EXPECTED_ITEMS)
        for lang_dir in ("menu/index.html", "kz/menu/index.html", "en/menu/index.html"):
            html = self.html[lang_dir]
            missing = [i.id for i in menu.items
                       if 'data-item-id="%s"' % i.id not in html]
            self.assertEqual(missing, [], "%s: нет позиций %s" % (lang_dir, missing[:5]))

    def test_dish_pages_exist_for_every_pizza(self):
        from build.data import load_menu
        menu = load_menu(ROOT / "data" / "menu.json")
        photos = menu.with_photos()
        self.assertEqual(len(photos), EXPECTED_PIZZAS)
        for item in photos:
            for prefix in ("menu", "kz/menu", "en/menu"):
                self.assertIn("%s/%s/index.html" % (prefix, item.id), self.html)

    def test_sitemap_lists_every_page(self):
        sitemap = (self.dist / "sitemap.xml").read_text(encoding="utf-8")
        self.assertEqual(sitemap.count("<loc>"), EXPECTED_PAGES)
        self.assertIn("<loc>https://frnds.kz/</loc>", sitemap)
        self.assertIn("<loc>https://frnds.kz/kz/breakfast/</loc>", sitemap)

    def test_robots_points_to_sitemap(self):
        robots = (self.dist / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("Sitemap: https://frnds.kz/sitemap.xml", robots)

    def test_kazakh_pages_use_kazakh_letters(self):
        """Ловим случай, когда казахская версия осталась русским текстом."""
        html = self.html["kz/index.html"]
        self.assertTrue(any(ch in html for ch in "әғқңөұүһі"),
                        "на казахской главной нет казахских букв")

    def test_leaflet_only_where_there_is_a_map(self):
        self.assertIn("leaflet.js", self.html["index.html"])
        self.assertIn("leaflet.js", self.html["contacts/index.html"])
        self.assertNotIn("leaflet.js", self.html["menu/index.html"])

    def test_page_titles_are_unique(self):
        """Два одинаковых title — страницы неразличимы в выдаче.

        Проверяем в целом по сайту, включая языковые версии: даже связанные
        через hreflang страницы должны отличаться, иначе человек в выдаче
        не поймёт, на каком языке он откроет ссылку.
        """
        import re
        titles = {}
        for name, html in self.html.items():
            match = re.search(r"<title>(.*?)</title>", html)
            titles.setdefault(match.group(1), []).append(name)
        dupes = {t: names for t, names in titles.items() if len(names) > 1}
        self.assertEqual(dupes, {}, "повторяющиеся title: %s" % dupes)

    def test_titles_fit_search_results(self):
        """Слишком длинный title обрезается в выдаче многоточием."""
        import re
        too_long = {}
        for name, html in self.html.items():
            title = re.search(r"<title>(.*?)</title>", html).group(1)
            if len(title) > 65:
                too_long[name] = "%d: %s" % (len(title), title)
        self.assertEqual(too_long, {}, "длинные title: %s" % too_long)

    def test_geo_texts_are_not_near_duplicates(self):
        """Пять гео-страниц не должны быть шаблоном с подстановкой района."""
        import json
        from itertools import combinations
        from pathlib import Path

        from build.pages.geo import GEO_SLUGS
        bodies = {}
        for slug in GEO_SLUGS:
            data = json.loads(
                (ROOT / "data" / "pages" / ("geo-%s.ru.json" % slug)).read_text(encoding="utf-8"))
            bodies[slug] = set(data["body"].split())
        for a, b in combinations(GEO_SLUGS, 2):
            overlap = len(bodies[a] & bodies[b]) / len(bodies[a] | bodies[b])
            self.assertLess(overlap, 0.6,
                            "тексты %s и %s совпадают на %.0f%%" % (a, b, overlap * 100))

    def test_rating_is_not_hardcoded_in_page_texts(self):
        """Число отзывов живёт в site.json — в тексте оно быстро станет ложью."""
        import json
        from pathlib import Path
        for path in sorted((ROOT / "data" / "pages").glob("geo-*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertNotIn("182", data["body"],
                             "%s: количество отзывов зашито в текст" % path.name)

    def test_own_delivery_is_present_on_home(self):
        """У заведения своя доставка — главная обязана о ней говорить."""
        self.assertIn("своя доставка", self.html["index.html"].lower())
        self.assertIn("жеткізу", self.html["kz/index.html"].lower())
        self.assertIn("delivery", self.html["en/index.html"].lower())

    def test_privacy_page_and_consent_banner(self):
        """Политика конфиденциальности и уведомление о данных (закон РК 94-V)."""
        for path, marker in (
            ("privacy/index.html", "94-V"),
            ("kz/privacy/index.html", "94-V"),
            ("en/privacy/index.html", "94-V"),
        ):
            self.assertIn(marker, self.html[path], path)
        # Баннер согласия есть на каждой странице и ведёт на политику своего языка
        for name, html in self.html.items():
            self.assertIn('id="consent"', html, "%s: нет баннера согласия" % name)
            self.assertIn('id="consent-ok"', html, name)
        self.assertIn('href="/privacy/"', self.html["index.html"])
        self.assertIn('href="/kz/privacy/"', self.html["kz/index.html"])
        # Ссылка на политику в подвале
        self.assertIn('href="/privacy/"', self.html["menu/index.html"])

    def test_delivery_page_exists_and_links_to_menu(self):
        """Страница «Доставка»: термосумки, WhatsApp и переход в меню."""
        for path, menu_href, marker in (
            ("delivery/index.html", 'href="/menu/"', "термосумк"),
            ("kz/delivery/index.html", 'href="/kz/menu/"', "термосөмке"),
            ("en/delivery/index.html", 'href="/en/menu/"', "thermal bag"),
        ):
            html = self.html[path]
            self.assertIn(menu_href, html, path)
            self.assertIn(marker, html.lower(), path)
            self.assertIn("wa.me/", html, path)
        # Пункт «Доставка» есть в шапке каждой страницы
        self.assertIn('href="/delivery/"', self.html["index.html"])
        self.assertIn('href="/kz/delivery/"', self.html["kz/menu/index.html"])

    def test_no_third_party_delivery_leftovers(self):
        """Старые формулировки времён «доставки нет» не должны вернуться."""
        banned = ["своей доставки нет", "своей доставки у нас нет",
                  "куда они возят", "зону покрытия определя"]
        for name, html in self.html.items():
            low = html.lower()
            for phrase in banned:
                self.assertNotIn(phrase, low, "%s: устаревшее — «%s»" % (name, phrase))


if __name__ == "__main__":
    unittest.main()
