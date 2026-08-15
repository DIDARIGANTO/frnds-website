"""Загрузка и валидация JSON-данных сайта.

Модуль ничего не знает про HTML: он только читает файлы, проверяет их
и отдаёт объекты. Любая опечатка в данных должна падать здесь, с внятным
сообщением, а не превращаться в кривую страницу.
"""

import json
from pathlib import Path

LANGS = ("ru", "kk", "en")


class DataError(Exception):
    """Данные не прошли проверку."""


class Category:
    __slots__ = ("id", "group", "order", "icon", "name")

    def __init__(self, raw):
        self.id = raw["id"]
        self.group = raw["group"]
        self.order = raw["order"]
        self.icon = raw.get("icon", "")
        self.name = raw["name"]


class Item:
    __slots__ = ("id", "category", "price", "photo", "badges", "tags", "name", "desc")

    def __init__(self, raw):
        self.id = raw["id"]
        self.category = raw["category"]
        self.price = raw["price"]
        self.photo = raw.get("photo") or ""
        self.badges = tuple(raw.get("badges", ()))
        self.tags = tuple(raw.get("tags", ()))
        self.name = raw["name"]
        self.desc = raw["desc"]


class Menu:
    def __init__(self, categories, items):
        self.categories = categories
        self.items = items

    def by_category(self, category_id):
        return [i for i in self.items if i.category == category_id]

    def get(self, item_id):
        for item in self.items:
            if item.id == item_id:
                return item
        raise DataError("нет блюда с id %r" % item_id)

    def with_photos(self):
        return [i for i in self.items if i.photo]


class Site:
    __slots__ = ("domain", "phone", "whatsapp", "instagram", "twogis", "hours",
                 "coords", "address", "rating", "aggregators")

    def __init__(self, raw):
        self.domain = raw["domain"].rstrip("/")
        self.phone = raw["phone"]
        self.whatsapp = raw["whatsapp"]
        self.instagram = raw.get("instagram", "")
        self.twogis = raw.get("twogis", "")
        self.hours = raw["hours"]
        self.coords = raw["coords"]
        self.address = raw["address"]
        self.rating = raw["rating"]
        self.aggregators = raw.get("aggregators", [])


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise DataError("не найден файл данных: %s" % path)
    except json.JSONDecodeError as err:
        raise DataError("сломан JSON в %s: %s" % (path, err))


def _check_translations(where, field, value):
    if not isinstance(value, dict):
        raise DataError("%s: поле %r должно быть объектом с переводами" % (where, field))
    for lang in LANGS:
        text = value.get(lang)
        if not text or not str(text).strip():
            raise DataError("%s: нет перевода %r для поля %r" % (where, lang, field))


def load_menu(path):
    raw = _read_json(path)
    categories = [Category(c) for c in raw.get("categories", [])]
    known = {c.id for c in categories}
    if len(known) != len(categories):
        raise DataError("в categories есть повторяющиеся id")

    for cat in categories:
        _check_translations("категория %s" % cat.id, "name", cat.name)

    items = []
    seen = set()
    for raw_item in raw.get("items", []):
        try:
            item = Item(raw_item)
        except KeyError as err:
            raise DataError("в позиции меню нет обязательного поля %s: %r" % (err, raw_item))
        where = "блюдо %s" % item.id
        if item.id in seen:
            raise DataError("%s: такой id уже был" % where)
        seen.add(item.id)
        if item.category not in known:
            raise DataError("%s: ссылается на несуществующую категорию %r" % (where, item.category))
        if not isinstance(item.price, int) or item.price <= 0:
            raise DataError("%s: цена должна быть целым числом больше нуля" % where)
        _check_translations(where, "name", item.name)
        _check_translations(where, "desc", item.desc)
        items.append(item)

    categories.sort(key=lambda c: c.order)
    return Menu(categories, items)


def load_site(path):
    raw = _read_json(path)
    try:
        return Site(raw)
    except KeyError as err:
        raise DataError("в site.json нет обязательного поля %s" % err)


def load_page(directory, page, lang):
    """Тексты одной страницы одного языка: data/pages/<page>.<lang>.json"""
    return _read_json(Path(directory) / ("%s.%s.json" % (page, lang)))
