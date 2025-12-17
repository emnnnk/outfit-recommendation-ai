"""catalog.py
Outfit pieces catalog used for assembling multi-piece outfit recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.parse import quote_plus
from pathlib import Path
import re


@dataclass(frozen=True)
class CatalogItem:
    key: str
    category: str  # top, bottom, shoes, outerwear, accessory
    label: str
    color_palettes: List[str]
    styles: List[str]
    image_filename: str
    shop_query: str


CATALOG: List[CatalogItem] = [
    CatalogItem(
        key="top_tshirt",
        category="top",
        label="Tişört",
        color_palettes=["neutral", "dark", "pastel", "vibrant"],
        styles=["casual", "sporty", "street", "minimalist"],
        image_filename="tisort.png",
        shop_query="tişört",
    ),
    CatalogItem(
        key="top_sweatshirt",
        category="top",
        label="Sweatshirt",
        color_palettes=["neutral", "dark", "pastel"],
        styles=["casual", "sporty", "street", "minimalist"],
        image_filename="kazak.png",
        shop_query="sweatshirt",
    ),
    CatalogItem(
        key="top_shirt",
        category="top",
        label="Gömlek",
        color_palettes=["neutral", "dark", "pastel"],
        styles=["classic", "formal", "minimalist"],
        image_filename="tisort.png",
        shop_query="gömlek",
    ),
    CatalogItem(
        key="bottom_jeans",
        category="bottom",
        label="Jean Pantolon",
        color_palettes=["neutral", "dark"],
        styles=["casual", "street", "classic"],
        image_filename="takim_elbise.png",
        shop_query="jean pantolon",
    ),
    CatalogItem(
        key="bottom_chinos",
        category="bottom",
        label="Kumaş Pantolon",
        color_palettes=["neutral", "dark", "pastel"],
        styles=["classic", "formal", "minimalist"],
        image_filename="takim_elbise.png",
        shop_query="kumaş pantolon",
    ),
    CatalogItem(
        key="bottom_shorts",
        category="bottom",
        label="Şort",
        color_palettes=["neutral", "dark", "vibrant"],
        styles=["casual", "sporty", "street"],
        image_filename="takim_elbise.png",
        shop_query="şort",
    ),
    CatalogItem(
        key="shoes_sneaker",
        category="shoes",
        label="Sneaker",
        color_palettes=["neutral", "dark", "pastel", "vibrant"],
        styles=["casual", "sporty", "street", "minimalist"],
        image_filename="takim_elbise.png",
        shop_query="sneaker",
    ),
    CatalogItem(
        key="shoes_boot",
        category="shoes",
        label="Bot",
        color_palettes=["neutral", "dark"],
        styles=["casual", "classic", "street"],
        image_filename="takim_elbise.png",
        shop_query="bot",
    ),
    CatalogItem(
        key="shoes_loafer",
        category="shoes",
        label="Loafer",
        color_palettes=["neutral", "dark"],
        styles=["classic", "formal", "minimalist"],
        image_filename="takim_elbise.png",
        shop_query="loafer",
    ),
    CatalogItem(
        key="outer_coat",
        category="outerwear",
        label="Mont",
        color_palettes=["neutral", "dark"],
        styles=["casual", "classic", "street", "minimalist"],
        image_filename="mont.png",
        shop_query="mont",
    ),
    CatalogItem(
        key="outer_jacket",
        category="outerwear",
        label="Ceket",
        color_palettes=["neutral", "dark", "pastel"],
        styles=["casual", "classic", "minimalist", "formal"],
        image_filename="ceket.png",
        shop_query="ceket",
    ),
    CatalogItem(
        key="outer_raincoat",
        category="outerwear",
        label="Yağmurluk",
        color_palettes=["neutral", "dark"],
        styles=["casual", "sporty", "street"],
        image_filename="yagmurluk.png",
        shop_query="yağmurluk",
    ),
    CatalogItem(
        key="acc_umbrella",
        category="accessory",
        label="Şemsiye",
        color_palettes=["neutral", "dark", "vibrant"],
        styles=["casual", "sporty", "classic", "street", "minimalist", "formal"],
        image_filename="yagmurluk.png",
        shop_query="şemsiye",
    ),
    CatalogItem(
        key="acc_scarf",
        category="accessory",
        label="Atkı",
        color_palettes=["neutral", "dark", "pastel"],
        styles=["casual", "classic", "street", "minimalist"],
        image_filename="kazak.png",
        shop_query="atkı",
    ),
    CatalogItem(
        key="acc_watch",
        category="accessory",
        label="Kol Saati",
        color_palettes=["neutral", "dark"],
        styles=["classic", "formal", "minimalist"],
        image_filename="takim_elbise.png",
        shop_query="kol saati",
    ),
]


def get_gender_query_prefix(gender: Optional[str]) -> str:
    if gender == "male":
        return "erkek"
    if gender == "female":
        return "kadın"
    return "unisex"


def get_palette_query_token(color_palette: Optional[str]) -> str:
    mapping = {
        "neutral": "bej",
        "dark": "siyah",
        "pastel": "pastel",
        "vibrant": "renkli",
    }
    return mapping.get(color_palette or "", "")


def boyner_search_url(query: str) -> str:
    return f"https://www.boyner.com.tr/search?q={quote_plus(query)}"


def build_piece_shop_url(
    *,
    gender: Optional[str],
    color_palette: Optional[str],
    event_type: Optional[str],
    base_query: str,
) -> str:
    gender_token = get_gender_query_prefix(gender)
    palette_token = get_palette_query_token(color_palette)

    event_token = (event_type or "").strip().replace("_", " ")

    parts = [p for p in [gender_token, event_token, palette_token, base_query] if p]
    return boyner_search_url(" ".join(parts))


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _static_images_dir() -> Path:
    return _repo_root() / "web-app" / "static" / "images"


def _slugify(text: str) -> str:
    tr_map = str.maketrans({
        "ç": "c",
        "Ç": "c",
        "ğ": "g",
        "Ğ": "g",
        "ı": "i",
        "İ": "i",
        "ö": "o",
        "Ö": "o",
        "ş": "s",
        "Ş": "s",
        "ü": "u",
        "Ü": "u",
    })
    out = text.translate(tr_map).lower().strip()
    out = re.sub(r"[^a-z0-9]+", "-", out)
    out = re.sub(r"-+", "-", out).strip("-")
    return out or "item"


def _palette_colors(color_palette: Optional[str]) -> tuple[str, str]:
    mapping = {
        "neutral": ("#11192f", "#4facfe"),
        "dark": ("#0a0a1a", "#302b63"),
        "pastel": ("#ffecd2", "#f093fb"),
        "vibrant": ("#f5576c", "#4facfe"),
    }
    return mapping.get(color_palette or "", ("#11192f", "#667eea"))


def _category_fallback_url(category: str) -> str:
    safe = category if category in {"top", "bottom", "shoes", "outerwear", "accessory"} else "top"
    return f"/static/images/pieces_fallback/{safe}.svg"


def _looks_like_category_image(*, category: str, filename: str) -> bool:
    name = (filename or "").lower()
    keywords = {
        "top": ["tisort", "tshirt", "kazak", "sweat", "gomlek", "gömlek", "shirt", "top"],
        "bottom": ["pant", "jean", "chinos", "short", "şort", "bottom"],
        "shoes": ["shoe", "sneaker", "bot", "boot", "loafer", "ayakk"],
        "outerwear": ["mont", "ceket", "jacket", "coat", "rain", "yagm", "yağ"],
        "accessory": ["umbrella", "sems", "şem", "atk", "scarf", "watch", "saat", "acc"],
    }
    allowed = keywords.get(category, [])
    return any(k in name for k in allowed)


def ensure_generated_piece_svg(
    *,
    category: str,
    label: str,
    color_palette: Optional[str],
) -> str:
    images_dir = _static_images_dir()
    gen_dir = images_dir / "generated"
    gen_dir.mkdir(parents=True, exist_ok=True)

    palette_a, palette_b = _palette_colors(color_palette)
    filename = f"{category}__{_slugify(label)}__{_slugify(color_palette or 'default')}.svg"
    path = gen_dir / filename

    if path.exists():
        return f"/static/images/generated/{filename}"

    icon_map = {
        "top": "T",
        "bottom": "B",
        "shoes": "S",
        "outerwear": "O",
        "accessory": "A",
    }
    icon = icon_map.get(category, "P")
    safe_label = label.replace("&", "and")

    svg = f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"512\" height=\"512\" viewBox=\"0 0 512 512\">
  <defs>
    <linearGradient id=\"g\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\">
      <stop offset=\"0\" stop-color=\"{palette_a}\"/>
      <stop offset=\"1\" stop-color=\"{palette_b}\"/>
    </linearGradient>
  </defs>
  <rect width=\"512\" height=\"512\" rx=\"48\" fill=\"url(#g)\"/>
  <rect x=\"56\" y=\"64\" width=\"400\" height=\"280\" rx=\"28\" fill=\"rgba(255,255,255,0.10)\" stroke=\"rgba(255,255,255,0.16)\"/>
  <g font-family=\"Inter,Segoe UI,Arial\" fill=\"rgba(255,255,255,0.92)\" text-anchor=\"middle\">
    <text x=\"256\" y=\"215\" font-size=\"140\" font-weight=\"900\">{icon}</text>
    <text x=\"256\" y=\"402\" font-size=\"24\" font-weight=\"800\">{safe_label}</text>
    <text x=\"256\" y=\"438\" font-size=\"14\" font-weight=\"600\" fill=\"rgba(255,255,255,0.72)\">{category}</text>
  </g>
</svg>\n"""

    try:
        path.write_text(svg, encoding="utf-8")
        return f"/static/images/generated/{filename}"
    except OSError:
        return _category_fallback_url(category)


