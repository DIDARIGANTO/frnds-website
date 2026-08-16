"""Страница полного меню: якорная навигация и 21 раздел."""

from html import escape

from build.components import dense_row, dish_card
from build.i18n import t
from build.layout import Page
from build.seo import breadcrumbs_jsonld, menu_jsonld
from build.i18n import url


def _chips(menu, lang):
    links = "".join(
        '<a class="chip" href="#%s">%s</a>' % (cat.id, escape(cat.name[lang]))
        for cat in menu.categories if menu.by_category(cat.id)
    )
    return ('<nav class="chips" aria-label="%s"><div class="chips__inner">%s</div></nav>'
            % (escape(t("menu.all", lang)), links))


def _section(cat, items, lang):
    has_photos = any(i.photo for i in items)
    if has_photos:
        content = '<div class="grid">%s</div>' % "".join(dish_card(i, lang) for i in items)
    else:
        # Разделы без фотографий рендерим плотным списком: сетка пустых карточек
        # читается как несработавшая загрузка изображений.
        content = '<ul class="rows">%s</ul>' % "".join(dense_row(i, lang) for i in items)
    return (
        '<section class="menu-section" id="%s">'
        '<h2 class="display">%s<img class="stroke" src="/img/stroke.svg" alt="" width="90" height="10"></h2>'
        "%s</section>" % (cat.id, escape(cat.name[lang]), content)
    )


def build(site, menu, texts, lang):
    sections = "".join(
        _section(cat, menu.by_category(cat.id), lang)
        for cat in menu.categories if menu.by_category(cat.id)
    )
    body = (
        '<main id="main"><div class="container">'
        "<h1>%s</h1><p class=\"hero__lead\">%s</p>"
        "</div>%s"
        '<div class="container">%s</div></main>'
        % (escape(texts["h1"]), escape(texts["intro"]), _chips(menu, lang), sections)
    )
    return Page(
        lang=lang, path="menu", title=texts["seo_title"],
        description=texts["seo_description"], body=body,
        json_ld=[
            menu_jsonld(site, menu, lang),
            breadcrumbs_jsonld([
                (t("breadcrumb.home", lang), site.domain + url(lang, "")),
                (texts["h1"], site.domain + url(lang, "menu")),
            ]),
        ],
        body_class="page-menu",
    )
