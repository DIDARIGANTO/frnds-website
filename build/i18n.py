"""Языки, URL и строки интерфейса.

Русский живёт в корне сайта (/menu/), казахский — под /kz/, английский —
под /en/. Код языка казахского в hreflang — kk, а в URL — kz: так привычнее
посетителю. Путаница между этими двумя написаниями — типичный источник
битых ссылок, поэтому преобразование живёт только здесь.
"""

LANGS = ("ru", "kk", "en")
LANG_DIR = {"ru": "", "kk": "kz", "en": "en"}
HTML_LANG = {"ru": "ru", "kk": "kk", "en": "en"}

UI = {
    "nav.menu":       {"ru": "Меню",        "kk": "Мәзір",        "en": "Menu"},
    "nav.delivery":   {"ru": "Доставка",    "kk": "Жеткізу",      "en": "Delivery"},
    "nav.breakfast":  {"ru": "Завтраки",    "kk": "Таңғы ас",     "en": "Breakfast"},
    "nav.about":      {"ru": "Наш дом",     "kk": "Біздің үй",    "en": "Our place"},
    "nav.contacts":   {"ru": "Контакты",    "kk": "Байланыс",     "en": "Contacts"},
    "cta.whatsapp":   {"ru": "Написать в WhatsApp", "kk": "WhatsApp-қа жазу", "en": "Message on WhatsApp"},
    "cta.menu":       {"ru": "Смотреть меню", "kk": "Мәзірді қарау", "en": "See the menu"},
    "cta.add":        {"ru": "В заказ",     "kk": "Тапсырысқа",   "en": "Add"},
    "cta.added":      {"ru": "Добавлено",   "kk": "Қосылды",      "en": "Added"},
    "cart.title":     {"ru": "Ваш заказ",   "kk": "Сіздің тапсырысыңыз", "en": "Your order"},
    "cart.empty":     {"ru": "Пока пусто. Выберите что-нибудь вкусное.",
                       "kk": "Әзірге бос. Дәмді бірдеңе таңдаңыз.",
                       "en": "Empty for now. Pick something tasty."},
    "cart.total":     {"ru": "Итого",       "kk": "Барлығы",      "en": "Total"},
    "cart.send":      {"ru": "Отправить в WhatsApp", "kk": "WhatsApp арқылы жіберу", "en": "Send via WhatsApp"},
    "cart.note":      {"ru": "Это заготовка сообщения — заказ подтвердится в переписке.",
                       "kk": "Бұл — хабарлама дайындамасы, тапсырыс хат алмасуда расталады.",
                       "en": "This only drafts a message — the order is confirmed in chat."},
    "cart.pickup":    {"ru": "Самовывоз",   "kk": "Өзім аламын",  "en": "Pickup"},
    "cart.dinein":    {"ru": "В зал",       "kk": "Залда",        "en": "Dine in"},
    "cart.items":     {"ru": "позиций",     "kk": "позиция",      "en": "items"},
    "cart.clear":     {"ru": "Очистить",    "kk": "Тазалау",      "en": "Clear"},
    "cart.remove":    {"ru": "Убрать",      "kk": "Алып тастау",  "en": "Remove"},
    "hours.open":     {"ru": "Открыто сейчас", "kk": "Қазір ашық", "en": "Open now"},
    "hours.closed":   {"ru": "Сейчас закрыто", "kk": "Қазір жабық", "en": "Closed now"},
    "hours.today":    {"ru": "Сегодня до",  "kk": "Бүгін",        "en": "Today until"},
    "rating.reviews": {"ru": "отзывов на 2GIS", "kk": "2GIS-тегі пікір", "en": "reviews on 2GIS"},
    "menu.all":       {"ru": "Всё меню",    "kk": "Барлық мәзір", "en": "Full menu"},
    "dish.similar":   {"ru": "Похожие пиццы", "kk": "Ұқсас пиццалар", "en": "Similar pizzas"},
    "dish.back":      {"ru": "Ко всему меню", "kk": "Барлық мәзірге", "en": "Back to full menu"},
    "footer.rights":  {"ru": "Все права защищены", "kk": "Барлық құқықтар қорғалған", "en": "All rights reserved"},
    "skip.content":   {"ru": "Перейти к содержимому", "kk": "Мазмұнға өту", "en": "Skip to content"},
    "lang.switch":    {"ru": "Язык сайта",  "kk": "Сайт тілі",    "en": "Site language"},
    "breadcrumb.home": {"ru": "Главная",    "kk": "Басты бет",    "en": "Home"},
    "consent.template": {
        "ru": "К друзьям заходят без формальностей. У нас одна, и та короткая: пользуясь сайтом, ты принимаешь {privacy} и {offer}.",
        "kk": "Досқа формальдылықсыз кіреді. Бізде біреу ғана бар, ол да қысқа: сайтты пайдалана отырып, сіз {privacy} және {offer} қабылдайсыз.",
        "en": "Friends don't ask for paperwork. We have just one line of it: by using the site you accept our {privacy} and {offer}.",
    },
    "consent.privacy": {"ru": "обработку персональных данных",
                        "kk": "дербес деректерді өңдеуді",
                        "en": "personal data policy"},
    "consent.offer":  {"ru": "условия публичной оферты",
                       "kk": "жария оферта шарттарын",
                       "en": "public offer terms"},
    "consent.close":  {"ru": "Закрыть уведомление", "kk": "Хабарламаны жабу", "en": "Close notice"},
    "nav.privacy":    {"ru": "Политика конфиденциальности",
                       "kk": "Құпиялылық саясаты",
                       "en": "Privacy policy"},
    "nav.offer":      {"ru": "Публичная оферта",
                       "kk": "Жария оферта",
                       "en": "Public offer"},
}


def t(key, lang):
    try:
        return UI[key][lang]
    except KeyError:
        raise KeyError("нет строки интерфейса %r для языка %r" % (key, lang))


def url(lang, path=""):
    """Абсолютный путь внутри сайта: url('kk', 'menu') -> '/kz/menu/'"""
    parts = [p for p in (LANG_DIR[lang], path.strip("/")) if p]
    return "/" + "/".join(parts) + "/" if parts else "/"


def output_path(lang, path=""):
    """Путь файла внутри dist/: output_path('kk', 'menu') -> 'kz/menu/index.html'"""
    parts = [p for p in (LANG_DIR[lang], path.strip("/")) if p]
    return "/".join(parts + ["index.html"]) if parts else "index.html"


def alternate_urls(domain, path=""):
    """Карта hreflang для страницы, включая x-default на русскую версию."""
    domain = domain.rstrip("/")
    alts = {lang: domain + url(lang, path) for lang in LANGS}
    alts["x-default"] = domain + url("ru", path)
    return alts