def resolve_piece_image_url(*, category: str, label: str, image_filename: str, color_palette: Optional[str]) -> str:
    images_dir = _static_images_dir()
    outfits_dir = images_dir / "outfits"
    outfits_dir.mkdir(parents=True, exist_ok=True)

    filename = (image_filename or "").strip()
    if filename:
        disk_path = outfits_dir / filename
        if disk_path.exists() and _looks_like_category_image(category=category, filename=filename):
            return f"/static/images/outfits/{filename}"

    # Generated per-piece placeholder (unique per label/category/palette)
    generated = ensure_generated_piece_svg(category=category, label=label, color_palette=color_palette)
    return generated or _category_fallback_url(category)


def filter_catalog(
    *,
    category: str,
    style: Optional[str] = None,
    color_palette: Optional[str] = None,
) -> List[CatalogItem]:
    items = [i for i in CATALOG if i.category == category]

    if style:
        styled = [i for i in items if style in i.styles]
        if styled:
            items = styled

    if color_palette:
        pal = [i for i in items if color_palette in i.color_palettes]
        if pal:
            items = pal

    return items


def item_to_piece_dict(
    item: CatalogItem,
    *,
    gender: Optional[str],
    color_palette: Optional[str],
    event_type: Optional[str] = None,
) -> Dict[str, str]:
    image_url = resolve_piece_image_url(
        category=item.category,
        label=item.label,
        image_filename=item.image_filename,
        color_palette=color_palette,
    )
    shop_link = build_piece_shop_url(
        gender=gender,
        color_palette=color_palette,
        event_type=event_type,
        base_query=item.shop_query,
    )
    return {
        "category": item.category,
        "key": item.key,
        "label": item.label,
        "image": image_url,
        "shop_link": shop_link,
        "link": shop_link,
    }
