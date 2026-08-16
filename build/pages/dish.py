"""Страница одного блюда. Собирается для позиций с фотографией — 13 пицц."""

from html import escape

from build.components import dish_card, money, price_pill
from build.i18n import t, url
from build.layout import Page
from build.seo import breadcrumbs_jsonld, menuitem_jsonld

CITY = {"ru": "Астана", "kk": "Астана", "en": "Astana"}


def _picture(slug, alt):
    base = "/img/pizza/%s" % slug
    return (
        "<picture>"
        '<source type="image/webp" srcset="%(b)s-400.webp 400w, %(b)s-800.webp 800w, %(b)s-1200.webp 1200w" '
        'sizes="(max-width: 900px) 92vw, 520px">'
        '<img src="%(b)s-800.jpg" alt="%(alt)s" width="800" height="800" fetchpriority="high">'
        "</picture>" % {"b": base, "alt": escape(alt, quote=True)}
    )


def _similar(menu, item, lang):
    """Три другие пиццы. Берём по порядку, без random — сборка воспроизводима."""
    pizzas = [i for i in menu.by_category(item.category) if i.id != item.id]
    start = ([i.id for i in menu.by_category(item.category)].index(item.id) + 1) % max(1, len(pizzas))
    picked = (pizzas + pizzas)[start:start + 3]
    if not picked:
        return ""
    return (
        '<section class="section"><div class="container">'
        '<h2 class="display">%s</h2><div class="grid">%s</div>'
        "</div></section>"
        % (escape(t("dish.similar", lang)), "".join(dish_card(i, lang) for i in picked))
    )


def build(site, menu, item, lang):
    name = item.name[lang]
    alt = "%s — Frnds, %s" % (name, CITY[lang])
    home_url = site.domain + url(lang, "")
    menu_url = site.domain + url(lang, "menu")
    self_url = site.domain + url(lang, "menu/%s" % item.id)

    body = (
        '<main id="main"><div class="container">'
        '<nav class="breadcrumbs" aria-label="breadcrumbs">'
        '<a href="%(menu_href)s">%(menu_name)s</a> · <span aria-current="page">%(name)s</span>'
        "</nav>"
        '<div class="dish">'
        '<div class="dish__media">%(picture)s</div>'
        "<div><h1>%(name)s</h1>"
        '<p class="hero__lead">%(desc)s</p>'
        '<p class="dish__price">%(price)s</p>'
        '<div class="hero__actions">%(pill)s'
        '<a class="pill pill--ghost" href="%(wa)s" rel="noopener" target="_blank">%(cta_wa)s</a></div>'
        '<p class="section__more"><a href="%(menu_href)s">← %(back)s</a></p>'
        "</div></div></div>%(similar)s</main>"
        % {"menu_href": url(lang, "menu"), "menu_name": escape(t("nav.menu", lang)),
           "name": escape(name), "picture": _picture(item.photo, alt),
           "desc": escape(item.desc[lang]), "price": escape(money(item.price)),
           "pill": price_pill(item.price, lang, item.id),
           "wa": "https://wa.me/%s" % site.whatsapp,
           "cta_wa": escape(t("cta.whatsapp", lang)),
           "back": escape(t("dish.back", lang)),
           "similar": _similar(menu, item, lang)}
    )

    # Названия пицц на русском и казахском часто совпадают буква в букву
    # («Маргарита»), поэтому шаблон заголовка у языков разный — иначе
    # версии неразличимы в поисковой выдаче.
    title = {
        "ru": "%s — пицца, Frnds Астана" % name,
        "kk": "%s — Frnds пиццасы, Астана" % name,
        "en": "%s pizza — Frnds, Astana" % name,
    }[lang]
    description = "%s %s — %s. %s" % (
        name, money(item.price), item.desc[lang],
        {"ru": "Заказ в WhatsApp, самовывоз и зал в Астане.",
         "kk": "WhatsApp арқылы тапсырыс, өзің алу және зал — Астанада.",
         "en": "Order on WhatsApp, pickup and dine-in in Astana."}[lang])

    return Page(
        lang=lang, path="menu/%s" % item.id, title=title, description=description[:300],
        body=body, og_image="%s/img/pizza/%s-1200.jpg" % (site.domain, item.photo),
        json_ld=[
            menuitem_jsonld(site, item, lang),
            breadcrumbs_jsonld([
                (t("breadcrumb.home", lang), home_url),
                (t("nav.menu", lang), menu_url),
                (name, self_url),
            ]),
        ],
        body_class="page-dish",
    )
