# Сайт Frnds — план реализации

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Статический многоязычный сайт пиццерии Frnds в Астане — 69 страниц на RU/KZ/EN, меню на 104 позиции, корзина с выгрузкой заказа в WhatsApp, гео-страницы под районы города.

**Architecture:** Генератор на чистом Python 3.9 (только stdlib) собирает статические HTML из JSON-данных. HTML строится функциями-компонентами, а не текстовыми шаблонами: нет самодельного парсера, всё покрывается обычными unit-тестами, экранирование через `html.escape`. Фронтенд — один CSS и два маленьких JS без фреймворков. Результат в `dist/` заливается на любой хостинг.

**Tech Stack:** Python 3.9 stdlib, Pillow (только для разовой нарезки фото), ванильный CSS и JS, Leaflet локально, шрифты Manrope и Playfair Display в woff2.

**Спецификация:** `docs/superpowers/specs/2026-08-14-frnds-website-design.md`

**Исходники (уже извлечены, лежат вне репозитория):**
- Логотипы с прозрачностью 4231×1975: `<scratch>/frnds-logo-{white,orange,dark}.png`
- 13 фото пицц 3000×3000: `<scratch>/menu/pizza_imgs/x{18..23,34..40}.png`
- Отрендеренные макеты меню: `<scratch>/menu/{bar,kitchen,pizza}_p{1,2}_full.png`

где `<scratch>` = `/private/tmp/claude-501/-Users-didar-Desktop------------hostel-22/b946e5ac-a4ba-42b5-8c9c-ed6d970cecea/scratchpad`

---

## Структура файлов

```
build.py                  оркестратор сборки
build/
  __init__.py
  data.py                 загрузка и валидация JSON
  i18n.py                 языки, UI-строки, построение URL
  layout.py               каркас страницы: head, meta, hreflang, JSON-LD
  components.py           header, footer, карточка блюда, пилюля-цена, бейджи
  seo.py                  sitemap.xml, robots.txt, JSON-LD Restaurant
  assets.py               копирование статики в dist/
  pages/
    __init__.py
    home.py  menu.py  dish.py  breakfast.py  about.py  contacts.py  geo.py
tools/
  prepare_images.py       разовая нарезка фото (Pillow)
data/
  site.json               контакты, часы, домен, соцсети
  menu.json               20 разделов, 104 позиции, 3 языка
  pages/                  тексты страниц: <page>.<lang>.json
src/
  css/style.css
  js/cart.js  js/nav.js
  fonts/*.woff2
  img/                    логотипы, нарезанные фото, иконки
  vendor/leaflet/
tests/
  test_data.py  test_i18n.py  test_seo.py  test_pages.py  test_contrast.py
dist/                     результат сборки (в .gitignore)
```

Границы: `data.py` не знает про HTML. `components.py` не читает файлы. Страницы получают данные аргументами и возвращают строку. `assets.py` не зависит от контента.

---

## Task 1: Скелет проекта

**Files:**
- Create: `build/__init__.py`, `build/pages/__init__.py`, `tests/__init__.py`
- Create: `README.md`
- Create: `run_tests.sh`

- [ ] **Step 1: Создать дерево каталогов**

```bash
cd "/Users/didar/Desktop/тут сайты /Frnds"
mkdir -p build/pages tools data/pages src/css src/js src/fonts src/img src/vendor tests
touch build/__init__.py build/pages/__init__.py tests/__init__.py
```

- [ ] **Step 2: Написать README.md**

```markdown
# Сайт Frnds

Статический сайт пиццерии Frnds (Астана) на трёх языках.

## Как пересобрать сайт

    python3 build.py

Готовый сайт появится в папке `dist/` — её содержимое и заливается на хостинг.

## Как посмотреть локально

    python3 -m http.server -d dist 8000

Открыть http://localhost:8000

## Как поменять цену или блюдо

Всё меню лежит в `data/menu.json`. Найдите блюдо по названию, поправьте
поле `price` (число, без пробелов и знака тенге) и пересоберите сайт.
Цена обновится сразу на всех страницах и во всех трёх языках.

## Как поменять телефон, часы, адрес

`data/site.json`.

## Как поменять тексты страниц

`data/pages/` — по файлу на страницу и язык, например `home.ru.json`.

## Тесты

    ./run_tests.sh
```

- [ ] **Step 3: Написать run_tests.sh**

```bash
#!/bin/sh
set -e
python3 -m unittest discover -s tests -v
```

- [ ] **Step 4: Проверить запуск**

Run: `chmod +x run_tests.sh && ./run_tests.sh`
Expected: `Ran 0 tests` — каталог тестов пуст, ошибок нет.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "chore: скелет проекта и инструкция по сборке"
```

---

## Task 2: Загрузка и валидация данных

**Files:**
- Create: `build/data.py`
- Test: `tests/test_data.py`

- [ ] **Step 1: Написать падающий тест**

```python
# tests/test_data.py
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
```

- [ ] **Step 2: Запустить тест и убедиться, что падает**

Run: `python3 -m unittest tests.test_data -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'build.data'`

- [ ] **Step 3: Реализовать build/data.py**

```python
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
```

- [ ] **Step 4: Запустить тест**

Run: `python3 -m unittest tests.test_data -v`
Expected: PASS, 5 тестов.

- [ ] **Step 5: Commit**

```bash
git add build/data.py tests/test_data.py && git commit -m "feat: загрузка и валидация данных меню и сайта"
```

---

## Task 3: Настройки сайта

**Files:**
- Create: `data/site.json`

- [ ] **Step 1: Записать данные заведения**

Факты подтверждены: 2GIS (адрес, часы, телефон, рейтинг 4.9 из 182 отзывов), Instagram `@frnds.kz`, координаты `51.119566, 71.484317`.

```json
{
  "domain": "https://frnds.kz",
  "phone": "+77074809215",
  "whatsapp": "77074809215",
  "instagram": "https://www.instagram.com/frnds.kz",
  "twogis": "https://2gis.kz/astana/firm/70000001113515854",
  "hours": { "open": "09:00", "close": "23:00" },
  "coords": { "lat": 51.119566, "lon": 71.484317 },
  "address": {
    "ru": "Астана, улица Сағадат Нұрмағамбетов, 25",
    "kk": "Астана, Сағадат Нұрмағамбетов көшесі, 25",
    "en": "Astana, Sagadat Nurmagambetov Street 25"
  },
  "rating": { "value": 4.9, "count": 182 },
  "aggregators": []
}
```

`domain` — рабочее значение, домена у владельца пока нет. Меняется одной строкой, после чего пересборка чинит hreflang, canonical, sitemap и Schema.org разом.
`aggregators` пуст: ссылки на Glovo/Wolt/Yandex владелец ещё не прислал, блок «Как забрать» скрывает пустой список.

- [ ] **Step 2: Проверить, что файл читается**

Run: `python3 -c "from build.data import load_site; s = load_site('data/site.json'); print(s.domain, s.rating)"`
Expected: `https://frnds.kz {'value': 4.9, 'count': 182}`

- [ ] **Step 3: Commit**

```bash
git add data/site.json && git commit -m "feat: контакты и настройки заведения"
```

---

## Task 4: Меню — 104 позиции на трёх языках

**Files:**
- Create: `data/menu.json`

Это самая объёмная задача по содержанию и самая простая по коду. Источник — макеты с Яндекс.Диска, отрендеренные в PNG (пути в шапке плана). Казахский текст переносится как есть, русский и английский — перевод.

- [ ] **Step 1: Завести 21 категорию**

Порядок задаёт вид страницы меню: сначала то, чем заведение известно.

| order | id | group | ru | kk | en |
|---|---|---|---|---|---|
| 1 | `pizza` | pizza | Пицца | Пицца | Pizza |
| 2 | `breakfast` | kitchen | Завтраки | Таңғы астар | Breakfast |
| 3 | `panuozzo` | kitchen | Пануоццо | Пануоццо | Panuozzo |
| 4 | `pasta` | kitchen | Свежая паста | Фреш пасталар | Fresh pasta |
| 5 | `salads` | kitchen | Салаты | Салаттар | Salads |
| 6 | `soups` | kitchen | Супы | Сорпалар | Soups |
| 7 | `hot` | kitchen | Горячее | Ыстық тағамдар | Main courses |
| 8 | `sides` | kitchen | Гарниры | Гарнирлер | Sides |
| 9 | `bread` | kitchen | Хлеб | Нан | Bread |
| 10 | `desserts` | kitchen | Десерты | Тіскебасарлар | Desserts |
| 11 | `coffee` | bar | Классический кофе | Классикалық кофе | Classic coffee |
| 12 | `specialty` | bar | Спешелти напитки | Арнайы сусындар | Specialty drinks |
| 13 | `tea` | bar | Классический чай | Классикалық шай | Classic tea |
| 14 | `signature-tea` | bar | Авторские чаи | Авторлық шайлар | Signature teas |
| 15 | `ice-tea` | bar | Айс-ти | Айс-ти | Iced tea |
| 16 | `lemonades` | bar | Лимонады | Лимонадтар | Lemonades |
| 17 | `smoothies` | bar | Смузи | Смузилер | Smoothies |
| 18 | `milkshakes` | bar | Милкшейки | Милкшейктер | Milkshakes |
| 19 | `soft-drinks` | bar | Напитки | Сусындар | Soft drinks |
| 20 | `milk` | bar | Альтернативное молоко | Баламалы сүт | Alternative milk |
| 21 | `coffee-addons` | bar | Добавки к кофе | Кофеге қосымша | Coffee add-ons |

