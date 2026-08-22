"""Страница «Наш дом» — концепция заведения."""

from html import escape

from build.i18n import t, url
from build.pages.home import polaroid
from build.layout import Page
from build.seo import breadcrumbs_jsonld, restaurant_jsonld


def _paragraphs(text):
    return "".join("<p>%s</p>" % escape(p.strip())
                   for p in text.split("\n\n") if p.strip())


def build(site, menu, texts, lang):
    values = "".join(
        '<article class="tile"><h3>%s</h3><p>%s</p></article>'
        % (escape(v["title"]), escape(v["text"])) for v in texts["values"]
    )
    body = (
        '<main id="main"><div class="container">'
        "<h1>%(h1)s</h1>"
        '<p class="hero__lead">%(intro)s</p>'
        '<img class="stroke" src="/img/stroke.svg" alt="" width="150" height="10">'
        "</div>"
        '<section class="section watermark"><div class="container split split--wall">'
        "<div>%(body)s</div>"
        # Полароиды с фотостены: гости у стены и команда на кухне
        '<div class="fan fan--duo">'
        '<figure class="fan__card fan__card--left">%(p_wall)s</figure>'
        '<figure class="fan__card fan__card--right">%(p_team)s</figure>'
        "</div>"
        "</div></section>"
        '<section class="section section--tint"><div class="container">'
        '<div class="tiles">%(values)s</div>'
        '<p class="section__more"><a class="pill pill--brand" href="%(menu_url)s">%(cta)s</a></p>'
        "</div></section></main>"
        % {"h1": escape(texts["h1"]), "intro": escape(texts["intro"]),
           "body": _paragraphs(texts["body"]), "values": values,
           "p_wall": polaroid("photo-wall", lang),
           "p_team": polaroid("team-kitchen", lang),
           "menu_url": url(lang, "menu"), "cta": escape(t("cta.menu", lang))}
    )
    return Page(
        lang=lang, path="about", title=texts["seo_title"],
        description=texts["seo_description"], body=body,
        json_ld=[
            restaurant_jsonld(site, lang),
            breadcrumbs_jsonld([
                (t("breadcrumb.home", lang), site.domain + url(lang, "")),
                (texts["h1"], site.domain + url(lang, "about")),
            ]),
        ],
        body_class="page-about",
    )
