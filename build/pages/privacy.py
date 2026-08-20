"""Политика конфиденциальности — обработка персональных данных по закону РК."""

from html import escape

from build.i18n import t, url
from build.layout import Page
from build.seo import breadcrumbs_jsonld


def build(site, menu, texts, lang):
    sections = "".join(
        "<section><h2>%s</h2>%s</section>"
        % (escape(s["title"]),
           "".join("<p>%s</p>" % escape(p.strip())
                   for p in s["text"].split("\n\n") if p.strip()))
        for s in texts["sections"]
    )
    body = (
        '<main id="main"><div class="container legal">'
        "<h1>%(h1)s</h1>"
        '<p class="hero__lead">%(intro)s</p>'
        '<img class="stroke" src="/img/stroke.svg" alt="" width="150" height="10">'
        "%(sections)s"
        '<p class="legal__updated">%(updated)s</p>'
        "</div></main>"
        % {"h1": escape(texts["h1"]), "intro": escape(texts["intro"]),
           "sections": sections, "updated": escape(texts["updated"])}
    )
    return Page(
        lang=lang, path="privacy", title=texts["seo_title"],
        description=texts["seo_description"], body=body,
        json_ld=[breadcrumbs_jsonld([
            (t("breadcrumb.home", lang), site.domain + url(lang, "")),
            (texts["h1"], site.domain + url(lang, "privacy")),
        ])],
        body_class="page-privacy",
    )
