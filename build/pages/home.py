"""Главная страница."""

from html import escape

from build.components import dish_card, whatsapp_button
from build.i18n import t, url
from build.layout import Page
from build.seo import restaurant_jsonld

CITY = {"ru": "Астана", "kk": "Астана", "en": "Astana"}

# Полароиды команды и гостей — «made for our friends». Снимки уже в рамках,
# сайт только раскладывает их веером, как на фотостене в зале.
POLAROID_ALT = {
    "team-kitchen": {"ru": "Команда Frnds на кухне — селфи с поварами",
                     "kk": "Frnds командасы ас үйде — аспаздармен селфи",
                     "en": "The Frnds team in the kitchen — selfie with the chefs"},
    "chefs-heart": {"ru": "Повара Frnds складывают сердце над тарелкой",
                    "kk": "Frnds аспаздары тәрелке үстінде жүрек жасап тұр",
                    "en": "Frnds chefs making a heart over a plate"},
    "guests-table": {"ru": "Гости Frnds за большим общим столом",
                     "kk": "Frnds қонақтары үлкен ортақ үстел басында",
                     "en": "Frnds guests at the big communal table"},
    "photo-wall": {"ru": "Гости Frnds у фотостены в зале",
                   "kk": "Frnds қонақтары залдағы фотоқабырға жанында",
                   "en": "Frnds guests by the photo wall in the café"},
}


