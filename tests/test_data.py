import json
import tempfile
import unittest
from pathlib import Path

from build.data import DataError, load_menu, load_site


class TestLoadMenu(unittest.TestCase):
    def _write(self, payload):
        tmp = Path(tempfile.mkdtemp()) / "menu.json"
        tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return tmp

    def test_loads_categories_and_items(self):
        path = self._write({
            "categories": [
                {"id": "pizza", "group": "pizza", "order": 1,
                 "name": {"ru": "Пицца", "kk": "Пицца", "en": "Pizza"}}
            ],
            "items": [
                {"id": "pepperoni", "category": "pizza", "price": 3590,
                 "name": {"ru": "Пепперони", "kk": "Пепперони", "en": "Pepperoni"},
                 "desc": {"ru": "Острая", "kk": "Ащы", "en": "Spicy"}}
            ],
        })
        menu = load_menu(path)
        self.assertEqual(len(menu.categories), 1)
        self.assertEqual(menu.items[0].price, 3590)
        self.assertEqual(menu.items[0].name["kk"], "Пепперони")

    def test_rejects_item_with_unknown_category(self):
        path = self._write({
            "categories": [],
            "items": [
                {"id": "x", "category": "ghost", "price": 1,
                 "name": {"ru": "a", "kk": "a", "en": "a"},
                 "desc": {"ru": "b", "kk": "b", "en": "b"}}
            ],
        })
        with self.assertRaises(DataError) as ctx:
            load_menu(path)
        self.assertIn("ghost", str(ctx.exception))

    def test_rejects_missing_translation(self):
        path = self._write({
            "categories": [
                {"id": "pizza", "group": "pizza", "order": 1,
                 "name": {"ru": "Пицца", "kk": "Пицца", "en": "Pizza"}}
            ],
            "items": [
                {"id": "x", "category": "pizza", "price": 1,
                 "name": {"ru": "Только русский"},
                 "desc": {"ru": "b", "kk": "b", "en": "b"}}
            ],
        })
        with self.assertRaises(DataError) as ctx:
            load_menu(path)
        self.assertIn("kk", str(ctx.exception))

    def test_rejects_duplicate_item_id(self):
        item = {"id": "same", "category": "pizza", "price": 1,
                "name": {"ru": "a", "kk": "a", "en": "a"},
                "desc": {"ru": "b", "kk": "b", "en": "b"}}
        path = self._write({
            "categories": [
                {"id": "pizza", "group": "pizza", "order": 1,
                 "name": {"ru": "Пицца", "kk": "Пицца", "en": "Pizza"}}
            ],
            "items": [item, dict(item)],
        })
        with self.assertRaises(DataError):
            load_menu(path)

    def test_rejects_non_positive_price(self):
        path = self._write({
            "categories": [
                {"id": "pizza", "group": "pizza", "order": 1,
                 "name": {"ru": "Пицца", "kk": "Пицца", "en": "Pizza"}}
            ],
            "items": [
                {"id": "x", "category": "pizza", "price": 0,
                 "name": {"ru": "a", "kk": "a", "en": "a"},
                 "desc": {"ru": "b", "kk": "b", "en": "b"}}
            ],
        })
        with self.assertRaises(DataError) as ctx:
            load_menu(path)
        self.assertIn("цена", str(ctx.exception))


class TestLoadSite(unittest.TestCase):
    def test_reads_contacts(self):
        tmp = Path(tempfile.mkdtemp()) / "site.json"
        tmp.write_text(json.dumps({
            "domain": "https://frnds.kz",
            "phone": "+77074809215",
            "whatsapp": "77074809215",
            "instagram": "https://www.instagram.com/frnds.kz",
            "hours": {"open": "09:00", "close": "23:00"},
            "coords": {"lat": 51.119566, "lon": 71.484317},
            "address": {"ru": "Сағадат Нұрмағамбетов, 25",
                        "kk": "Сағадат Нұрмағамбетов, 25",
                        "en": "Sagadat Nurmagambetov St 25"},
            "rating": {"value": 4.9, "count": 182},
            "aggregators": [],
        }, ensure_ascii=False), encoding="utf-8")
        site = load_site(tmp)
        self.assertEqual(site.whatsapp, "77074809215")
        self.assertEqual(site.rating["count"], 182)


if __name__ == "__main__":
    unittest.main()
