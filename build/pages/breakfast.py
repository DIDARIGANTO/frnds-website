"""Страница завтраков — главное отличие заведения от обычной пиццерии."""

from html import escape

from build.components import dense_row, whatsapp_button
from build.i18n import t, url
from build.layout import Page
from build.seo import breadcrumbs_jsonld


def _paragraphs(text):
    return "".join("<p>%s</p>" % escape(p.strip())
                   for p in text.split("\n\n") if p.strip())


def build(site, menu, texts, lang):
    items = menu.by_category("breakfast")
    rows = "".join(dense_row(i, lang) for i in items)
    wa = "https://wa.me/%s" % site.whatsapp

    body = (
        '<main id="main"><div class="container">'
        "<h1>%(h1)s</h1>"
        '<p class="hero__lead">%(intro)s</p>'
        '<img class="stroke" src="/img/stroke.svg" alt="" width="150" height="10">'
        "</div>"
        '<section class="section"><div class="container">%(body)s</div></section>'
        '<section class="section section--tint"><div class="container">'
        '<h2 class="display">%(menu_title)s</h2>'
        '<ul class="rows">%(rows)s</ul>'
        '<p class="section__more">%(cta)s</p>'
        "<p>%(wa_btn)s "
        '<a class="pill pill--ghost" href="%(menu_url)s">%(all_menu)s</a></p>'
        "</div></section></main>"
        % {"h1": escape(texts["h1"]), "intro": escape(texts["intro"]),
           "body": _paragraphs(texts["body"]),
           "menu_title": escape(t("nav.breakfast", lang)), "rows": rows,
           "cta": escape(texts["cta_text"]),
           "wa_btn": whatsapp_button(site, lang, "brand"),
           "menu_url": url(lang, "menu"), "all_menu": escape(t("menu.all", lang))}
    )

    return Page(
        lang=lang, path="breakfast", title=texts["seo_title"],
        description=texts["seo_description"], body=body,
        json_ld=[breadcrumbs_jsonld([
            (t("breadcrumb.home", lang), site.domain + url(lang, "")),
            (texts["h1"], site.domain + url(lang, "breakfast")),
        ])],
        body_class="page-breakfast",
    )
