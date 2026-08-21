"""Гео-страницы по районам Астаны.

У заведения своя доставка (курьеры Frnds, термосумки), поэтому страницы
отвечают и на «пиццерия рядом», и на «доставка пиццы в мой район».
Тексты районов уникальные — лежат в data/pages/geo-*.json.
"""

import json
from html import escape
from pathlib import Path

from build.components import dish_card, whatsapp_button
from build.i18n import t, url
from build.layout import Page
from build.seo import breadcrumbs_jsonld, restaurant_jsonld

GEO_SLUGS = ("esil", "levyi-bereg", "saryarka", "almaty-rayon", "baikonyr")

AREA_SERVED = {
    "esil": {"ru": "Есильский район", "kk": "Есіл ауданы", "en": "Esil District"},
    "levyi-bereg": {"ru": "Левый берег Астаны", "kk": "Астананың сол жағалауы", "en": "Left Bank, Astana"},
    "saryarka": {"ru": "Район Сарыарка", "kk": "Сарыарқа ауданы", "en": "Saryarka District"},
    "almaty-rayon": {"ru": "Алматинский район", "kk": "Алматы ауданы", "en": "Almaty District"},
    "baikonyr": {"ru": "Район Байконур", "kk": "Байқоңыр ауданы", "en": "Baikonyr District"},
}


def _paragraphs(text):
    return "".join("<p>%s</p>" % escape(p.strip())
                   for p in text.split("\n\n") if p.strip())


def _restaurant_with_area(site, lang, slug):
    payload = json.loads(restaurant_jsonld(site, lang))
    payload["areaServed"] = {"@type": "AdministrativeArea", "name": AREA_SERVED[slug][lang]}
    return json.dumps(payload, ensure_ascii=False, separators=(", ", ": ")).replace("</", "<\\/")


def _build_one(site, menu, texts, slug, lang):
    cards = "".join(dish_card(i, lang) for i in menu.by_category("pizza")[:6])
    wa = "https://wa.me/%s" % site.whatsapp

    body = (
        '<main id="main"><div class="container">'
        "<h1>%(h1)s</h1>"
        '<img class="stroke" src="/img/stroke.svg" alt="" width="150" height="10">'
        "</div>"
        '<section class="section"><div class="container split">'
        "<div>%(body)s</div>"
        '<div><div id="map" data-lat="%(lat)s" data-lon="%(lon)s" data-label="%(label)s"></div>'
        '<p class="section__more">%(landmarks)s</p></div>'
        "</div></section>"
        '<section class="section section--tint"><div class="container">'
        '<h2 class="display">%(hits)s</h2><div class="grid">%(cards)s</div>'
        '<p class="section__more">%(cta)s</p>'
        "<p>%(wa_btn)s "
        '<a class="pill pill--ghost" href="%(menu_url)s">%(all_menu)s</a></p>'
        "</div></section></main>"
        % {"h1": escape(texts["h1"]), "body": _paragraphs(texts["body"]),
           "lat": site.coords["lat"], "lon": site.coords["lon"],
           "label": escape("Frnds — %s" % site.address[lang], quote=True),
           "landmarks": escape(texts["landmarks"]),
           "hits": escape({"ru": "Что берут чаще всего", "kk": "Жиі тапсырыс беретіндер",
                           "en": "What people order most"}[lang]),
           "cards": cards, "cta": escape(texts["cta"]),
           "wa_btn": whatsapp_button(site, lang, "brand"),
           "menu_url": url(lang, "menu"), "all_menu": escape(t("menu.all", lang))}
    )

    return Page(
        lang=lang, path=slug, title=texts["seo_title"],
        description=texts["seo_description"], body=body,
        json_ld=[
            _restaurant_with_area(site, lang, slug),
            breadcrumbs_jsonld([
                (t("breadcrumb.home", lang), site.domain + url(lang, "")),
                (texts["h1"], site.domain + url(lang, slug)),
            ]),
        ],
        body_class="page-geo", needs_map=True,
    )


def build_all(site, menu, lang, pages_dir="data/pages"):
    from build.data import load_page
    pages = []
    for slug in GEO_SLUGS:
        texts = load_page(Path(pages_dir), "geo-%s" % slug, lang)
        pages.append(_build_one(site, menu, texts, slug, lang))
    return pages
