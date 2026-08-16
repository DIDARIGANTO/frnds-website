"""Переиспользуемые куски разметки.

Компоненты — чистые функции: получают данные, возвращают строку,
ничего не читают с диска. escape вызывается на каждом тексте из данных.
"""

from html import escape

from build.i18n import LANGS, t, url

TAG_EMOJI = {"spicy": "🌶", "veg": "🌿", "kids": "👶"}
BADGE_TEXT = {
    "hit": {"ru": "хит", "kk": "хит", "en": "popular"},
    "new": {"ru": "новинка", "kk": "жаңа", "en": "new"},
}


def money(value):
    """3590 -> '3 590 ₸' — узкий неразрывный пробел, цена не разрывается."""
    digits = "{:,}".format(int(value)).replace(",", " ")
    return "%s ₸" % digits


def price_pill(price, lang, item_id=""):
    attrs = ' data-add="%s"' % escape(item_id, quote=True) if item_id else ""
    return (
        '<button class="pill pill--price" type="button"%s>'
        '<span class="pill__price">%s</span>'
        '<span class="pill__action">%s</span>'
        "</button>" % (attrs, money(price), escape(t("cta.add", lang)))
    )


def _picture(slug, alt):
    base = "/img/pizza/%s" % slug
    return (
        "<picture>"
        '<source type="image/webp" srcset="%(b)s-400.webp 400w, %(b)s-800.webp 800w, %(b)s-1200.webp 1200w" '
        'sizes="(max-width: 700px) 45vw, 280px">'
        '<img src="%(b)s-400.jpg" alt="%(alt)s" width="400" height="400" loading="lazy" decoding="async">'
        "</picture>" % {"b": base, "alt": escape(alt, quote=True)}
    )


def dish_card(item, lang):
    name = item.name[lang]
    emoji = "".join(TAG_EMOJI.get(tag, "") for tag in item.tags)
    badges = "".join(
        '<span class="badge">%s</span>' % escape(BADGE_TEXT[b][lang])
        for b in item.badges if b in BADGE_TEXT
    )
    media = ""
    href = ""
    if item.photo:
        alt = "%s — Frnds, %s" % (name, {"ru": "Астана", "kk": "Астана", "en": "Astana"}[lang])
        href = url(lang, "menu/%s" % item.id)
        media = ('<a class="card__media" href="%s" tabindex="-1">%s%s</a>'
                 % (href, _picture(item.photo, alt), badges))

    title = escape(name) + (' <span class="card__tags">%s</span>' % emoji if emoji else "")
    heading = (
        '<h3 class="card__title"><a href="%s">%s</a></h3>' % (href, title)
        if href else '<h3 class="card__title">%s</h3>' % title
    )

    return (
        '<article class="card" data-item-id="%s" data-item-price="%d" data-item-name="%s">'
        "%s"
        '<div class="card__body">%s'
        '<p class="card__desc">%s</p>'
        '<div class="card__foot">%s</div>'
        "</div></article>"
        % (escape(item.id, quote=True), item.price, escape(name, quote=True),
           media, heading, escape(item.desc[lang]), price_pill(item.price, lang, item.id))
    )


def dense_row(item, lang):
    """Плотная строка для разделов без фото: название · состав · цена."""
    name = item.name[lang]
    emoji = "".join(TAG_EMOJI.get(tag, "") for tag in item.tags)
    title = escape(name) + (' <span class="card__tags">%s</span>' % emoji if emoji else "")
    return (
        '<li class="row" data-item-id="%s" data-item-price="%d" data-item-name="%s">'
        '<div class="row__text"><h3 class="row__title">%s</h3>'
        '<p class="row__desc">%s</p></div>'
        '<div class="row__price">%s</div></li>'
        % (escape(item.id, quote=True), item.price, escape(name, quote=True),
           title, escape(item.desc[lang]), price_pill(item.price, lang, item.id))
    )


