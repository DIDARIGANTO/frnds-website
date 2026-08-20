"""Страница «Доставка»: своя доставка в термосумках и переход в меню."""

from html import escape

from build.components import dish_card, whatsapp_button
from build.i18n import t, url
from build.layout import Page
from build.seo import breadcrumbs_jsonld, restaurant_jsonld


def build(site, menu, texts, lang):
    steps = "".join(
        '<article class="tile"><h3>%s</h3><p>%s</p></article>'
        % (escape(s["title"]), escape(s["text"])) for s in texts["steps"]
    )
    cards = "".join(dish_card(i, lang) for i in menu.by_category("pizza")[:6])

    body = (
        '<main id="main"><div class="container">'
        "<h1>%(h1)s</h1>"
        '<p class="hero__lead">%(intro)s</p>'
        '<img class="stroke" src="/img/stroke.svg" alt="" width="150" height="10">'
        '<div class="hero__actions">%(wa_btn)s'
        '<a class="pill pill--ghost" href="%(menu_url)s">%(menu_cta)s</a></div>'
        "</div>"
        # ФОТО ТЕРМОСУМКИ: когда владелец пришлёт снимок файлом, положить его
        # в src/img/delivery/ и заменить плитки на split-раскладку с фото.
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
