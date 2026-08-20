"""Каркас HTML-страницы: head, мета-теги, hreflang, подключение ассетов."""

from html import escape

from build.i18n import HTML_LANG, alternate_urls, t, url


class Page:
    """Всё, что нужно знать каркасу о конкретной странице."""

    __slots__ = ("lang", "path", "title", "description", "body",
                 "og_image", "json_ld", "body_class", "needs_map")

    def __init__(self, lang, path, title, description, body,
                 og_image="", json_ld=None, body_class="", needs_map=False):
        self.lang = lang
        self.path = path
        self.title = title
        self.description = description
        self.body = body
        self.og_image = og_image
        self.json_ld = json_ld or []
        self.body_class = body_class
        self.needs_map = needs_map


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
    # Leaflet тянем только туда, где есть карта: на страницах меню и блюд
    # это лишние 150 КБ без единого пикселя пользы.
    if page.needs_map:
        head += ['  <link rel="stylesheet" href="/vendor/leaflet/leaflet.css">',
                 '  <script src="/vendor/leaflet/leaflet.js" defer></script>']
    for block in page.json_ld:
        head.append('  <script type="application/ld+json">%s</script>' % block)
    head += ['  <script src="/js/nav.js" defer></script>',
             '  <script src="/js/cart.js" defer></script>',
             "</head>"]

    # Уведомление об обработке персональных данных (закон РК № 94-V).
    # Скрыто по умолчанию; nav.js показывает его, пока гость не закрыл крестиком.
    # Шаблон с плейсхолдерами: порядок слов в казахском другой, поэтому ссылки
    # подставляются в переведённое предложение, а не приклеиваются к концу.
    sentence = escape(t("consent.template", page.lang))
    sentence = sentence.replace("{privacy}", '<a href="%s">%s</a>' % (
        url(page.lang, "privacy"), escape(t("consent.privacy", page.lang))))
    sentence = sentence.replace("{offer}", '<a href="%s">%s</a>' % (
        url(page.lang, "offer"), escape(t("consent.offer", page.lang))))
    consent = (
        '<div class="consent" id="consent" role="region" aria-label="%(label)s" hidden>'
        "<p>%(sentence)s</p>"
        '<button class="consent__close" type="button" id="consent-ok" aria-label="%(close)s">×</button>'
        "</div>"
        % {"label": escape(t("nav.privacy", page.lang)),
           "sentence": sentence,
           "close": escape(t("consent.close", page.lang))}
    )

    body_class = ' class="%s"' % page.body_class if page.body_class else ""
    body = [
        '<body%s data-lang="%s">' % (body_class, page.lang),
        '<a class="skip-link" href="#main">%s</a>' % escape(t("skip.content", page.lang)),
        header,
        page.body,
        footer,
        consent,
        "</body>",
        "</html>",
    ]
    return "\n".join(head + [b for b in body if b])
