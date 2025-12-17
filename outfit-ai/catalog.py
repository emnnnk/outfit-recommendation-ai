"""catalog.py
Outfit pieces catalog used for assembling multi-piece outfit recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.parse import quote_plus


@dataclass(frozen=True)
class CatalogItem:
    key: str
    category: str  # top, bottom, shoes, outerwear, accessory
    label: str
    color_palettes: List[str]
    styles: List[str]
    image_filename: str
    trendyol_query: str


CATALOG: List[CatalogItem] = [
    CatalogItem(
        key="top_tshirt",
        category="top",
        label="Tişört",
        color_palettes=["neutral", "dark", "pastel", "vibrant"],
        styles=["casual", "sporty", "street", "minimalist"],
        image_filename="tisort.png",
        trendyol_query="tişört",
    ),
    CatalogItem(
        key="top_sweatshirt",
        category="top",
        label="Sweatshirt",
        color_palettes=["neutral", "dark", "pastel"],
        styles=["casual", "sporty", "street", "minimalist"],
        image_filename="kazak.png",
        trendyol_query="sweatshirt",
    ),
    CatalogItem(
        key="top_shirt",
        category="top",
        label="Gömlek",
        color_palettes=["neutral", "dark", "pastel"],
        styles=["classic", "formal", "minimalist"],
        image_filename="tisort.png",
        trendyol_query="gömlek",
    ),
    CatalogItem(
        key="bottom_jeans",
        category="bottom",
        label="Jean Pantolon",
        color_palettes=["neutral", "dark"],
        styles=["casual", "street", "classic"],
        image_filename="takim_elbise.png",
        trendyol_query="jean pantolon",
    ),
    CatalogItem(
        key="bottom_chinos",
        category="bottom",
        label="Kumaş Pantolon",
        color_palettes=["neutral", "dark", "pastel"],
        styles=["classic", "formal", "minimalist"],
        image_filename="takim_elbise.png",
        trendyol_query="kumaş pantolon",
    ),
    CatalogItem(
        key="bottom_shorts",
        category="bottom",
        label="Şort",
        color_palettes=["neutral", "dark", "vibrant"],
        styles=["casual", "sporty", "street"],
        image_filename="takim_elbise.png",
        trendyol_query="şort",
    ),
    CatalogItem(
        key="shoes_sneaker",
        category="shoes",
        label="Sneaker",
        color_palettes=["neutral", "dark", "pastel", "vibrant"],
        styles=["casual", "sporty", "street", "minimalist"],
        image_filename="takim_elbise.png",
        trendyol_query="sneaker",
    ),
    CatalogItem(
        key="shoes_boot",
        category="shoes",
        label="Bot",
        color_palettes=["neutral", "dark"],
        styles=["casual", "classic", "street"],
        image_filename="takim_elbise.png",
        trendyol_query="bot",
    ),
    CatalogItem(
        key="shoes_loafer",
        category="shoes",
        label="Loafer",
        color_palettes=["neutral", "dark"],
        styles=["classic", "formal", "minimalist"],
        image_filename="takim_elbise.png",
        trendyol_query="loafer",
    ),
    CatalogItem(
        key="outer_coat",
        category="outerwear",
        label="Mont",
        color_palettes=["neutral", "dark"],
        styles=["casual", "classic", "street", "minimalist"],
        image_filename="mont.png",
        trendyol_query="mont",
    ),
    CatalogItem(
        key="outer_jacket",
        category="outerwear",
        label="Ceket",
        color_palettes=["neutral", "dark", "pastel"],
        styles=["casual", "classic", "minimalist", "formal"],
        image_filename="ceket.png",
        trendyol_query="ceket",
    ),
    CatalogItem(
        key="outer_raincoat",
        category="outerwear",
        label="Yağmurluk",
        color_palettes=["neutral", "dark"],
        styles=["casual", "sporty", "street"],
        image_filename="yagmurluk.png",
        trendyol_query="yağmurluk",
    ),
    CatalogItem(
        key="acc_umbrella",
        category="accessory",
        label="Şemsiye",
        color_palettes=["neutral", "dark", "vibrant"],
        styles=["casual", "sporty", "classic", "street", "minimalist", "formal"],
        image_filename="yagmurluk.png",
        trendyol_query="şemsiye",
    ),
    CatalogItem(
        key="acc_scarf",
        category="accessory",
        label="Atkı",
        color_palettes=["neutral", "dark", "pastel"],
        styles=["casual", "classic", "street", "minimalist"],
        image_filename="kazak.png",
        trendyol_query="atkı",
    ),
    CatalogItem(
        key="acc_watch",
        category="accessory",
        label="Kol Saati",
        color_palettes=["neutral", "dark"],
        styles=["classic", "formal", "minimalist"],
        image_filename="takim_elbise.png",
        trendyol_query="kol saati",
    ),
]


def get_gender_query_prefix(gender: Optional[str]) -> str:
    if gender == "male":
        return "erkek"
    if gender == "female":
        return "kadın"
    return "unisex"


def get_palette_query_token(color_palette: Optional[str]) -> str:
    # Keep it intentionally broad; Trendyol search works better with simple color tokens.
    mapping = {
        "neutral": "bej",
        "dark": "siyah",
        "pastel": "pastel",
        "vibrant": "renkli",
    }
    return mapping.get(color_palette or "", "")


def trendyol_search_url(query: str) -> str:
    return f"https://www.trendyol.com/sr?q={quote_plus(query)}"


def build_piece_shop_url(*, gender: Optional[str], color_palette: Optional[str], base_query: str) -> str:
    gender_token = get_gender_query_prefix(gender)
    palette_token = get_palette_query_token(color_palette)

    parts = [p for p in [gender_token, palette_token, base_query] if p]
    return trendyol_search_url(" ".join(parts))


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
) -> Dict[str, str]:
    return {
        "category": item.category,
        "key": item.key,
        "label": item.label,
        "image": f"/static/images/outfits/{item.image_filename}",
        "link": build_piece_shop_url(gender=gender, color_palette=color_palette, base_query=item.trendyol_query),
    }