Раздел `tea` в макете бара ошибочно озаглавлен «КЛАССИКАЛЫҚ КОФЕ» — на сайте исправляем на «Классикалық шай». Опечатку не переносим.

- [ ] **Step 2: Перенести 13 пицц с фото**

Порядок фото в контактном листе совпадает с раскладкой макета. Соответствие проверено визуально:

| id | photo | цена | ru | kk |
|---|---|---|---|---|
| `pizza-meat-kazy` | `pizza-meat-kazy` | 4690 | Пицца с мясом и казы | Ет пен қазы қосылған пицца |
| `pizza-margherita` | `pizza-margherita` | 3190 | Маргарита | Маргарита |
| `pizza-pepperoni` | `pizza-pepperoni` | 3590 | Пепперони | Пепперони |
| `pizza-salmon-broccoli` | `pizza-salmon-broccoli` | 4190 | Лосось и брокколи | Ақсерке мен брокколи |
| `pizza-bolognese` | `pizza-bolognese` | 3890 | Болоньезе | Болоньезе |
| `pizza-stracciatella-lecho` | `pizza-stracciatella-lecho` | 3990 | Лечо со страчателлой | Страчателла қосылған лечо |
| `pizza-chicken-tomato` | `pizza-chicken-tomato` | 3790 | Курица и томаты | Тауық еті мен қызанақ |
| `pizza-meatballs` | `pizza-meatballs` | 3990 | Пицца с фрикадельками | Ет түйірлері қосылған пицца |
| `pizza-shrimp` | `pizza-shrimp` | 4190 | Пицца с креветками | Асшаян қосылған пицца |
| `pizza-strawberry-gorgonzola` | `pizza-strawberry-gorgonzola` | 3990 | Клубника и горгонзола | Құлпынай мен горгонзола |
| `pizza-cheese` | `pizza-cheese` | 3690 | Сырная | Ірімшікті |
| `pizza-truffle-mushroom` | `pizza-truffle-mushroom` | 3790 | Грибы с трюфелем | Трюфель қосылған саңырауқұлақты |
| `pizza-carbonara` | `pizza-carbonara` | 3990 | Карбонара | Карбонара |

Описания берутся с макета `pizza_p1_full.png` и `pizza_p2_full.png`. Пример готовой позиции:

```json
{
  "id": "pizza-pepperoni",
  "category": "pizza",
  "price": 3590,
  "photo": "pizza-pepperoni",
  "badges": ["hit"],
  "tags": ["spicy"],
  "name": { "ru": "Пепперони", "kk": "Пепперони", "en": "Pepperoni" },
  "desc": {
    "ru": "Острая пепперони, моцарелла и сливочный соус с ароматом свежего базилика.",
    "kk": "Ащы пепперони, моцарелла және балғын базиликтің хош иісі бар кілегейлі тұздық.",
    "en": "Spicy pepperoni, mozzarella and a cream sauce scented with fresh basil."
  }
}
```

Метки `hit` ставим на Пепперони, Маргариту и Карбонару — классика, которую заказывают чаще всего. `spicy` — Пепперони и Арабьята. Владелец поправит, если статистика другая.

- [ ] **Step 3: Перенести 48 позиций кухни**

Источник: `kitchen_p1_full.png` (завтраки 13, салаты 5, супы 4, горячее 3) и `kitchen_p2_full.png` (пануоццо 6, паста 5, десерты 4, хлеб 2, гарниры 6). Поле `photo` пустое.

Гарниры и хлеб в макете идут без описаний — у них `desc` заполняется коротким пояснением на трёх языках (например, «Хрустящий картофель фри» / «Қытырлақ картоп фри» / «Crispy french fries»), потому что валидатор требует описание. Пустая карточка выглядит как ошибка загрузки.

- [ ] **Step 4: Перенести 43 позиции бара**

Источник: `bar_p1_full.png` и `bar_p2_full.png`.

Позиции с объёмом в названии («Американо (350 мл.)», «Латте (450 мл.)») переносятся отдельными строками, как в макете — это разные цены. Объём остаётся частью названия.

- [ ] **Step 5: Собрать список спорных переводов**

Создать `docs/перевод-на-проверку.md` со списком позиций, где перевод с казахского неоднозначен и требует слова владельца:

- «Ақсерке» — форель или лосось (встречается в 5 позициях);
- «қазы» — конская колбаса: оставить «казы» или перевести;
- «Пануоццо» — сохраняем итальянское написание;
- «Тіскебасарлар» — переведено как «Десерты»;
- английские названия блюд, где казахское описание содержит местные реалии.

- [ ] **Step 6: Проверить данные валидатором**

Run: `python3 -c "from build.data import load_menu; m = load_menu('data/menu.json'); print(len(m.categories), 'категорий,', len(m.items), 'позиций,', len(m.with_photos()), 'с фото')"`
Expected: `21 категорий, 104 позиций, 13 с фото`

- [ ] **Step 7: Commit**

```bash
git add data/menu.json docs/перевод-на-проверку.md
git commit -m "feat: меню на 104 позиции в трёх языках"
```

---

## Task 5: Языки и построение URL

**Files:**
- Create: `build/i18n.py`
- Test: `tests/test_i18n.py`

- [ ] **Step 1: Написать падающий тест**

```python
# tests/test_i18n.py
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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Запустить и убедиться, что падает**

Run: `python3 -m unittest tests.test_i18n -v`
Expected: FAIL — `No module named 'build.i18n'`

- [ ] **Step 3: Реализовать build/i18n.py**

Ключевая деталь: русский лежит в корне (`/menu/`), казахский под `/kz/`, английский под `/en/`. Код языка казахского в hreflang — `kk`, а в URL — `kz`, потому что так привычнее посетителю; путаница между этими двумя написаниями — типичный источник битых ссылок, поэтому преобразование живёт в одном месте.

```python
"""Языки, URL и строки интерфейса."""

LANGS = ("ru", "kk", "en")
LANG_DIR = {"ru": "", "kk": "kz", "en": "en"}
HTML_LANG = {"ru": "ru", "kk": "kk", "en": "en"}

UI = {
    "nav.menu":       {"ru": "Меню",        "kk": "Мәзір",        "en": "Menu"},
    "nav.breakfast":  {"ru": "Завтраки",    "kk": "Таңғы ас",     "en": "Breakfast"},
    "nav.about":      {"ru": "Наш дом",     "kk": "Біздің үй",    "en": "Our place"},
    "nav.contacts":   {"ru": "Контакты",    "kk": "Байланыс",     "en": "Contacts"},
    "cta.whatsapp":   {"ru": "Написать в WhatsApp", "kk": "WhatsApp-қа жазу", "en": "Message on WhatsApp"},
    "cta.menu":       {"ru": "Смотреть меню", "kk": "Мәзірді қарау", "en": "See the menu"},
    "cta.add":        {"ru": "В заказ",     "kk": "Тапсырысқа",   "en": "Add"},
    "cta.added":      {"ru": "Добавлено",   "kk": "Қосылды",      "en": "Added"},
    "cart.title":     {"ru": "Ваш заказ",   "kk": "Сіздің тапсырысыңыз", "en": "Your order"},
    "cart.empty":     {"ru": "Пока пусто. Выберите что-нибудь вкусное.",
                       "kk": "Әзірге бос. Дәмді бірдеңе таңдаңыз.",
                       "en": "Empty for now. Pick something tasty."},
    "cart.total":     {"ru": "Итого",       "kk": "Барлығы",      "en": "Total"},
    "cart.send":      {"ru": "Отправить в WhatsApp", "kk": "WhatsApp арқылы жіберу", "en": "Send via WhatsApp"},
    "cart.note":      {"ru": "Это заготовка сообщения — заказ подтвердится в переписке.",
                       "kk": "Бұл — хабарлама дайындамасы, тапсырыс хат алмасуда расталады.",
                       "en": "This only drafts a message — the order is confirmed in chat."},
    "cart.pickup":    {"ru": "Самовывоз",   "kk": "Өзім аламын",  "en": "Pickup"},
    "cart.dinein":    {"ru": "В зал",       "kk": "Залда",        "en": "Dine in"},
    "cart.items":     {"ru": "позиций",     "kk": "позиция",      "en": "items"},
    "hours.open":     {"ru": "Открыто сейчас", "kk": "Қазір ашық", "en": "Open now"},
    "hours.closed":   {"ru": "Сейчас закрыто", "kk": "Қазір жабық", "en": "Closed now"},
    "hours.today":    {"ru": "Сегодня до",  "kk": "Бүгін",        "en": "Today until"},
    "rating.reviews": {"ru": "отзывов на 2GIS", "kk": "2GIS-тегі пікір", "en": "reviews on 2GIS"},
    "menu.all":       {"ru": "Всё меню",    "kk": "Барлық мәзір", "en": "Full menu"},
    "dish.similar":   {"ru": "Похожие пиццы", "kk": "Ұқсас пиццалар", "en": "Similar pizzas"},
    "footer.rights":  {"ru": "Все права защищены", "kk": "Барлық құқықтар қорғалған", "en": "All rights reserved"},
    "skip.content":   {"ru": "Перейти к содержимому", "kk": "Мазмұнға өту", "en": "Skip to content"},
    "lang.switch":    {"ru": "Язык сайта",  "kk": "Сайт тілі",    "en": "Site language"},
}


