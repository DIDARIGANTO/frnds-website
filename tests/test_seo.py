import json
import unittest
import xml.etree.ElementTree as ET

from build.seo import breadcrumbs_jsonld, menu_jsonld, menuitem_jsonld, restaurant_jsonld, robots_txt, sitemap_xml
from tests.test_pages import make_item, make_site


class TestSitemap(unittest.TestCase):
    def test_is_valid_xml_with_all_urls(self):
        xml = sitemap_xml("https://frnds.kz", ["", "menu", "menu/pizza-cheese"])
        root = ET.fromstring(xml)
        locs = [e.text for e in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        self.assertIn("https://frnds.kz/", locs)
        self.assertIn("https://frnds.kz/kz/menu/", locs)
        self.assertIn("https://frnds.kz/en/menu/pizza-cheese/", locs)
        self.assertEqual(len(locs), 9)  # 3 пути × 3 языка


class TestRobots(unittest.TestCase):
    def test_points_to_sitemap(self):
        text = robots_txt("https://frnds.kz")
        self.assertIn("Sitemap: https://frnds.kz/sitemap.xml", text)
        self.assertIn("User-agent: *", text)


class TestJsonLd(unittest.TestCase):
    def test_restaurant_has_required_fields(self):
        data = json.loads(restaurant_jsonld(make_site(), "ru"))
        self.assertEqual(data["@type"], "Restaurant")
        self.assertEqual(data["aggregateRating"]["ratingValue"], 4.9)
        self.assertEqual(data["aggregateRating"]["reviewCount"], 182)
        self.assertIn("geo", data)
        self.assertIn("openingHoursSpecification", data)
        self.assertEqual(data["telephone"], "+77074809215")

    def test_menuitem_carries_price_in_kzt(self):
        data = json.loads(menuitem_jsonld(make_site(), make_item(), "ru"))
        self.assertEqual(data["@type"], "MenuItem")
        self.assertEqual(data["offers"]["priceCurrency"], "KZT")
        self.assertEqual(data["offers"]["price"], 3590)

    def test_breadcrumbs_are_ordered(self):
        data = json.loads(breadcrumbs_jsonld([
            ("Главная", "https://frnds.kz/"),
            ("Меню", "https://frnds.kz/menu/"),
        ]))
        self.assertEqual(data["itemListElement"][0]["position"], 1)
        self.assertEqual(data["itemListElement"][1]["name"], "Меню")

    def test_menu_jsonld_lists_sections(self):
        from build.data import Category, Menu
        menu = Menu(
            [Category({"id": "pizza", "group": "pizza", "order": 1,
                       "name": {"ru": "Пицца", "kk": "Пицца", "en": "Pizza"}})],
            [make_item()],
        )
        data = json.loads(menu_jsonld(make_site(), menu, "ru"))
        self.assertEqual(data["@type"], "Menu")
        self.assertEqual(data["hasMenuSection"][0]["name"], "Пицца")
        self.assertEqual(
            data["hasMenuSection"][0]["hasMenuItem"][0]["offers"]["price"], 3590)


if __name__ == "__main__":
    unittest.main()
