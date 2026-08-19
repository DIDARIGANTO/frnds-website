import unittest

from build.data import Site
from build.layout import Page, render_page


def make_site():
    return Site({
        "domain": "https://frnds.kz",
        "phone": "+77074809215",
        "whatsapp": "77074809215",
        "instagram": "https://www.instagram.com/frnds.kz",
        "twogis": "https://2gis.kz/astana/firm/70000001113515854",
        "hours": {"open": "09:00", "close": "23:00"},
        "coords": {"lat": 51.119566, "lon": 71.484317},
        "address": {"ru": "Астана, улица Сағадат Нұрмағамбетов, 25",
                    "kk": "Астана, Сағадат Нұрмағамбетов көшесі, 25",
                    "en": "Astana, Sagadat Nurmagambetov Street 25"},
        "rating": {"value": 4.9, "count": 182},
        "aggregators": [],
    })


class TestRenderPage(unittest.TestCase):
    def setUp(self):
        self.html = render_page(Page(
            lang="ru", path="menu", title="Меню Frnds",
            description="Всё меню пиццерии Frnds в Астане",
            body="<main id=\"main\"><h1>Меню</h1></main>",
        ), make_site())

    def test_has_doctype_and_lang(self):
        self.assertTrue(self.html.startswith("<!DOCTYPE html>"))
        self.assertIn('<html lang="ru">', self.html)

    def test_has_title_and_description(self):
        self.assertIn("<title>Меню Frnds</title>", self.html)
        self.assertIn('name="description" content="Всё меню пиццерии Frnds в Астане"', self.html)

    def test_has_canonical_and_hreflang(self):
        self.assertIn('rel="canonical" href="https://frnds.kz/menu/"', self.html)
        self.assertIn('hreflang="ru" href="https://frnds.kz/menu/"', self.html)
        self.assertIn('hreflang="kk" href="https://frnds.kz/kz/menu/"', self.html)
        self.assertIn('hreflang="en" href="https://frnds.kz/en/menu/"', self.html)
        self.assertIn('hreflang="x-default" href="https://frnds.kz/menu/"', self.html)

    def test_escapes_title(self):
        html = render_page(Page(
            lang="ru", path="", title='Пицца "Маргарита" & кофе',
            description="d", body="<main></main>",
        ), make_site())
        self.assertIn("&quot;Маргарита&quot;", html)
        self.assertIn("&amp; кофе", html)

    def test_has_open_graph(self):
        self.assertIn('property="og:title"', self.html)
        self.assertIn('property="og:url" content="https://frnds.kz/menu/"', self.html)
        self.assertIn('property="og:image"', self.html)

    def test_has_skip_link_and_main(self):
        self.assertIn('href="#main"', self.html)
        self.assertIn('id="main"', self.html)

    def test_kazakh_page_gets_kk_lang(self):
        html = render_page(Page(
            lang="kk", path="menu", title="Мәзір", description="d",
            body="<main id=\"main\"></main>",
        ), make_site())
        self.assertIn('<html lang="kk">', html)
        self.assertIn('rel="canonical" href="https://frnds.kz/kz/menu/"', html)

    def test_json_ld_is_embedded(self):
        html = render_page(Page(
            lang="ru", path="", title="t", description="d",
            body="<main></main>", json_ld=['{"@type": "Restaurant"}'],
        ), make_site())
        self.assertIn('<script type="application/ld+json">{"@type": "Restaurant"}</script>', html)


from build.components import dish_card, footer, header, money, price_pill
from build.data import Item


def make_item(**over):
    raw = {"id": "pizza-pepperoni", "category": "pizza", "price": 3590,
           "photo": "pizza-pepperoni", "badges": ["hit"], "tags": ["spicy"],
           "name": {"ru": "Пепперони", "kk": "Пепперони", "en": "Pepperoni"},
           "desc": {"ru": "Острая пепперони и моцарелла.",
                    "kk": "Ащы пепперони мен моцарелла.",
                    "en": "Spicy pepperoni and mozzarella."}}
    raw.update(over)
    return Item(raw)


class TestComponents(unittest.TestCase):
    def test_money_formats_thousands_with_narrow_space(self):
        self.assertEqual(money(3590), "3 590 ₸")
        self.assertEqual(money(700), "700 ₸")

    def test_price_pill_formats_price_and_action(self):
        html = price_pill(3590, "ru", "pizza-pepperoni")
        self.assertIn("3 590", html)
        self.assertIn('data-add="pizza-pepperoni"', html)
        self.assertIn("В заказ", html)

    def test_dish_card_carries_data_for_cart(self):
        html = dish_card(make_item(), "ru")
        self.assertIn('data-item-id="pizza-pepperoni"', html)
        self.assertIn('data-item-price="3590"', html)
        self.assertIn("Пепперони", html)

    def test_dish_card_with_photo_uses_picture(self):
        html = dish_card(make_item(), "ru")
        self.assertIn("<picture", html)
        self.assertIn("pizza-pepperoni-400.webp", html)
        self.assertIn('loading="lazy"', html)
        self.assertIn('width="400" height="400"', html)

    def test_dish_card_without_photo_has_no_picture(self):
        html = dish_card(make_item(photo=""), "ru")
        self.assertNotIn("<picture", html)
        self.assertIn("Пепперони", html)

    def test_dish_card_escapes_text(self):
        html = dish_card(make_item(name={"ru": 'Пицца "Хит" & Co',
                                         "kk": "a", "en": "b"}), "ru")
        self.assertIn("&quot;Хит&quot;", html)
        self.assertNotIn('"Хит" & Co<', html)

    def test_dish_card_photo_links_to_dish_page(self):
        html = dish_card(make_item(), "kk")
        self.assertIn('href="/kz/menu/pizza-pepperoni/"', html)

    def test_header_has_nav_and_lang_switch(self):
        html = header("ru", make_site())
        self.assertIn('href="/menu/"', html)
        self.assertIn('href="/kz/"', html)
        self.assertIn('href="/en/"', html)
        self.assertIn("wa.me/77074809215", html)

    def test_header_lang_switch_keeps_path(self):
        html = header("ru", make_site(), path="menu")
        self.assertIn('href="/kz/menu/"', html)
        self.assertIn('href="/en/menu/"', html)

    def test_footer_has_clickable_phone(self):
        html = footer("ru", make_site())
        self.assertIn('href="tel:+77074809215"', html)
        self.assertIn("2gis.kz", html)

    def test_whatsapp_buttons_carry_icon(self):
        from build.components import whatsapp_button
        html = whatsapp_button(make_site(), "ru", "ghost")
        self.assertIn("icon-wa", html)
        self.assertIn("pill--wa", html)
        self.assertIn("pill--ghost", html)
        self.assertIn("wa.me/77074809215", html)
        # Шапка и подвал тоже используют кнопку со значком
        self.assertIn("icon-wa", header("ru", make_site()))
        self.assertIn("icon-wa", footer("ru", make_site()))


if __name__ == "__main__":
    unittest.main()