def t(key, lang):
    try:
        return UI[key][lang]
    except KeyError:
        raise KeyError("нет строки интерфейса %r для языка %r" % (key, lang))


def url(lang, path=""):
    """Абсолютный путь внутри сайта: url('kk', 'menu') -> '/kz/menu/'"""
    parts = [p for p in (LANG_DIR[lang], path.strip("/")) if p]
    return "/" + "/".join(parts) + "/" if parts else "/"


def output_path(lang, path=""):
    """Путь файла внутри dist/: output_path('kk', 'menu') -> 'kz/menu/index.html'"""
    parts = [p for p in (LANG_DIR[lang], path.strip("/")) if p]
    return "/".join(parts + ["index.html"]) if parts else "index.html"


def alternate_urls(domain, path=""):
    """Карта hreflang для страницы, включая x-default на русскую версию."""
    domain = domain.rstrip("/")
    alts = {lang: domain + url(lang, path) for lang in LANGS}
    alts["x-default"] = domain + url("ru", path)
    return alts
```

- [ ] **Step 4: Запустить тест**

Run: `python3 -m unittest tests.test_i18n -v`
Expected: PASS, 6 тестов.

- [ ] **Step 5: Commit**

```bash
git add build/i18n.py tests/test_i18n.py && git commit -m "feat: языки, URL и строки интерфейса"
```

---

## Task 6: Подготовка изображений

**Files:**
- Create: `tools/prepare_images.py`
- Create: `src/img/logo/*.png`, `src/img/pizza/*.{webp,jpg}`

- [ ] **Step 1: Написать скрипт нарезки**

Исходники в scratch-каталоге (пути в шапке плана). Скрипт разовый: он переносит и сжимает картинки в `src/img/`, дальше репозиторий живёт без 3000×3000 оригиналов.

```python
"""Разовая подготовка изображений: логотипы и фото пицц.

Запускается вручную после появления новых фото:
    python3 tools/prepare_images.py <путь-к-исходникам>
"""

import sys
from pathlib import Path

from PIL import Image

WIDTHS = (400, 800, 1200)
PIZZA_ORDER = [
    ("x21", "pizza-margherita"),
    ("x18", "pizza-pepperoni"),
    ("x22", "pizza-meat-kazy"),
    ("x23", "pizza-salmon-broccoli"),
    ("x19", "pizza-bolognese"),
    ("x20", "pizza-stracciatella-lecho"),
    ("x34", "pizza-chicken-tomato"),
    ("x35", "pizza-meatballs"),
    ("x36", "pizza-shrimp"),
    ("x37", "pizza-strawberry-gorgonzola"),
    ("x38", "pizza-cheese"),
    ("x39", "pizza-truffle-mushroom"),
    ("x40", "pizza-carbonara"),
]


def prepare_pizzas(source, target):
    target.mkdir(parents=True, exist_ok=True)
    for raw_name, slug in PIZZA_ORDER:
        src = source / ("%s.png" % raw_name)
        if not src.exists():
            print("пропуск, нет файла: %s" % src)
            continue
        img = Image.open(src).convert("RGB")
        side = min(img.size)
        left = (img.width - side) // 2
        top = (img.height - side) // 2
        img = img.crop((left, top, left + side, top + side))
        for width in WIDTHS:
            resized = img.resize((width, width), Image.LANCZOS)
            resized.save(target / ("%s-%d.webp" % (slug, width)), "WEBP", quality=82, method=6)
            resized.save(target / ("%s-%d.jpg" % (slug, width)), "JPEG", quality=84, optimize=True)
        print("готово: %s" % slug)


def prepare_logos(source, target):
    target.mkdir(parents=True, exist_ok=True)
    for variant in ("white", "orange", "dark"):
        src = source / ("frnds-logo-%s.png" % variant)
        if not src.exists():
            print("пропуск, нет логотипа: %s" % src)
            continue
        img = Image.open(src)
        for width in (320, 640):
            height = round(img.height * width / img.width)
            out = img.resize((width, height), Image.LANCZOS)
            out.save(target / ("frnds-%s-%d.png" % (variant, width)), "PNG", optimize=True)
        print("готово: логотип %s" % variant)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    source = Path(sys.argv[1])
    root = Path(__file__).resolve().parent.parent
    prepare_pizzas(source / "menu" / "pizza_imgs", root / "src" / "img" / "pizza")
    prepare_logos(source, root / "src" / "img" / "logo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Запустить на извлечённых исходниках**

```bash
python3 tools/prepare_images.py "/private/tmp/claude-501/-Users-didar-Desktop------------hostel-22/b946e5ac-a4ba-42b5-8c9c-ed6d970cecea/scratchpad"
```

Expected: 13 строк «готово: pizza-…» и 3 строки «готово: логотип …».

- [ ] **Step 3: Проверить результат**

Run: `ls src/img/pizza | wc -l && ls src/img/logo && du -sh src/img`
Expected: 78 файлов пицц (13 × 3 размера × 2 формата), 6 логотипов, общий вес меньше 8 МБ.

- [ ] **Step 4: Убедиться, что фото соответствуют названиям**

Открыть `src/img/pizza/pizza-margherita-400.jpg` и `pizza-carbonara-400.jpg`. На первой должны быть томат, моцарелла и базилик; на второй — желток и бекон. Если перепутано, поправить соответствие в `PIZZA_ORDER` и перезапустить.

- [ ] **Step 5: Создать четыре недостающих файла-ассета**

Каркас страницы ссылается на фавикон и картинку для превью, страница «Наш дом» — на плейсхолдер интерьера, дизайн-система — на фирменный росчерк. Без них будут 404.

`src/img/favicon.svg` — оранжевый круг с рукописной «F»:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <circle cx="32" cy="32" r="32" fill="#FF7F17"/>
  <text x="32" y="46" font-family="Georgia, serif" font-style="italic"
        font-size="42" fill="#FFF" text-anchor="middle">F</text>
</svg>
```

`src/img/og-default.jpg` — превью для мессенджеров, 1200×630: фото Маргариты на кремовом фоне с логотипом. Собирается тем же скриптом:

```python
def prepare_og(source, target):
    target.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGB", (1200, 630), (253, 248, 243))
    pizza = Image.open(target.parent / "pizza" / "pizza-margherita-800.jpg").resize((520, 520), Image.LANCZOS)
    canvas.paste(pizza, (640, 55))
    logo = Image.open(source / "frnds-logo-orange.png")
    logo.thumbnail((420, 420), Image.LANCZOS)
    canvas.paste(logo, (70, 200), logo)
    canvas.save(target / "og-default.jpg", "JPEG", quality=88, optimize=True)
```

Вызвать из `main()`: `prepare_og(source, root / "src" / "img")`.

`src/img/interior/placeholder.svg` — кремовый прямоугольник 3:2 с надписью «Здесь будет фото зала» и подписью-комментарием в HTML рядом, чтобы владелец нашёл, куда класть снимки.

`src/img/stroke.svg` — фирменный росчерк из брендбука, тот самый графический мотив из спецификации (раздел 6). Извлекается из логотипа: берётся верхняя перекладина «F» как отдельный мазок, сохраняется одноцветным SVG с `fill="currentColor"`, чтобы перекрашиваться под контекст.

- [ ] **Step 6: Проверить, что ни один ассет не отдаёт 404**

Run: `ls src/img/favicon.svg src/img/og-default.jpg src/img/stroke.svg src/img/interior/placeholder.svg`
Expected: все четыре файла на месте.

- [ ] **Step 7: Commit**

```bash
git add tools/prepare_images.py src/img && git commit -m "feat: логотипы, фото пицц, фавикон и превью для мессенджеров"
```

---

## Task 7: Шрифты

**Files:**
- Create: `src/fonts/*.woff2`
- Create: `src/css/fonts.css`

- [ ] **Step 1: Скачать Manrope и Playfair Display**

Manrope заменяет платный Gilroy: та же геометрическая основа, свободная лицензия. Подмножество `cyrillic-ext` содержит казахские ә ғ қ ң ө ұ ү һ і.

```bash
mkdir -p src/fonts
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
curl -s -A "$UA" "https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Playfair+Display:wght@400;700&display=swap" -o /tmp/frnds-fonts.css
grep -oE "https://fonts.gstatic.com/[^)]+\.woff2" /tmp/frnds-fonts.css | sort -u | while read -r u; do
  curl -s "$u" -o "src/fonts/$(basename "$u")"
done
ls src/fonts | wc -l
```

- [ ] **Step 2: Проверить, что казахские буквы есть в шрифте**

Собрать `src/css/fonts.css` из `/tmp/frnds-fonts.css`, заменив URL на локальные пути, оставив только подмножества `latin`, `cyrillic`, `cyrillic-ext`. Затем создать временную проверочную страницу и открыть её в браузере:

```html
<!-- /tmp/font-check.html -->
<link rel="stylesheet" href="src/css/fonts.css">
<p style="font:600 40px Manrope">Әә Ғғ Ққ Ңң Өө Ұұ Үү Һһ Іі — Мәзір, тағамдар</p>
<p style="font:700 40px 'Playfair Display'">Frnds — Пицца және таңғы ас</p>
```

Expected: все девять казахских букв отрисованы шрифтом, а не подставлены системным — сравнить начертание с латиницей рядом. Если какая-то буква выпадает в системный шрифт, добавить подмножество или заменить гарнитуру.

- [ ] **Step 3: Commit**

```bash
git add src/fonts src/css/fonts.css && git commit -m "feat: локальные шрифты Manrope и Playfair Display"
```

---

## Task 8: Каркас страницы

**Files:**
- Create: `build/layout.py`
- Test: `tests/test_pages.py`

- [ ] **Step 1: Написать падающий тест**

```python
# tests/test_pages.py
import unittest

from build.data import Site
from build.layout import Page, render_page


def make_site():
    return Site({
        "domain": "https://frnds.kz",
        "phone": "+77074809215",
        "whatsapp": "77074809215",
        "instagram": "https://www.instagram.com/frnds.kz",
        "twogis": "https://2gis.kz/astana/firm/70000001113515854",
        "hours": {"open": "09:00", "close": "23:00"},
        "coords": {"lat": 51.119566, "lon": 71.484317},
        "address": {"ru": "Астана, улица Сағадат Нұрмағамбетов, 25",
                    "kk": "Астана, Сағадат Нұрмағамбетов көшесі, 25",
                    "en": "Astana, Sagadat Nurmagambetov Street 25"},
        "rating": {"value": 4.9, "count": 182},
        "aggregators": [],
    })


class TestRenderPage(unittest.TestCase):
    def setUp(self):
        self.html = render_page(Page(
            lang="ru", path="menu", title="Меню Frnds",
            description="Всё меню пиццерии Frnds в Астане",
            body="<main id=\"main\"><h1>Меню</h1></main>",
        ), make_site())

    def test_has_doctype_and_lang(self):
        self.assertTrue(self.html.startswith("<!DOCTYPE html>"))
        self.assertIn('<html lang="ru">', self.html)

    def test_has_title_and_description(self):
        self.assertIn("<title>Меню Frnds</title>", self.html)
        self.assertIn('name="description" content="Всё меню пиццерии Frnds в Астане"', self.html)

    def test_has_canonical_and_hreflang(self):
        self.assertIn('rel="canonical" href="https://frnds.kz/menu/"', self.html)
        self.assertIn('hreflang="kk" href="https://frnds.kz/kz/menu/"', self.html)
        self.assertIn('hreflang="en" href="https://frnds.kz/en/menu/"', self.html)
        self.assertIn('hreflang="x-default" href="https://frnds.kz/menu/"', self.html)

    def test_escapes_title(self):
        html = render_page(Page(
            lang="ru", path="", title='Пицца "Маргарита" & кофе',
            description="d", body="<main></main>",
        ), make_site())
        self.assertIn("&quot;Маргарита&quot;", html)
        self.assertIn("&amp; кофе", html)

    def test_has_open_graph(self):
        self.assertIn('property="og:title"', self.html)
        self.assertIn('property="og:url" content="https://frnds.kz/menu/"', self.html)

    def test_has_skip_link_and_main(self):
        self.assertIn('href="#main"', self.html)
        self.assertIn('id="main"', self.html)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Запустить и убедиться, что падает**

Run: `python3 -m unittest tests.test_pages -v`
Expected: FAIL — `No module named 'build.layout'`

- [ ] **Step 3: Реализовать build/layout.py**

```python
"""Каркас HTML-страницы: head, мета-теги, hreflang, подключение ассетов."""

from html import escape

from build.i18n import HTML_LANG, alternate_urls, t, url


class Page:
    """Всё, что нужно знать каркасу о конкретной странице."""

    __slots__ = ("lang", "path", "title", "description", "body",
                 "og_image", "json_ld", "body_class")

    def __init__(self, lang, path, title, description, body,
                 og_image="", json_ld=None, body_class=""):
        self.lang = lang
        self.path = path
        self.title = title
        self.description = description
        self.body = body
        self.og_image = og_image
        self.json_ld = json_ld or []
        self.body_class = body_class


def _meta(name, content, attr="name"):
    return '  <meta %s="%s" content="%s">' % (attr, name, escape(content, quote=True))


def render_page(page, site, header="", footer=""):
    alts = alternate_urls(site.domain, page.path)
    canonical = alts[page.lang]
    og_image = page.og_image or (site.domain + "/img/og-default.jpg")

    head = [
        "<!DOCTYPE html>",
        '<html lang="%s">' % HTML_LANG[page.lang],
        "<head>",
        '  <meta charset="utf-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1">',
        "  <title>%s</title>" % escape(page.title),
        _meta("description", page.description),
        '  <link rel="canonical" href="%s">' % canonical,
    ]
    for lang in ("ru", "kk", "en", "x-default"):
        head.append('  <link rel="alternate" hreflang="%s" href="%s">' % (lang, alts[lang]))

    head += [
        _meta("og:title", page.title, attr="property"),
        _meta("og:description", page.description, attr="property"),
        _meta("og:url", canonical, attr="property"),
        _meta("og:image", og_image, attr="property"),
        _meta("og:type", "website", attr="property"),
        _meta("og:site_name", "Frnds", attr="property"),
        _meta("twitter:card", "summary_large_image"),
        _meta("theme-color", "#FF7F17"),
        '  <link rel="icon" href="/img/favicon.svg" type="image/svg+xml">',
        '  <link rel="stylesheet" href="/css/fonts.css">',
        '  <link rel="stylesheet" href="/css/style.css">',
    ]
    for block in page.json_ld:
        head.append('  <script type="application/ld+json">%s</script>' % block)
    head += ['  <script src="/js/nav.js" defer></script>',
             '  <script src="/js/cart.js" defer></script>',
             "</head>"]

    body_class = ' class="%s"' % page.body_class if page.body_class else ""
    body = [
        "<body%s data-lang=\"%s\">" % (body_class, page.lang),
        '<a class="skip-link" href="#main">%s</a>' % escape(t("skip.content", page.lang)),
        header,
        page.body,
        footer,
        "</body>",
        "</html>",
    ]
    return "\n".join(head + body)
```

- [ ] **Step 4: Запустить тест**

Run: `python3 -m unittest tests.test_pages -v`
Expected: PASS, 6 тестов.

- [ ] **Step 5: Commit**

```bash
git add build/layout.py tests/test_pages.py && git commit -m "feat: каркас страницы с мета-тегами и hreflang"
```

---

## Task 9: Компоненты

**Files:**
- Create: `build/components.py`
- Modify: `tests/test_pages.py` — дописать класс `TestComponents`

- [ ] **Step 1: Дописать падающие тесты**

```python
# в tests/test_pages.py, после существующих классов
from build.components import dish_card, header, footer, price_pill
from build.data import Item


def make_item(**over):
    raw = {"id": "pizza-pepperoni", "category": "pizza", "price": 3590,
           "photo": "pizza-pepperoni", "badges": ["hit"], "tags": ["spicy"],
           "name": {"ru": "Пепперони", "kk": "Пепперони", "en": "Pepperoni"},
           "desc": {"ru": "Острая пепперони и моцарелла.",
                    "kk": "Ащы пепперони мен моцарелла.",
                    "en": "Spicy pepperoni and mozzarella."}}
    raw.update(over)
    return Item(raw)


class TestComponents(unittest.TestCase):
    def test_price_pill_formats_thousands_with_space(self):
        html = price_pill(3590, "ru")
        self.assertIn("3 590", html)
        self.assertIn("₸", html)

    def test_dish_card_carries_data_for_cart(self):
        html = dish_card(make_item(), "ru")
        self.assertIn('data-item-id="pizza-pepperoni"', html)
        self.assertIn('data-item-price="3590"', html)
        self.assertIn("Пепперони", html)

    def test_dish_card_with_photo_uses_picture(self):
        html = dish_card(make_item(), "ru")
        self.assertIn("<picture", html)
        self.assertIn("pizza-pepperoni-400.webp", html)
        self.assertIn('loading="lazy"', html)
        self.assertIn('width="400" height="400"', html)

    def test_dish_card_without_photo_has_no_picture(self):
        html = dish_card(make_item(photo=""), "ru")
        self.assertNotIn("<picture", html)
        self.assertIn("Пепперони", html)

    def test_dish_card_escapes_text(self):
        html = dish_card(make_item(name={"ru": 'Пицца "Хит" & Co',
                                        "kk": "a", "en": "b"}), "ru")
        self.assertIn("&quot;Хит&quot;", html)
        self.assertNotIn('"Хит"', html)

    def test_header_has_nav_and_lang_switch(self):
        html = header("ru", make_site())
        self.assertIn('href="/menu/"', html)
        self.assertIn('href="/kz/"', html)
        self.assertIn('href="/en/"', html)
        self.assertIn("wa.me/77074809215", html)

    def test_footer_has_clickable_phone(self):
        html = footer("ru", make_site())
        self.assertIn('href="tel:+77074809215"', html)
        self.assertIn("2gis.kz", html)
```

- [ ] **Step 2: Запустить и убедиться, что падает**

Run: `python3 -m unittest tests.test_pages -v`
Expected: FAIL — `No module named 'build.components'`

- [ ] **Step 3: Реализовать build/components.py**

Компоненты — чистые функции: получают данные, возвращают строку, ничего не читают с диска. `escape` вызывается на каждом пользовательском тексте.

```python
"""Переиспользуемые куски разметки."""

from html import escape

from build.i18n import LANGS, t, url

TAG_EMOJI = {"spicy": "🌶", "veg": "🌿", "kids": "👶"}
BADGE_TEXT = {
    "hit": {"ru": "хит", "kk": "хит", "en": "popular"},
    "new": {"ru": "новинка", "kk": "жаңа", "en": "new"},
}


def money(value, lang):
    """3590 -> '3 590 ₸' — узкий пробел, чтобы цена не разрывалась."""
    digits = "{:,}".format(int(value)).replace(",", "\u202f")
    return "%s\u202f₸" % digits


def price_pill(price, lang, item_id=""):
    attrs = ' data-add="%s"' % escape(item_id, quote=True) if item_id else ""
    return (
        '<button class="pill pill--price" type="button"%s>'
        '<span class="pill__price">%s</span>'
        '<span class="pill__action">%s</span>'
        "</button>" % (attrs, money(price, lang), escape(t("cta.add", lang)))
    )


def _picture(slug, alt):
    base = "/img/pizza/%s" % slug
    return (
        "<picture>"
        '<source type="image/webp" srcset="%(b)s-400.webp 400w, %(b)s-800.webp 800w, %(b)s-1200.webp 1200w" '
        'sizes="(max-width: 700px) 45vw, 280px">'
        '<img src="%(b)s-400.jpg" alt="%(alt)s" width="400" height="400" loading="lazy" decoding="async">'
        "</picture>" % {"b": base, "alt": escape(alt, quote=True)}
    )


def dish_card(item, lang):
    name = item.name[lang]
    emoji = "".join(TAG_EMOJI.get(tag, "") for tag in item.tags)
    badges = "".join(
        '<span class="badge">%s</span>' % escape(BADGE_TEXT[b][lang])
        for b in item.badges if b in BADGE_TEXT
    )
    media = ""
    if item.photo:
        alt = "%s — Frnds, Астана" % name
        media = '<div class="card__media">%s%s</div>' % (_picture(item.photo, alt), badges)

    href = url(lang, "menu/%s" % item.id) if item.photo else ""
    title = escape(name) + (" " + emoji if emoji else "")
    heading = (
        '<h3 class="card__title"><a href="%s">%s</a></h3>' % (href, title)
        if href else '<h3 class="card__title">%s</h3>' % title
    )

    return (
        '<article class="card" data-item-id="%s" data-item-price="%d" data-item-name="%s">'
        "%s"
        '<div class="card__body">%s'
        '<p class="card__desc">%s</p>'
        '<div class="card__foot">%s</div>'
        "</div></article>"
        % (escape(item.id, quote=True), item.price, escape(name, quote=True),
           media, heading, escape(item.desc[lang]), price_pill(item.price, lang, item.id))
    )


def _logo(lang):
    return (
        '<a class="logo" href="%s" aria-label="Frnds — на главную">'
        '<img src="/img/logo/frnds-orange-320.png" alt="Frnds" width="160" height="75">'
        "</a>" % url(lang, "")
    )


def _lang_switch(lang, path=""):
    labels = {"ru": "RU", "kk": "KZ", "en": "EN"}
    links = "".join(
        '<a href="%s"%s>%s</a>' % (url(code, path),
                                   ' aria-current="true"' if code == lang else "",
                                   labels[code])
        for code in LANGS
    )
    return '<nav class="lang" aria-label="%s">%s</nav>' % (escape(t("lang.switch", lang)), links)


def header(lang, site, path=""):
    nav_items = [("nav.menu", "menu"), ("nav.breakfast", "breakfast"),
                 ("nav.about", "about"), ("nav.contacts", "contacts")]
    links = "".join(
        '<a href="%s">%s</a>' % (url(lang, target), escape(t(key, lang)))
        for key, target in nav_items
    )
    wa = "https://wa.me/%s" % site.whatsapp
    return (
        '<header class="header">'
        '<div class="container header__inner">'
        "%(logo)s"
        '<nav class="nav" aria-label="%(navlabel)s">%(links)s</nav>'
        '<div class="header__meta">'
        '<span class="dot" aria-hidden="true"></span>'
        '<span>%(hours)s %(close)s</span>'
        '<span class="header__rating">%(rating)s★</span>'
        "</div>"
        "%(lang)s"
        '<a class="pill pill--brand header__cta" href="%(wa)s" rel="noopener" target="_blank">%(cta)s</a>'
        '<button class="burger" type="button" aria-expanded="false" aria-controls="mobile-nav" '
        'aria-label="%(navlabel)s"><span></span><span></span><span></span></button>'
        "</div>"
        '<div class="mobile-nav" id="mobile-nav" hidden>%(links)s%(lang)s</div>'
        "</header>"
        % {"logo": _logo(lang), "links": links, "lang": _lang_switch(lang, path),
           "wa": wa, "cta": escape(t("cta.whatsapp", lang)),
           "navlabel": escape(t("nav.menu", lang)),
           "hours": escape(t("hours.today", lang)), "close": site.hours["close"],
           "rating": site.rating["value"]}
    )


def footer(lang, site):
    sections = [("nav.menu", "menu"), ("nav.breakfast", "breakfast"),
                ("nav.about", "about"), ("nav.contacts", "contacts")]
    links = "".join(
        '<a href="%s">%s</a>' % (url(lang, target), escape(t(key, lang)))
        for key, target in sections
    )
    return (
        '<footer class="footer">'
        '<div class="container footer__inner">'
        '<div class="footer__col">'
        '<img src="/img/logo/frnds-white-320.png" alt="Frnds" width="140" height="65">'
        "<p>%(address)s</p>"
        "<p>%(open)s — %(close)s</p>"
        "</div>"
        '<div class="footer__col"><nav aria-label="%(navlabel)s">%(links)s</nav></div>'
        '<div class="footer__col">'
        '<a href="tel:%(phone)s">%(phone)s</a>'
        '<a href="https://wa.me/%(wa)s" rel="noopener" target="_blank">WhatsApp</a>'
        '<a href="%(ig)s" rel="noopener" target="_blank">Instagram</a>'
        '<a href="%(gis)s" rel="noopener" target="_blank">2GIS</a>'
        "</div>"
        "</div>"
        '<div class="container footer__legal">© 2026 Frnds · %(rights)s</div>'
        "</footer>"
        % {"address": escape(site.address[lang]), "open": site.hours["open"],
           "close": site.hours["close"], "links": links,
           "navlabel": escape(t("nav.menu", lang)),
           "phone": escape(site.phone), "wa": escape(site.whatsapp),
           "ig": escape(site.instagram), "gis": escape(site.twogis),
           "rights": escape(t("footer.rights", lang))}
    )
```

- [ ] **Step 4: Запустить тест**

Run: `python3 -m unittest tests.test_pages -v`
Expected: PASS, 13 тестов.

- [ ] **Step 5: Commit**

```bash
git add build/components.py tests/test_pages.py && git commit -m "feat: компоненты разметки — шапка, подвал, карточка блюда"
```

---

## Task 10: Дизайн-система в CSS

**Files:**
- Create: `src/css/style.css`
- Test: `tests/test_contrast.py`

- [ ] **Step 1: Написать тест контрастов**

Тест защищает главное решение спецификации: белый текст на брендовом оранжевом даёт 2.53:1 и запрещён.

```python
# tests/test_contrast.py
import re
import unittest
from pathlib import Path

CSS = Path("src/css/style.css")


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

    def test_large_brand_heading_on_cream_passes_large_threshold(self):
        self.assertGreaterEqual(contrast(self.token("brand-deep"), self.token("cream")), 3.0)

    def test_no_white_text_on_brand_fill(self):
        """Белое по #FF7F17 — 2.53:1. Ловим попытку вернуть это в стили."""
        pattern = re.compile(
            r"\.pill--brand\s*\{[^}]*color:\s*(#fff|#ffffff|white)", re.I | re.S)
        self.assertIsNone(pattern.search(self.css),
                          "белый текст на брендовой заливке запрещён: контраст 2.53:1")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Запустить и убедиться, что падает**

Run: `python3 -m unittest tests.test_contrast -v`
Expected: FAIL — `FileNotFoundError: src/css/style.css`

- [ ] **Step 3: Написать style.css**

Начать с токенов — тест смотрит именно на них:

```css
:root {
  --brand: #FF7F17;        /* заливка; текст поверх — тёмный, не белый */
  --brand-deep: #D96410;   /* крупные заголовки, от 24px bold */
  --brand-text: #A84C08;   /* мелкий текст брендовым цветом: цены, ссылки */
  --cream: #FDF8F3;
  --surface: #FFFFFF;
  --ink: #1A1A1A;
  --ink-soft: rgba(26, 26, 26, .62);
  --line: rgba(26, 26, 26, .10);
  --success: #2E9E5B;

  --radius-card: 24px;
  --radius-pill: 9999px;
  --container: 1180px;
  --gap: 24px;
}
```

Дальше по разделам, в этом порядке: сброс и базовая типографика → контейнер и сетка → шапка → мобильная навигация → герой → карточка блюда → пилюля-цена → якорная навигация → нижний бар корзины → панель заказа → подвал → медиа-запросы → `prefers-reduced-motion`.

Обязательные требования, вытекающие из спецификации:

```css
body {
  margin: 0;
  background: var(--cream);
  color: var(--ink);
  font: 400 16px/1.6 Manrope, system-ui, sans-serif;
}

