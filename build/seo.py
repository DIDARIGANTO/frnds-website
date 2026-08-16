"""Карта сайта, robots.txt и микроразметка Schema.org."""

import json
from xml.sax.saxutils import escape as xml_escape

from build.i18n import LANGS, url

_CUISINE = ["Pizza", "Italian", "Breakfast", "Coffee"]


def _dumps(payload):
    """Компактный JSON без экранирования кириллицы, безопасный внутри <script>."""
    text = json.dumps(payload, ensure_ascii=False, separators=(", ", ": "))
    return text.replace("</", "<\\/")


def sitemap_xml(domain, paths):
    domain = domain.rstrip("/")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
             'xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for path in paths:
        for lang in LANGS:
            loc = domain + url(lang, path)
            lines.append("  <url>")
            lines.append("    <loc>%s</loc>" % xml_escape(loc))
            for alt in LANGS:
                lines.append(
                    '    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>'
                    % (alt, xml_escape(domain + url(alt, path)))
                )
            lines.append("    <changefreq>weekly</changefreq>")
            lines.append("    <priority>%s</priority>" % ("1.0" if path == "" else "0.8"))
            lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def robots_txt(domain):
    return (
        "User-agent: *\n"
        "Allow: /\n\n"
        "Sitemap: %s/sitemap.xml\n" % domain.rstrip("/")
    )


def restaurant_jsonld(site, lang):
    return _dumps({
        "@context": "https://schema.org",
        "@type": "Restaurant",
        "name": "Frnds",
        "url": site.domain + url(lang, ""),
        "image": site.domain + "/img/og-default.jpg",
        "telephone": site.phone,
        "priceRange": "₸₸",
        "servesCuisine": _CUISINE,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": site.address[lang],
            "addressLocality": {"ru": "Астана", "kk": "Астана", "en": "Astana"}[lang],
            "addressCountry": "KZ",
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": site.coords["lat"],
            "longitude": site.coords["lon"],
        },
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday",
                          "Friday", "Saturday", "Sunday"],
            "opens": site.hours["open"],
            "closes": site.hours["close"],
        }],
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": site.rating["value"],
            "reviewCount": site.rating["count"],
        },
        "sameAs": [s for s in (site.instagram, site.twogis) if s],
    })


def _menu_item_payload(site, item, lang):
    payload = {
        "@type": "MenuItem",
        "name": item.name[lang],
        "description": item.desc[lang],
        "offers": {
            "@type": "Offer",
            "price": item.price,
            "priceCurrency": "KZT",
        },
    }
    if item.photo:
        payload["image"] = "%s/img/pizza/%s-800.jpg" % (site.domain, item.photo)
        payload["url"] = site.domain + url(lang, "menu/%s" % item.id)
    return payload


def menuitem_jsonld(site, item, lang):
    payload = _menu_item_payload(site, item, lang)
    payload["@context"] = "https://schema.org"
    return _dumps(payload)


def menu_jsonld(site, menu, lang):
    sections = []
    for cat in menu.categories:
        items = menu.by_category(cat.id)
        if not items:
            continue
        sections.append({
            "@type": "MenuSection",
            "name": cat.name[lang],
            "hasMenuItem": [_menu_item_payload(site, i, lang) for i in items],
        })
    return _dumps({
        "@context": "https://schema.org",
        "@type": "Menu",
        "name": {"ru": "Меню Frnds", "kk": "Frnds мәзірі", "en": "Frnds menu"}[lang],
        "inLanguage": lang,
        "hasMenuSection": sections,
    })


def breadcrumbs_jsonld(crumbs):
    return _dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": href}
            for i, (name, href) in enumerate(crumbs)
        ],
    })