def polaroid(slug, lang, sizes="(max-width: 900px) 50vw, 260px", eager=False):
    base = "/img/team/%s" % slug
    return (
        "<picture>"
        '<source type="image/webp" srcset="%(b)s-360.webp 360w, %(b)s-600.webp 600w, %(b)s-900.webp 900w" '
        'sizes="%(sizes)s">'
        '<img src="%(b)s-600.jpg" alt="%(alt)s" width="600" height="955"%(load)s>'
        "</picture>"
        % {"b": base, "sizes": sizes, "alt": escape(POLAROID_ALT[slug][lang], quote=True),
           "load": ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'}
    )


def _stroke():
    return '<img class="stroke" src="/img/stroke.svg" alt="" width="150" height="10">'


def _hero(site, texts, lang):
    wa = "https://wa.me/%s" % site.whatsapp
    return (
        '<section class="hero"><div class="container hero__inner">'
        '<div class="hero__text">'
        # Логотип рукописный, поэтому это картинка — но заголовок страницы
        # должен быть настоящим h1, иначе у главной нет заголовка для поиска.
        '<h1 class="hero__h1"><img class="hero__logo" src="/img/logo/frnds-orange-640.png"'
        ' alt="%(logo_alt)s" width="320" height="149" fetchpriority="high"></h1>'
        '<p class="hero__kicker">%(kicker)s</p>'
        '<p class="hero__lead">%(lead)s</p>'
        '<div class="hero__actions">'
        '<a class="pill pill--brand" href="%(menu_url)s">%(cta_menu)s</a>'
        "%(wa_btn)s"
        "</div>"
        '<p class="hero__meta"><span class="dot"></span>%(address)s · %(today)s %(close)s</p>'
        "</div>"
        # Веер из трёх полароидов — команда и гости. Оранжевый круг из макета
        # меню остаётся позади: тот же мотив, что и раньше под пиццей.
        '<div class="hero__media hero__media--wall"><span class="hero__circle" aria-hidden="true"></span>'
        '<div class="fan">'
        '<figure class="fan__card fan__card--left">%(p_team)s</figure>'
        '<figure class="fan__card fan__card--center">%(p_chefs)s</figure>'
        '<figure class="fan__card fan__card--right">%(p_guests)s</figure>'
        "</div>"
        "</div></div></section>"
        % {"logo_alt": escape(texts["hero_logo_alt"], quote=True),
           "p_team": polaroid("team-kitchen", lang, eager=True),
           "p_chefs": polaroid("chefs-heart", lang, eager=True),
           "p_guests": polaroid("guests-table", lang, eager=True),
           "kicker": escape(texts["hero_kicker"]), "lead": escape(texts["hero_text"]),
           "menu_url": url(lang, "menu"), "cta_menu": escape(t("cta.menu", lang)),
           "wa_btn": whatsapp_button(site, lang, "ghost"),
           "address": escape(site.address[lang]), "today": escape(t("hours.today", lang)),
           "close": site.hours["close"]}
    )


def _hits(menu, texts, lang):
    cards = "".join(dish_card(item, lang) for item in menu.by_category("pizza")[:6])
    return (
        '<section class="section"><div class="container">'
        '<h2 class="display">%s</h2>%s<div class="grid">%s</div>'
        '<p class="section__more"><a href="%s">%s →</a></p>'
        "</div></section>"
        % (escape(texts["hits_title"]), _stroke(), cards,
           url(lang, "menu"), escape(t("menu.all", lang)))
    )


def _manifesto(texts, lang):
    """Письмо гостю — фирменный текст владельца, слово в слово."""
    paragraphs = "".join(
        "<p>%s</p>" % escape(p.strip())
        for p in texts["manifesto_text"].split("\n\n") if p.strip()
    )
    return (
        '<section class="section watermark"><div class="container manifesto">'
        '<h2 class="display">%s</h2>%s%s'
        '<p class="manifesto__sign">%s</p>'
        "</div></section>"
        % (escape(texts["manifesto_title"]), _stroke(), paragraphs,
           escape(texts["manifesto_sign"]))
    )


def _breakfast(texts, lang):
    return (
        '<section class="section section--tint"><div class="container split">'
        '<div><h2 class="display">%s</h2>%s<p>%s</p>'
        '<p><a class="pill pill--brand" href="%s">%s →</a></p></div>'
        '<img src="/img/pizza/pizza-salmon-broccoli-800.jpg" alt="%s"'
        ' width="800" height="800" loading="lazy">'
        "</div></section>"
        % (escape(texts["breakfast_title"]), _stroke(), escape(texts["breakfast_text"]),
           url(lang, "breakfast"), escape(t("nav.breakfast", lang)),
           escape("Завтраки Frnds, %s" % CITY[lang], quote=True))
    )


def _about(texts, lang):
    return (
        '<section class="section watermark"><div class="container split split--wall">'
        '<div class="fan fan--duo">'
        '<figure class="fan__card fan__card--left">%s</figure>'
        '<figure class="fan__card fan__card--right">%s</figure>'
        "</div>"
        '<div><h2 class="display">%s</h2>%s<p>%s</p>'
        '<p><a href="%s">%s →</a></p></div>'
        "</div></section>"
        % (polaroid("photo-wall", lang), polaroid("guests-table", lang),
           escape(texts["about_title"]), _stroke(),
           escape(texts["about_text"]), url(lang, "about"), escape(t("nav.about", lang)))
    )


def _reviews(site, texts, lang):
    quotes = "".join(
        '<figure class="quote"><blockquote>%s</blockquote>'
        "<footer>%s</footer></figure>"
        % (escape(r["text"]), escape(r["author"]))
        for r in texts["reviews"]
    )
    return (
        '<section class="section section--tint"><div class="container">'
        '<h2 class="display">%s</h2>%s'
        '<p class="rating-line"><strong>%s</strong>'
        '<span>%s %s</span></p>'
        '<div class="quote-grid">%s</div>'
        '<p class="section__more"><a href="%s" rel="noopener" target="_blank">2GIS →</a></p>'
        "</div></section>"
        % (escape(texts["reviews_title"]), _stroke(), site.rating["value"],
           site.rating["count"], escape(t("rating.reviews", lang)), quotes,
           escape(site.twogis, quote=True))
    )


def _howto(site, texts, lang):
    cells = "".join(
        '<article class="tile"><h3>%s</h3><p>%s</p></article>'
        % (escape(x["title"]), escape(x["text"])) for x in texts["howto"]
    )
    return (
        '<section class="section"><div class="container">'
        '<h2 class="display">%s</h2>%s<div class="tiles">%s</div>'
        "</div></section>" % (escape(texts["howto_title"]), _stroke(), cells)
    )


def _map(site, texts, lang):
    return (
        '<section class="section section--tint"><div class="container">'
        '<h2 class="display">%s</h2>%s'
        '<div id="map" data-lat="%s" data-lon="%s" data-label="%s"></div>'
        '<p class="section__more">%s · <a href="%s" rel="noopener" target="_blank">2GIS →</a></p>'
        "</div></section>"
        % (escape(texts["map_title"]), _stroke(), site.coords["lat"], site.coords["lon"],
           escape("Frnds — %s" % site.address[lang], quote=True),
           escape(site.address[lang]), escape(site.twogis, quote=True))
    )


def build(site, menu, texts, lang):
    body = "".join([
        '<main id="main">',
        _hero(site, texts, lang),
        _hits(menu, texts, lang),
        _manifesto(texts, lang),
        _breakfast(texts, lang),
        _about(texts, lang),
        _reviews(site, texts, lang),
        _howto(site, texts, lang),
        _map(site, texts, lang),
        "</main>",
    ])
    return Page(
        lang=lang, path="", title=texts["seo_title"], description=texts["seo_description"],
        body=body, og_image=site.domain + "/img/og-default.jpg",
        json_ld=[restaurant_jsonld(site, lang)], body_class="page-home", needs_map=True,
    )