h1, h2, h3 { letter-spacing: -.02em; line-height: 1.15; margin: 0 0 .5em; }
h1 { font-size: clamp(32px, 5vw, 48px); font-weight: 800; }
h2 { font-size: clamp(24px, 3.4vw, 32px); font-weight: 700; }

.display { font-family: 'Playfair Display', Georgia, serif; font-weight: 700; }

/* Пилюля-цена: цена и есть кнопка. На ховере раздувается и меняет текст. */
.pill--price {
  display: inline-flex; align-items: center; gap: 8px;
  min-height: 36px; padding: 9px 14px;
  border: 0; border-radius: var(--radius-pill);
  background: var(--cream); color: var(--brand-text);
  font: 600 14px/1 Manrope, sans-serif; cursor: pointer;
  transition: background-color .2s ease-out, color .2s ease-out, padding .2s ease-out;
}
.pill--price .pill__action { display: none; }
.pill--price:hover, .pill--price:focus-visible {
  background: var(--brand); color: var(--ink);   /* 6.88:1 */
  padding: 12px 20px; min-height: 44px;
}
.pill--price:hover .pill__action,
.pill--price:focus-visible .pill__action { display: inline; }

.pill--brand { background: var(--brand); color: var(--ink); }

.skip-link {
  position: absolute; left: -9999px;
}
.skip-link:focus { left: 16px; top: 16px; z-index: 999; padding: 12px 18px;
  background: var(--ink); color: var(--surface); border-radius: var(--radius-pill); }

