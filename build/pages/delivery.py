"""Страница «Доставка»: своя доставка в термосумках и переход в меню."""

from html import escape

from build.components import dish_card, whatsapp_button
from build.i18n import t, url
from build.layout import Page
from build.seo import breadcrumbs_jsonld, restaurant_jsonld


CITY = {"ru": "Астана", "kk": "Астана", "en": "Astana"}

PHOTO_ALT = {
    "courier": {"ru": "Курьер Frnds с фирменной термосумкой у входа в кафе",
                "kk": "Кафе кіреберісіндегі фирмалық термосөмкелі Frnds курьері",
                "en": "Frnds courier with a branded thermal bag at the café entrance"},
    "bag": {"ru": "Оранжевая термосумка Frnds в зале кафе",
            "kk": "Кафе залындағы Frnds қызғылт сары термосөмкесі",
            "en": "Orange Frnds thermal bag inside the café"},
}


def _photo(slug, lang, sizes, eager=False):
    base = "/img/delivery/%s" % slug
    return (
        "<picture>"
        '<source type="image/webp" srcset="%(b)s-480.webp 480w, %(b)s-800.webp 800w, %(b)s-1100.webp 1100w" '
        'sizes="%(sizes)s">'
        '<img src="%(b)s-800.jpg" alt="%(alt)s" width="800" height="1000"%(load)s>'
        "</picture>"
        % {"b": base, "sizes": sizes, "alt": escape(PHOTO_ALT[slug][lang], quote=True),
           "load": ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'}
    )


def build(site, menu, texts, lang):
    steps = "".join(
        '<article class="tile"><h3>%s</h3><p>%s</p></article>'
        % (escape(s["title"]), escape(s["text"])) for s in texts["steps"]
    )
    cards = "".join(dish_card(i, lang) for i in menu.by_category("pizza")[:6])

    body = (
        '<main id="main">'
        '<section class="hero hero--delivery"><div class="container hero__inner">'
        '<div class="hero__text">'
        "<h1>%(h1)s</h1>"
        '<p class="hero__lead">%(intro)s</p>'
        '<img class="stroke" src="/img/stroke.svg" alt="" width="150" height="10">'
        '<div class="hero__actions">%(wa_btn)s'
        '<a class="pill pill--ghost" href="%(menu_url)s">%(menu_cta)s</a></div>'
        "</div>"
        # Настоящие фото заведения: курьер у входа и сумка в зале.
        # Два кадра внахлёст — как пачка снимков на столе.
        '<div class="photo-stack">'
        '<figure class="photo-stack__back">%(photo_bag)s</figure>'
        '<figure class="photo-stack__front">%(photo_courier)s</figure>'
        "</div>"
        "</div></section>"
        '<section class="section watermark"><div class="container">'
        '<div class="tiles">%(steps)s</div></div></section>'
        '<section class="section section--tint"><div class="container">'
        '<h2 class="display">%(pick_title)s</h2>'
        '<img class="stroke" src="/img/stroke.svg" alt="" width="150" height="10">'
        '<div class="grid">%(cards)s</div>'
        '<p class="section__more"><a class="pill pill--brand" href="%(menu_url)s">%(all_menu)s</a></p>'
        "</div></section></main>"
        % {"h1": escape(texts["h1"]), "intro": escape(texts["intro"]),
           "wa_btn": whatsapp_button(site, lang, "brand"),
           "menu_url": url(lang, "menu"), "menu_cta": escape(t("cta.menu", lang)),
           "photo_courier": _photo("courier", lang, "(max-width: 900px) 70vw, 360px", eager=True),
           "photo_bag": _photo("bag", lang, "(max-width: 900px) 55vw, 300px"),
           "steps": steps, "pick_title": escape(texts["pick_title"]),
           "cards": cards, "all_menu": escape(t("menu.all", lang))}
    )

    return Page(
        lang=lang, path="delivery", title=texts["seo_title"],
        description=texts["seo_description"], body=body,
        json_ld=[
            restaurant_jsonld(site, lang),
            breadcrumbs_jsonld([
                (t("breadcrumb.home", lang), site.domain + url(lang, "")),
                (texts["h1"], site.domain + url(lang, "delivery")),
            ]),
        ],
        body_class="page-delivery",
    )
