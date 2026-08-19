"""Контакты: адрес, часы, карта, способы связи."""

from html import escape

from build.components import whatsapp_button
from build.i18n import t, url
from build.layout import Page
from build.seo import breadcrumbs_jsonld, restaurant_jsonld


def build(site, menu, texts, lang):
    wa = "https://wa.me/%s" % site.whatsapp
    aggregators = "".join(
        '<li><a href="%s" rel="noopener" target="_blank">%s</a></li>'
        % (escape(a["url"], quote=True), escape(a["name"]))
        for a in site.aggregators
    )
    aggregator_block = (
        '<div class="tile"><h3>%s</h3><ul>%s</ul></div>'
        % (escape({"ru": "Агрегаторы", "kk": "Агрегаторлар", "en": "Delivery apps"}[lang]),
           aggregators)
        if aggregators else ""
    )

    body = (
        '<main id="main"><div class="container">'
        "<h1>%(h1)s</h1><p class=\"hero__lead\">%(intro)s</p>"
        '<img class="stroke" src="/img/stroke.svg" alt="" width="150" height="10">'
        "</div>"
        '<section class="section"><div class="container">'
        '<div class="tiles">'
        '<div class="tile"><h3>%(addr_title)s</h3><p>%(address)s</p><p>%(landmarks)s</p></div>'
        '<div class="tile"><h3>%(hours_title)s</h3><p>%(open)s — %(close)s</p><p>%(hours_note)s</p></div>'
        '<div class="tile"><h3>%(contact_title)s</h3>'
        '<p><a href="tel:%(phone)s">%(phone_view)s</a></p>'
        '<p><a href="%(wa)s" rel="noopener" target="_blank">WhatsApp</a></p>'
        '<p><a href="%(ig)s" rel="noopener" target="_blank">Instagram</a></p></div>'
        "%(aggregators)s"
        "</div>"
        '<p class="section__more">%(wa_btn)s</p>'
        "</div></section>"
        '<section class="section section--tint"><div class="container">'
        '<div id="map" data-lat="%(lat)s" data-lon="%(lon)s" data-label="%(label)s"></div>'
        '<p class="section__more"><a href="%(gis)s" rel="noopener" target="_blank">2GIS →</a></p>'
        "</div></section></main>"
        % {"h1": escape(texts["h1"]), "intro": escape(texts["intro"]),
           "addr_title": escape({"ru": "Адрес", "kk": "Мекенжай", "en": "Address"}[lang]),
           "address": escape(site.address[lang]), "landmarks": escape(texts["landmarks"]),
           "hours_title": escape({"ru": "Часы работы", "kk": "Жұмыс уақыты", "en": "Opening hours"}[lang]),
           "open": site.hours["open"], "close": site.hours["close"],
           "hours_note": escape(texts["hours_note"]),
           "contact_title": escape({"ru": "Связаться", "kk": "Байланысу", "en": "Get in touch"}[lang]),
           "phone": escape(site.phone, quote=True), "phone_view": "+7 707 480 92 15",
           "wa": wa, "wa_btn": whatsapp_button(site, lang, "brand"),
           "ig": escape(site.instagram, quote=True),
           "aggregators": aggregator_block,
           "cta_wa": escape(t("cta.whatsapp", lang)),
           "lat": site.coords["lat"], "lon": site.coords["lon"],
           "label": escape("Frnds — %s" % site.address[lang], quote=True),
           "gis": escape(site.twogis, quote=True)}
    )

    return Page(
        lang=lang, path="contacts", title=texts["seo_title"],
        description=texts["seo_description"], body=body,
        json_ld=[
            restaurant_jsonld(site, lang),
            breadcrumbs_jsonld([
                (t("breadcrumb.home", lang), site.domain + url(lang, "")),
                (texts["h1"], site.domain + url(lang, "contacts")),
            ]),
        ],
        body_class="page-contacts", needs_map=True,
    )