:focus-visible { outline: 3px solid var(--brand-deep); outline-offset: 2px; }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; }
}
```

Сетка карточек: 4 колонки от 1100px, 3 от 860px, 2 на мобильном — как в макете Dodo, где 2 колонки на телефоне остаются читаемыми.

- [ ] **Step 4: Запустить тест**

Run: `python3 -m unittest tests.test_contrast -v`
Expected: PASS, 5 тестов.

- [ ] **Step 5: Commit**

```bash
git add src/css/style.css tests/test_contrast.py && git commit -m "feat: дизайн-система с проверяемыми контрастами"
```

---

## Task 11: Главная страница

**Files:**
- Create: `build/pages/home.py`
- Create: `data/pages/home.ru.json`, `home.kk.json`, `home.en.json`

- [ ] **Step 1: Написать тексты главной**

`data/pages/home.ru.json`:

```json
{
  "seo_title": "Frnds — пиццерия и завтраки весь день в Астане",
  "seo_description": "Пицца на дровах, паста и завтраки весь день. Астана, Сағадат Нұрмағамбетов, 25. Ежедневно с 09:00 до 23:00. Заказ в WhatsApp.",
  "hero_kicker": "Пицца и завтраки весь день",
  "hero_text": "Заходите к нам как к своим: тёплый свет, кофе на любой вкус и пицца, которую мы печём с той же любовью, с какой готовят дома.",
  "hits_title": "Берут чаще всего",
  "breakfast_title": "Завтраки весь день",
  "breakfast_text": "Проспали? У нас это не проблема. Сырники, скрэмбл, шакшука и вафли готовим с открытия до закрытия — в девять утра и в девять вечера одинаково.",
  "about_title": "Дом вне дома",
  "about_text": "Frnds — это про друзей. Мы вдохновлялись Бруклином, а готовим в Астане: та же простая честная еда, за которой хочется задержаться подольше.",
  "howto_title": "Как забрать",
  "reviews_title": "Что о нас говорят"
}
```

Казахская и английская версии — те же ключи. Казахский тон — на «сіз», как договорились.

- [ ] **Step 2: Реализовать build/pages/home.py**

**Единый контракт всех страничных модулей:** каждый экспортирует `build(site, menu, texts, lang) -> Page`. Никаких `render`, никаких других сигнатур — `build.py` вызывает их единообразно в цикле. Модуль `dish` — исключение по аргументам (`build(site, menu, item, lang)`), потому что получает конкретное блюдо, а `geo` экспортирует `build_all(site, menu, lang) -> list[Page]`.

```python
"""Главная страница."""