def _logo(lang):
    return (
        '<a class="logo" href="%s" aria-label="Frnds">'
        '<img src="/img/logo/frnds-orange-320.png" alt="Frnds" width="120" height="56">'
        "</a>" % url(lang, "")
    )


def _lang_switch(lang, path=""):
    labels = {"ru": "RU", "kk": "KZ", "en": "EN"}
    links = "".join(
        '<a href="%s"%s>%s</a>' % (url(code, path),
                                   ' aria-current="true"' if code == lang else "",
                                   labels[code])
        for code in LANGS
    )
    return '<nav class="lang" aria-label="%s">%s</nav>' % (escape(t("lang.switch", lang)), links)


def nav_links(lang):
    items = [("nav.menu", "menu"), ("nav.breakfast", "breakfast"),
             ("nav.about", "about"), ("nav.contacts", "contacts")]
    return "".join(
        '<a href="%s">%s</a>' % (url(lang, target), escape(t(key, lang)))
        for key, target in items
    )


def header(lang, site, path=""):
    wa = "https://wa.me/%s" % site.whatsapp
    return (
        '<header class="header">'
        '<div class="container header__inner">'
        "%(logo)s"
        '<nav class="nav" aria-label="%(navlabel)s">%(links)s</nav>'
        '<div class="header__meta">'
        '<span class="dot" aria-hidden="true"></span>'
        "<span>%(hours)s %(close)s</span>"
        '<span class="header__rating">%(rating)s★</span>'
        "</div>"
        "%(lang)s"
        '<a class="pill pill--brand header__cta" href="%(wa)s" rel="noopener" target="_blank">%(cta)s</a>'
        '<button class="burger" type="button" aria-expanded="false" aria-controls="mobile-nav" '
        'aria-label="%(navlabel)s"><span></span><span></span><span></span></button>'
        "</div>"
        '<div class="mobile-nav" id="mobile-nav" hidden>%(links)s%(lang)s'
        '<a class="pill pill--brand" href="%(wa)s" rel="noopener" target="_blank">%(cta)s</a></div>'
        "</header>"
        % {"logo": _logo(lang), "links": nav_links(lang), "lang": _lang_switch(lang, path),
           "wa": wa, "cta": escape(t("cta.whatsapp", lang)),
           "navlabel": escape(t("nav.menu", lang)),
           "hours": escape(t("hours.today", lang)), "close": site.hours["close"],
           "rating": site.rating["value"]}
    )


def footer(lang, site):
    return (
        '<footer class="footer">'
        '<div class="container footer__inner">'
        '<div class="footer__col footer__col--logo">'
        '<img src="/img/logo/frnds-white-320.png" alt="Frnds" width="140" height="65" loading="lazy">'
        "<p>%(address)s</p>"
        "<p>%(open)s — %(close)s</p>"
        "</div>"
        '<div class="footer__col"><nav aria-label="%(navlabel)s">%(links)s</nav></div>'
        '<div class="footer__col footer__col--contacts">'
        '<a href="tel:%(phone)s">%(phone_view)s</a>'
        '<a href="https://wa.me/%(wa)s" rel="noopener" target="_blank">WhatsApp</a>'
        '<a href="%(ig)s" rel="noopener" target="_blank">Instagram</a>'
        '<a href="%(gis)s" rel="noopener" target="_blank">2GIS</a>'
        "</div>"
        "</div>"
        '<div class="container footer__legal">© 2026 Frnds · %(rights)s</div>'
        "</footer>"
        % {"address": escape(site.address[lang]), "open": site.hours["open"],
           "close": site.hours["close"], "links": nav_links(lang),
           "navlabel": escape(t("nav.menu", lang)),
           "phone": escape(site.phone, quote=True),
           "phone_view": escape("+7 707 480 92 15"),
           "wa": escape(site.whatsapp, quote=True),
           "ig": escape(site.instagram, quote=True), "gis": escape(site.twogis, quote=True),
           "rights": escape(t("footer.rights", lang))}
    )
