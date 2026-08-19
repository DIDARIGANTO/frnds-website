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

# Значок WhatsApp (Simple Icons, CC0). fill="currentColor" — цвет наследуется
# от кнопки, поэтому один и тот же значок работает на оранжевой, контурной
# и зелёной (ховер) заливке.
ICON_WA = (
    '<svg class="icon-wa" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
    '<path fill="currentColor" d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967'
    '-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223'
    '-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059'
    '-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298'
    '.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242'
    '-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372'
    '-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 '
    '2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871'
    '.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074'
    '-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l'
    '-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001'
    '-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 '
    '0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 '
    '11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 '
    '5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 '
    '11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>'
)


def whatsapp_button(site, lang, variant="brand", extra_class=""):
    """Кнопка «Написать в WhatsApp»: значок + текст, зелёный ховер в CSS."""
    classes = "pill pill--%s pill--wa" % variant
    if extra_class:
        classes += " " + extra_class
    return (
        '<a class="%s" href="https://wa.me/%s" rel="noopener" target="_blank">'
        "%s<span>%s</span></a>"
        % (classes, escape(site.whatsapp, quote=True), ICON_WA,
           escape(t("cta.whatsapp", lang)))
    )


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
        "%(wa_cta)s"
        '<button class="burger" type="button" aria-expanded="false" aria-controls="mobile-nav" '
        'aria-label="%(navlabel)s"><span></span><span></span><span></span></button>'
        "</div>"
        '<div class="mobile-nav" id="mobile-nav" hidden>%(links)s%(lang)s%(wa_mobile)s</div>'
        "</header>"
        % {"logo": _logo(lang), "links": nav_links(lang), "lang": _lang_switch(lang, path),
           "wa_cta": whatsapp_button(site, lang, "brand", "header__cta"),
           "wa_mobile": whatsapp_button(site, lang, "brand"),
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
        '<a class="link-wa" href="https://wa.me/%(wa)s" rel="noopener" target="_blank">%(wa_icon)sWhatsApp</a>'
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
           "wa": escape(site.whatsapp, quote=True), "wa_icon": ICON_WA,
           "ig": escape(site.instagram, quote=True), "gis": escape(site.twogis, quote=True),
           "rights": escape(t("footer.rights", lang))}
    )