from html import escape

from build.components import dish_card
from build.i18n import t, url
from build.layout import Page
from build.seo import restaurant_jsonld


def _hero(site, menu, texts, lang):
    wa = "https://wa.me/%s" % site.whatsapp
    return (
        '<section class="hero">'
        '<div class="container hero__inner">'
        '<div class="hero__text">'
        '<img class="hero__logo" src="/img/logo/frnds-orange-640.png" alt="Frnds"'
        ' width="320" height="149" fetchpriority="high">'
        '<p class="hero__kicker">%(kicker)s</p>'
        '<p class="hero__lead">%(lead)s</p>'
        '<div class="hero__actions">'
        '<a class="pill pill--brand" href="%(menu_url)s">%(cta_menu)s</a>'
        '<a class="pill pill--ghost" href="%(wa)s" rel="noopener" target="_blank">%(cta_wa)s</a>'
        "</div>"
        '<p class="hero__meta"><span class="dot"></span>%(address)s · %(today)s %(close)s</p>'
        "</div>"
        '<div class="hero__media"><span class="hero__circle" aria-hidden="true"></span>'
        '<img src="/img/pizza/pizza-margherita-800.jpg" alt="%(alt)s"'
        ' width="800" height="800" fetchpriority="high">'
        "</div></div></section>"
        % {"kicker": escape(texts["hero_kicker"]), "lead": escape(texts["hero_text"]),
           "menu_url": url(lang, "menu"), "cta_menu": escape(t("cta.menu", lang)),
           "wa": wa, "cta_wa": escape(t("cta.whatsapp", lang)),
           "address": escape(site.address[lang]), "today": escape(t("hours.today", lang)),
           "close": site.hours["close"], "alt": escape("Пицца Маргарита — Frnds, Астана", quote=True)}
    )


def _hits(menu, texts, lang):
    cards = "".join(dish_card(item, lang) for item in menu.by_category("pizza")[:6])
    return (
        '<section class="section"><div class="container">'
        '<h2 class="display">%s</h2><div class="grid">%s</div>'
        '<p class="section__more"><a href="%s">%s</a></p>'
        "</div></section>"
        % (escape(texts["hits_title"]), cards, url(lang, "menu"), escape(t("menu.all", lang)))
    )


def build(site, menu, texts, lang):
    body = "".join([
        '<main id="main">',
        _hero(site, menu, texts, lang),
        _hits(menu, texts, lang),
        _breakfast(menu, texts, lang),
        _about(texts, lang),
        _reviews(site, texts, lang),
        _howto(site, texts, lang),
        _map(site, lang),
        "</main>",
    ])
    return Page(
        lang=lang, path="", title=texts["seo_title"], description=texts["seo_description"],
        body=body, og_image=site.domain + "/img/pizza/pizza-margherita-1200.jpg",
        json_ld=[restaurant_jsonld(site, lang)], body_class="page-home",
    )
```

Остальные секции пишутся по тому же образцу — чистая функция принимает данные, возвращает строку:

- `_breakfast` — широкий блок с текстом `texts["breakfast_text"]` и ссылкой на `/breakfast/`.
- `_about` — два абзаца концепции, рукописный росчерк водяным знаком, место под фото зала.
- `_reviews` — `site.rating["value"]`, `site.rating["count"]`, три цитаты из `texts["reviews"]` (реальные, из 2GIS), ссылка на `site.twogis`.
- `_howto` — три плитки: зал, самовывоз, агрегаторы. Плитка агрегаторов не выводится, если `site.aggregators` пуст.
- `_map` — `<div id="map" data-lat="…" data-lon="…"></div>`, инициализируется в `nav.js`.

- [ ] **Step 3: Проверить сборку страницы**

Run: `python3 -c "
from build.data import load_menu, load_site, load_page
from build.pages import home
site, menu = load_site('data/site.json'), load_menu('data/menu.json')
page = home.build(site, menu, load_page('data/pages', 'home', 'ru'), 'ru')
print(len(page.body), 'символов'); assert 'Frnds' in page.body and 'wa.me' in page.body
assert page.path == '' and page.title"`
Expected: число символов больше 8000, ошибок нет.

- [ ] **Step 4: Commit**

```bash
git add build/pages/home.py data/pages/home.*.json && git commit -m "feat: главная страница"
```

---

## Task 12: Страница меню

**Files:**
- Create: `build/pages/menu.py`
- Create: `data/pages/menu.{ru,kk,en}.json`

- [ ] **Step 1: Реализовать страницу**

Сигнатура та же: `build(site, menu, texts, lang) -> Page`, `path="menu"`.

Липкая якорная навигация по 21 разделу: чипы со ссылками `#<category-id>`, активный подсвечивается скролл-шпионом из `nav.js`.

Разделы с фото (`pizza`) рендерятся сеткой карточек через `dish_card`. Разделы без фото — плотным списком, потому что 91 карточка без изображения читается как несработавшая загрузка (решение из спецификации, раздел 7):

