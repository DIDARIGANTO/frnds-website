"""Сборка сайта Frnds.

    python3 build.py

Читает данные из data/, собирает страницы на трёх языках в dist/.
Любая опечатка в данных останавливает сборку с понятным сообщением.
"""

import shutil
import sys
from pathlib import Path

from build.assets import copy_static
from build.components import footer, header
from build.data import DataError, load_menu, load_page, load_site
from build.i18n import LANGS, output_path
from build.layout import render_page
from build.pages import about, breakfast, contacts, delivery, dish, geo, home
from build.pages import menu as menu_page
from build.seo import robots_txt, sitemap_xml

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"

SIMPLE_PAGES = [
    ("", "home", home),
    ("menu", "menu", menu_page),
    ("delivery", "delivery", delivery),
    ("breakfast", "breakfast", breakfast),
    ("about", "about", about),
    ("contacts", "contacts", contacts),
]


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

    pages_dir = ROOT / "data" / "pages"
    built = 0
    paths = set()

    try:
        for lang in LANGS:
            chrome = (header(lang, site), footer(lang, site))

            for path, texts_name, module in SIMPLE_PAGES:
                texts = load_page(pages_dir, texts_name, lang)
                page = module.build(site, menu, texts, lang)
                write(output_path(lang, page.path), render_page(page, site, *chrome))
                paths.add(page.path)
                built += 1

            for item in menu.with_photos():
                page = dish.build(site, menu, item, lang)
                write(output_path(lang, page.path), render_page(page, site, *chrome))
                paths.add(page.path)
                built += 1

            for page in geo.build_all(site, menu, lang, pages_dir=pages_dir):
                write(output_path(lang, page.path), render_page(page, site, *chrome))
                paths.add(page.path)
                built += 1
    except DataError as err:
        print("Ошибка в текстах страниц: %s" % err)
        return 1
    except KeyError as err:
        print("В тексте страницы не хватает ключа %s" % err)
        return 1

    write("sitemap.xml", sitemap_xml(site.domain, sorted(paths)))
    write("robots.txt", robots_txt(site.domain))
    copy_static(DIST)

    print("Собрано страниц: %d" % built)
    return 0


if __name__ == "__main__":
    sys.exit(main())
