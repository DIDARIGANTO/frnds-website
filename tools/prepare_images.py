"""Разовая подготовка изображений: логотипы, фото пицц, OG-превью.

Запускается вручную после появления новых фото:
    python3 tools/prepare_images.py <путь-к-исходникам>

Ожидаемая структура исходников:
    <путь>/menu/pizza_imgs/x18.png … x40.png   фото пицц 3000×3000
    <путь>/frnds-logo-{white,orange,dark}.png  логотипы с прозрачностью
"""

import sys
from pathlib import Path

from PIL import Image

WIDTHS = (400, 800, 1200)

# Соответствие исходных кадров слагам блюд. Порядок совпадает с раскладкой
# макета меню: сначала первая страница слева направо по рядам, потом вторая.
PIZZA_ORDER = [
    ("x22", "pizza-meat-kazy"),
    ("x21", "pizza-margherita"),
    ("x18", "pizza-pepperoni"),
    ("x23", "pizza-salmon-broccoli"),
    ("x19", "pizza-bolognese"),
    ("x20", "pizza-stracciatella-lecho"),
    ("x34", "pizza-chicken-tomato"),
    ("x35", "pizza-meatballs"),
    ("x36", "pizza-shrimp"),
    ("x37", "pizza-strawberry-gorgonzola"),
    ("x38", "pizza-cheese"),
    ("x39", "pizza-truffle-mushroom"),
    ("x40", "pizza-carbonara"),
]


def prepare_pizzas(source, target):
    target.mkdir(parents=True, exist_ok=True)
    done = 0
    for raw_name, slug in PIZZA_ORDER:
        matches = sorted(source.glob("*_%s_*.png" % raw_name)) or [source / ("%s.png" % raw_name)]
        src = matches[0]
        if not src.exists():
            print("пропуск, нет файла: %s" % src)
            continue
        img = Image.open(src).convert("RGB")
        side = min(img.size)
        left = (img.width - side) // 2
        top = (img.height - side) // 2
        img = img.crop((left, top, left + side, top + side))
        for width in WIDTHS:
            resized = img.resize((width, width), Image.LANCZOS)
            resized.save(target / ("%s-%d.webp" % (slug, width)), "WEBP", quality=82, method=6)
            resized.save(target / ("%s-%d.jpg" % (slug, width)), "JPEG", quality=84, optimize=True)
        print("готово: %s" % slug)
        done += 1
    return done


def prepare_logos(source, target):
    target.mkdir(parents=True, exist_ok=True)
    for variant in ("white", "orange", "dark"):
        src = source / ("frnds-logo-%s.png" % variant)
        if not src.exists():
            print("пропуск, нет логотипа: %s" % src)
            continue
        img = Image.open(src)
        for width in (320, 640):
            height = round(img.height * width / img.width)
            out = img.resize((width, height), Image.LANCZOS)
            out.save(target / ("frnds-%s-%d.png" % (variant, width)), "PNG", optimize=True)
        print("готово: логотип %s" % variant)


def prepare_og(source, img_root):
    """Превью 1200×630 для WhatsApp и соцсетей: пицца на кремовом + логотип."""
    pizza_path = img_root / "pizza" / "pizza-margherita-800.jpg"
    if not pizza_path.exists():
        print("пропуск OG: сначала нужны фото пицц")
        return
    canvas = Image.new("RGB", (1200, 630), (253, 248, 243))
    pizza = Image.open(pizza_path).resize((520, 520), Image.LANCZOS)
    canvas.paste(pizza, (640, 55))
    logo_path = source / "frnds-logo-orange.png"
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        logo.thumbnail((440, 440), Image.LANCZOS)
        canvas.paste(logo, (80, 220), logo)
    canvas.save(img_root / "og-default.jpg", "JPEG", quality=88, optimize=True)
    print("готово: og-default.jpg")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    source = Path(sys.argv[1])
    img_root = Path(__file__).resolve().parent.parent / "src" / "img"
    prepare_pizzas(source / "menu" / "pizza_imgs", img_root / "pizza")
    prepare_logos(source, img_root / "logo")
    prepare_og(source, img_root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