```python
def _dense_row(item, lang):
    from html import escape

    from build.components import price_pill
    return (
        '<li class="row" data-item-id="%s" data-item-price="%d" data-item-name="%s">'
        '<div class="row__text"><h3 class="row__title">%s</h3>'
        '<p class="row__desc">%s</p></div>'
        '<div class="row__price">%s</div></li>'
        % (escape(item.id, quote=True), item.price, escape(item.name[lang], quote=True),
           escape(item.name[lang]), escape(item.desc[lang]), price_pill(item.price, lang, item.id))
    )
```

`data-`атрибуты обязаны быть и в плотной строке, и в карточке — корзина ищет их одинаково, независимо от вида раздела.

- [ ] **Step 2: Проверить, что все позиции попали на страницу**

Дописать в `tests/test_pages.py`:

```python
class TestMenuPage(unittest.TestCase):
    def setUp(self):
        from build.data import load_menu, load_page, load_site
        from build.pages import menu as menu_page
        self.menu = load_menu("data/menu.json")
        site = load_site("data/site.json")
        self.page = menu_page.build(site, self.menu, load_page("data/pages", "menu", "ru"), "ru")

    def test_every_item_appears_on_the_page(self):
        missing = [i.id for i in self.menu.items
                   if 'data-item-id="%s"' % i.id not in self.page.body]
        self.assertEqual(missing, [], "не попали в меню: %s" % missing)

    def test_every_category_has_an_anchor(self):
        for cat in self.menu.categories:
            self.assertIn('id="%s"' % cat.id, self.page.body)

    def test_every_item_is_addable_to_cart(self):
        """И карточки, и плотные строки несут цену для корзины."""
        for item in self.menu.items:
            self.assertIn('data-item-price="%d"' % item.price, self.page.body)
```

Run: `python3 -m unittest tests.test_pages -v`
Expected: PASS — все 104 позиции и 21 якорь на месте.

- [ ] **Step 3: Commit**

```bash
git add build/pages/menu.py data/pages/menu.*.json tests/test_pages.py
git commit -m "feat: страница меню с якорной навигацией"
```

---

## Task 13: Страницы пицц

**Files:**
- Create: `build/pages/dish.py`
- Test: дописать `tests/test_pages.py`

- [ ] **Step 1: Написать падающий тест**

```python
class TestDishPage(unittest.TestCase):
    def test_has_h1_price_and_structured_data(self):
        from build.data import load_menu, load_site
        from build.pages import dish
        site, menu = load_site("data/site.json"), load_menu("data/menu.json")
        item = menu.get("pizza-carbonara")
        page = dish.build(site, menu, item, "ru")
        self.assertIn("<h1", page.body)
        self.assertIn("Карбонара", page.body)
        self.assertIn("3\u202f990", page.body)
        self.assertTrue(any("MenuItem" in block for block in page.json_ld))

    def test_path_matches_menu_link(self):
        from build.data import load_menu, load_site
        from build.pages import dish
        site, menu = load_site("data/site.json"), load_menu("data/menu.json")
        page = dish.build(site, menu, menu.get("pizza-cheese"), "en")
        self.assertEqual(page.path, "menu/pizza-cheese")
```

- [ ] **Step 2: Запустить, убедиться, что падает**

Run: `python3 -m unittest tests.test_pages.TestDishPage -v`
Expected: FAIL — нет модуля `build.pages.dish`.

- [ ] **Step 3: Реализовать**

`build(site, menu, item, lang)` возвращает готовый `Page`: фото 1200px, `h1`, состав, цена с кнопкой добавления, хлебные крошки, блок «Похожие пиццы» (3 случайные другие пиццы — берутся по порядку, без `random`, чтобы сборка была воспроизводимой), JSON-LD `MenuItem` с ценой и валютой KZT.

`og_image` — фото этой пиццы: превью ссылки в WhatsApp показывает именно её.

- [ ] **Step 4: Запустить тест**

Run: `python3 -m unittest tests.test_pages -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add build/pages/dish.py tests/test_pages.py && git commit -m "feat: страницы пицц с микроразметкой"
```

---

## Task 14: Остальные страницы

**Files:**
- Create: `build/pages/breakfast.py`, `about.py`, `contacts.py`
- Create: `data/pages/{breakfast,about,contacts}.{ru,kk,en}.json`

- [ ] **Step 1: Завтраки**

Ключевой SEO-актив: «завтраки весь день» — то, чем заведение отличается от пиццерий. Все 13 позиций раздела, текст про режим «с 09:00 до 23:00», гео-упоминание левого берега и Есильского района, кнопка WhatsApp.

- [ ] **Step 2: Наш дом**

Концепция: «дом вне дома», «вдохновляясь Бруклином, готовим в Астане». Место под фото зала — плейсхолдер `img/interior/placeholder.svg` с подписью-комментарием в HTML, чтобы владелец нашёл, куда класть фото.

- [ ] **Step 3: Контакты**

Адрес, часы, кликабельный `tel:`, WhatsApp, Instagram, 2GIS, карта Leaflet, ориентиры («левый берег, рядом с Хан Шатыром»), JSON-LD `Restaurant`.

- [ ] **Step 4: Проверить, что все три страницы собираются на трёх языках**

Все три модуля соблюдают общий контракт `build(site, menu, texts, lang) -> Page` с путями `breakfast`, `about`, `contacts`.

Run: `python3 -c "
from build.data import load_menu, load_site, load_page
from build.pages import breakfast, about, contacts
site, menu = load_site('data/site.json'), load_menu('data/menu.json')
for mod, name in ((breakfast,'breakfast'), (about,'about'), (contacts,'contacts')):
    for lang in ('ru','kk','en'):
        page = mod.build(site, menu, load_page('data/pages', name, lang), lang)
        assert page.path == name, (name, page.path)
        assert len(page.body) > 1500, (name, lang, len(page.body))
print('все девять страниц собрались')"`
Expected: `все девять страниц собрались`

- [ ] **Step 5: Commit**

```bash
git add build/pages/breakfast.py build/pages/about.py build/pages/contacts.py data/pages
git commit -m "feat: страницы завтраков, о заведении и контактов"
```

---

## Task 15: Гео-страницы

**Files:**
- Create: `build/pages/geo.py`
- Create: `data/pages/geo-<slug>.{ru,kk,en}.json` — 5 районов × 3 языка

- [ ] **Step 1: Написать тексты пяти районов**

Слаги и заголовки:

| slug | ru `h1` |
|---|---|
| `esil` | Пиццерия и завтраки в Есильском районе Астаны |
| `levyi-bereg` | Пицца и завтраки на левом берегу Астаны |
| `saryarka` | Пиццерия для района Сарыарка |
| `almaty-rayon` | Пиццерия для Алматинского района Астаны |
| `baikonyr` | Пиццерия для района Байконур |

Каждый текст — 300–400 слов, свой, а не клон с подменённым словом. Для левого берега и Есиля — ориентиры (Хан Шатыр, Абу-Даби Плаза, Триумф Астаны) и то, что заведение прямо здесь. Для правобережных районов — честно: мы на левом берегу, дорога займёт столько-то, работаем на самовывоз и через агрегаторы. Обещать доставку, которой нет, нельзя.

- [ ] **Step 2: Реализовать генерацию**

`build_all(site, menu, lang) -> list[Page]` — по одной странице на район, `path` равен слагу района. Каждая содержит: `h1`, текст, 6 карточек популярных пицц, карту, кнопку WhatsApp, ссылку на полное меню, JSON-LD `Restaurant` с `areaServed`.

```python
GEO_SLUGS = ("esil", "levyi-bereg", "saryarka", "almaty-rayon", "baikonyr")


def build_all(site, menu, lang):
    from build.data import load_page
    pages = []
    for slug in GEO_SLUGS:
        texts = load_page("data/pages", "geo-%s" % slug, lang)
        pages.append(_build_one(site, menu, texts, slug, lang))
    return pages
```

- [ ] **Step 3: Проверить уникальность текстов**

Дописать тест: тексты двух любых гео-страниц не совпадают более чем на 60% по словам — защита от копипасты, за которую Google наказывает.

```python
class TestGeoPages(unittest.TestCase):
    def test_texts_are_not_near_duplicates(self):
        from build.data import load_page
        texts = {}
        for slug in ("esil", "levyi-bereg", "saryarka", "almaty-rayon", "baikonyr"):
            data = load_page("data/pages", "geo-%s" % slug, "ru")
            texts[slug] = set(data["body"].split())
        slugs = list(texts)
        for i, a in enumerate(slugs):
            for b in slugs[i + 1:]:
                overlap = len(texts[a] & texts[b]) / max(1, len(texts[a] | texts[b]))
                self.assertLess(overlap, 0.6, "тексты %s и %s слишком похожи" % (a, b))
```

Run: `python3 -m unittest tests.test_pages.TestGeoPages -v`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add build/pages/geo.py data/pages/geo-*.json tests/test_pages.py
git commit -m "feat: пять гео-страниц по районам Астаны"
```

---

## Task 16: SEO-файлы

**Files:**
- Create: `build/seo.py`
- Test: `tests/test_seo.py`

- [ ] **Step 1: Написать падающий тест**

```python
# tests/test_seo.py
import unittest
import xml.etree.ElementTree as ET

from build.seo import restaurant_jsonld, robots_txt, sitemap_xml
from tests.test_pages import make_site


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
        import json
        data = json.loads(restaurant_jsonld(make_site(), "ru"))
        self.assertEqual(data["@type"], "Restaurant")
        self.assertEqual(data["aggregateRating"]["ratingValue"], 4.9)
        self.assertEqual(data["aggregateRating"]["reviewCount"], 182)
        self.assertIn("geo", data)
        self.assertIn("openingHoursSpecification", data)
```

- [ ] **Step 2: Запустить, убедиться, что падает**

Run: `python3 -m unittest tests.test_seo -v`
Expected: FAIL — нет `build.seo`.

- [ ] **Step 3: Реализовать build/seo.py**

`sitemap_xml(domain, paths)` разворачивает каждый путь на три языка через `i18n.url`. `robots_txt(domain)` разрешает всё и указывает на карту сайта. `restaurant_jsonld(site, lang)` собирает `Restaurant` с адресом, координатами, часами, телефоном, `priceRange: "₸₸"`, `servesCuisine: ["Pizza", "Italian", "Breakfast"]` и рейтингом.

- [ ] **Step 4: Запустить тест**

Run: `python3 -m unittest tests.test_seo -v`
Expected: PASS, 3 теста.

- [ ] **Step 5: Commit**

```bash
git add build/seo.py tests/test_seo.py && git commit -m "feat: sitemap, robots и микроразметка заведения"
```

---

## Task 17: Оркестратор сборки

**Files:**
- Create: `build.py`
- Create: `build/assets.py`

- [ ] **Step 1: Реализовать копирование статики**

`build/assets.py`: `copy_static(dist)` копирует `src/css`, `src/js`, `src/fonts`, `src/img`, `src/vendor` в `dist/`, сохраняя структуру. Использует `shutil.copytree` с `dirs_exist_ok=True`.

- [ ] **Step 2: Реализовать build.py**

```python
"""Сборка сайта: python3 build.py"""

import shutil
import sys
from pathlib import Path

from build.assets import copy_static
from build.components import footer, header
from build.data import DataError, load_menu, load_page, load_site
from build.i18n import LANGS, output_path
from build.layout import render_page
from build.pages import about, breakfast, contacts, dish, geo, home, menu as menu_page
from build.seo import robots_txt, sitemap_xml

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"


def write(path, content):
    target = DIST / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def main():
    try:
        site = load_site(ROOT / "data" / "site.json")
        menu = load_menu(ROOT / "data" / "menu.json")
    except DataError as err:
        print("Ошибка в данных: %s" % err)
        return 1

    if DIST.exists():
        shutil.rmtree(DIST)

    pages_built = 0
    paths = set()

    for lang in LANGS:
        chrome = (header(lang, site), footer(lang, site))
        simple = [("", home), ("menu", menu_page), ("breakfast", breakfast),
                  ("about", about), ("contacts", contacts)]
        for path, module in simple:
            texts = load_page(ROOT / "data" / "pages", path or "home", lang)
            page = module.build(site, menu, texts, lang)
            write(output_path(lang, page.path), render_page(page, site, *chrome))
            paths.add(page.path)
            pages_built += 1

        for item in menu.with_photos():
            page = dish.build(site, menu, item, lang)
            write(output_path(lang, page.path), render_page(page, site, *chrome))
            paths.add(page.path)
            pages_built += 1

        for page in geo.build_all(site, menu, lang):
            write(output_path(lang, page.path), render_page(page, site, *chrome))
            paths.add(page.path)
            pages_built += 1

    write("sitemap.xml", sitemap_xml(site.domain, sorted(paths)))
    write("robots.txt", robots_txt(site.domain))
    copy_static(DIST)

    print("Собрано страниц: %d" % pages_built)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Собрать сайт**

Run: `python3 build.py`
Expected: `Собрано страниц: 69`

- [ ] **Step 4: Проверить структуру результата**

Run: `find dist -name index.html | wc -l && ls dist`
Expected: `69`, в списке — `index.html`, `menu`, `kz`, `en`, `css`, `js`, `img`, `fonts`, `sitemap.xml`, `robots.txt`.

- [ ] **Step 5: Commit**

```bash
git add build.py build/assets.py && git commit -m "feat: сборка сайта одной командой"
```

---

## Task 18: Корзина и выгрузка в WhatsApp

**Files:**
- Create: `src/js/cart.js`

- [ ] **Step 1: Реализовать хранилище**

Ключ `frnds.cart.v1` в `localStorage`, срок жизни 7 дней, формат `{updated: <timestamp>, items: [{id, qty}]}`. Названия и цены берутся из `data-`атрибутов карточек на странице — так корзина не расходится с меню после пересборки.

- [ ] **Step 2: Реализовать интерфейс**

Клик по `.pill--price` добавляет позицию и на 1.2 с показывает «Добавлено». Нижний бар появляется, когда в заказе что-то есть, и показывает «N позиций · сумма». Клик открывает панель: список с `+`/`−`, удаление, итог, переключатель «В зал» / «Самовывоз».

- [ ] **Step 3: Реализовать формирование сообщения**

```js
function buildMessage(items, total, mode, lang) {
  const L = MESSAGES[lang];
  const lines = items.map(function (it) {
    const qty = it.qty > 1 ? ' × ' + it.qty : '';
    return '• ' + it.name + qty + ' — ' + formatPrice(it.price * it.qty) + ' ₸';
  });
  return [L.greeting, '', lines.join('\n'), '', L.total + ': ' + formatPrice(total) + ' ₸', L[mode]].join('\n');
}
```

Ссылка: `https://wa.me/77074809215?text=` + `encodeURIComponent(message)`. Если сообщение длиннее 1500 символов, позиции сокращаются до «название × количество» без цен — иначе ссылка не откроется на части телефонов.

- [ ] **Step 4: Проверить в браузере**

Запустить `python3 -m http.server -d dist 8000`, открыть меню, добавить три позиции, открыть панель, нажать «Отправить в WhatsApp». Проверить, что открывается `wa.me` с читаемым текстом заказа и верной суммой. Перезагрузить страницу — корзина должна сохраниться.

- [ ] **Step 5: Commit**

```bash
git add src/js/cart.js && git commit -m "feat: корзина с выгрузкой заказа в WhatsApp"
```

---

## Task 19: Навигация и карта

**Files:**
- Create: `src/js/nav.js`
- Create: `src/vendor/leaflet/*`

- [ ] **Step 1: Скопировать Leaflet из соседнего проекта**

```bash
cp -R "/Users/didar/Desktop/тут сайты /hostel 22/vendor/leaflet" src/vendor/leaflet
ls src/vendor/leaflet
```

- [ ] **Step 2: Реализовать nav.js**

Три независимых блока: бургер (переключает `hidden` и `aria-expanded`), скролл-шпион на `IntersectionObserver` для якорной навигации меню, инициализация карты по `#map` с координатами из `data-`атрибутов. Каждый блок проверяет наличие своего элемента и молча выходит, если его нет на странице.

- [ ] **Step 3: Проверить в браузере**

Открыть главную и страницу меню на десктопе и в мобильном размере: бургер открывается и закрывается, при скролле меню подсвечивается активный раздел, карта показывает метку по адресу.

- [ ] **Step 4: Commit**

```bash
git add src/js/nav.js src/vendor && git commit -m "feat: мобильная навигация, скролл-шпион и карта"
```

---

## Task 20: Финальная проверка

- [ ] **Step 1: Прогнать все тесты**

Run: `./run_tests.sh`
Expected: все тесты проходят, ни одного FAIL.

- [ ] **Step 2: Пересобрать и проверить целостность**

```bash
python3 build.py
grep -L "hreflang" $(find dist -name index.html) | head
```
Expected: `Собрано страниц: 69` и пустой вывод grep — hreflang есть везде.

- [ ] **Step 3: Проверить страницы в браузере**

Открыть на десктопе и в мобильном размере: главную, меню, страницу пиццы, завтраки, контакты, одну гео-страницу, по одной на каждом языке. Проверить: переключение языка ведёт на ту же страницу, а не на главную; казахские буквы отрисованы Manrope; карточки без фото выглядят намеренно, а не сломанно.

- [ ] **Step 4: Прогнать Lighthouse**

Проверить главную и меню на мобильном профиле.
Expected: Performance ≥ 90, Accessibility ≥ 95, Best Practices ≥ 95, SEO = 100.

- [ ] **Step 5: Написать владельцу инструкцию**

`docs/как-обновлять-сайт.md`: как поменять цену, добавить блюдо, заменить фото, вписать домен, куда положить фото зала. Простым языком, без терминов.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "docs: инструкция по обновлению сайта для владельца"
```

---

## Что останется владельцу

После сборки сайт полностью рабочий, но четыре вещи улучшат его без единой строки кода:

1. **Фото зала, бариста и гостей** — заменить плейсхолдеры в `src/img/interior/`. Это единственное, чего сайту по-настоящему не хватает для концепции «дом вне дома».
2. **Вычитка переводов** — список спорных мест в `docs/перевод-на-проверку.md`.
3. **Домен** — одна строка в `data/site.json`, затем пересборка.
4. **Ссылки на агрегаторы** — массив `aggregators` в `data/site.json`; пока он пуст, блок «Как забрать» показывает только зал и самовывоз.
