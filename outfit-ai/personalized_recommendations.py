"""personalized_recommendations.py
Multi-outfit recommendation generator (MVP v1).

This module is intentionally lightweight and rule-driven; it augments the existing
single-category ML / rules baseline prediction with multiple outfit variations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from catalog import filter_catalog, item_to_piece_dict


@dataclass(frozen=True)
class UserProfile:
    gender: Optional[str] = None
    age_range: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    style: Optional[str] = None
    color_palette: Optional[str] = None
    cold_sensitivity: Optional[str] = None
    event_type: Optional[str] = None


def compute_bmi(height_cm: Optional[float], weight_kg: Optional[float]) -> Optional[float]:
    if not height_cm or not weight_kg:
        return None
    if height_cm <= 0 or weight_kg <= 0:
        return None
    h_m = height_cm / 100.0
    return weight_kg / (h_m * h_m)


def _select_index(items: List[Any], idx: int) -> Any:
    if not items:
        raise ValueError("No items to select from")
    return items[idx % len(items)]


def _outerwear_need(
    *,
    sicaklik: int,
    yagmur: str,
    ruzgar: str,
    cold_sensitivity: Optional[str],
) -> str:
    """Return outerwear strategy: none/light/medium/heavy/rain."""
    temp_effective = sicaklik
    if cold_sensitivity == "cold":
        temp_effective -= 3
    elif cold_sensitivity == "warm":
        temp_effective += 2

    if yagmur == "var":
        return "rain"

    if temp_effective < 7:
        return "heavy"
    if temp_effective < 15:
        return "medium"
    if temp_effective < 20 or ruzgar == "kuvvetli":
        return "light"
    return "none"


def _is_formal_event(event_type: Optional[str]) -> bool:
    return event_type in {"formal", "meeting", "work", "special"}


def _is_cold(*, sicaklik: int, cold_sensitivity: Optional[str]) -> bool:
    temp_effective = sicaklik
    if cold_sensitivity == "cold":
        temp_effective -= 3
    elif cold_sensitivity == "warm":
        temp_effective += 2
    return temp_effective <= 12


def _pick_first(items: List[Any], predicate) -> Optional[Any]:
    for it in items:
        try:
            if predicate(it):
                return it
        except Exception:
            continue
    return None


def _choose_board_key(
    *,
    event_type: Optional[str],
    style: Optional[str],
    yagmur: str,
    sicaklik: int,
    color_palette: Optional[str],
) -> str:
    if yagmur == "var":
        return "rainy"
    if sicaklik <= 8:
        return "winter"
    if sicaklik >= 28:
        return "summer"

    if event_type in {"work", "meeting"}:
        return "business"
    if event_type == "date":
        return "date"
    if event_type == "class":
        return "class"
    if event_type == "outdoors":
        return "outdoors"
    if event_type == "sport":
        return "sporty"

    if style == "street":
        return "street"
    if style == "classic":
        return "classic"
    if style == "minimalist":
        return "minimalist"
    if style == "formal":
        return "formal"

    return "default"


def _board_image_url(key: str) -> str:
    return f"/static/images/boards/{key}.svg"


def _avatar_asset(name: str) -> str:
    return f"/static/images/avatar/{name}.svg"


def _pick_piece_image(pieces: List[Dict[str, Any]], category: str) -> Optional[str]:
    for p in pieces:
        if p.get("category") == category and p.get("image"):
            return str(p.get("image"))
    return None


def _bottom_preference(event_type: Optional[str], style: Optional[str], sicaklik: int) -> str:
    if _is_formal_event(event_type) or style in ["formal", "classic"]:
        return "chinos"
    if sicaklik >= 28 and (style in ["sporty", "casual", "street"]):
        return "shorts"
    return "jeans"


def _shoes_preference(event_type: Optional[str], style: Optional[str], sicaklik: int) -> str:
    if event_type == "sport" or style == "sporty":
        return "sneaker"
    if _is_formal_event(event_type) or style in ["formal", "classic", "minimalist"]:
        return "loafer"
    if sicaklik < 10:
        return "boot"
    if event_type in ["work", "meeting", "special"] or style in ["formal", "classic", "minimalist"]:
        return "loafer"
    return "sneaker"


def _fit_note_from_bmi(bmi: Optional[float]) -> Optional[str]:
    if bmi is None:
        return None
    # Not medical advice; keep wording gentle.
    if bmi >= 27:
        return "Rahat bir kesim tercih etmek konforu artırabilir (kişisel ölçüne göre)."
    if bmi <= 19:
        return "Katmanlı giyim daha dengeli bir görünüm sağlayabilir (kişisel ölçüne göre)."
    return "Standart kesimler çoğu kombin için dengeli durur (kişisel ölçüne göre)."


def generate_outfit_recommendations(
    *,
    base_outfit: str,
    sicaklik: int,
    yagmur: str,
    ruzgar: str,
    mevsim: str,
    ortam: str,
    profile: UserProfile,
    count: int = 6,
) -> List[Dict[str, Any]]:
    """Generate 5-8 outfit recommendations.

    Output schema (per outfit):
      - title: str
      - reasons: list[str]
      - pieces: list[{category,key,label,image,link}]
    """

    style = profile.style
    palette = profile.color_palette

    formal = _is_formal_event(profile.event_type)
    cold = _is_cold(sicaklik=sicaklik, cold_sensitivity=profile.cold_sensitivity)

    outer_strategy = _outerwear_need(
        sicaklik=sicaklik,
        yagmur=yagmur,
        ruzgar=ruzgar,
        cold_sensitivity=profile.cold_sensitivity,
    )

    bottom_pref = _bottom_preference(profile.event_type, style, sicaklik)
    shoes_pref = _shoes_preference(profile.event_type, style, sicaklik)

    tops = filter_catalog(category="top", style=style, color_palette=palette)
    bottoms_all = filter_catalog(category="bottom", style=style, color_palette=palette)
    shoes_all = filter_catalog(category="shoes", style=style, color_palette=palette)
    outerwear_all = filter_catalog(category="outerwear", style=style, color_palette=palette)
    accessories_all = filter_catalog(category="accessory", style=style, color_palette=palette)

    # Fallback if any category accidentally becomes empty.
    if not tops:
        tops = filter_catalog(category="top")
    if not bottoms_all:
        bottoms_all = filter_catalog(category="bottom")
    if not shoes_all:
        shoes_all = filter_catalog(category="shoes")
    if not outerwear_all:
        outerwear_all = filter_catalog(category="outerwear")
    if not accessories_all:
        accessories_all = filter_catalog(category="accessory")

    # Preference ordering via simple key match.
    bottom_candidates: List[Any]
    if bottom_pref == "shorts":
        bottom_candidates = [b for b in bottoms_all if "short" in b.key] or bottoms_all
    elif bottom_pref == "chinos":
        bottom_candidates = [b for b in bottoms_all if "chinos" in b.key] or bottoms_all
    else:
        bottom_candidates = [b for b in bottoms_all if "jeans" in b.key] or bottoms_all

    if shoes_pref == "boot":
        shoes_candidates = [s for s in shoes_all if "boot" in s.key] or shoes_all
    elif shoes_pref == "loafer":
        shoes_candidates = [s for s in shoes_all if "loafer" in s.key] or shoes_all
    else:
        shoes_candidates = [s for s in shoes_all if "sneaker" in s.key] or shoes_all

    if outer_strategy == "rain":
        outer_candidates = [o for o in outerwear_all if "rain" in o.key] or outerwear_all
    elif outer_strategy == "heavy":
        outer_candidates = [o for o in outerwear_all if "coat" in o.key] or outerwear_all
    elif outer_strategy in ("medium", "light"):
        outer_candidates = [o for o in outerwear_all if "jacket" in o.key] or outerwear_all
    else:
        outer_candidates = []

    if cold and not outer_candidates:
        outer_candidates = [o for o in outerwear_all if ("coat" in o.key or "jacket" in o.key)] or outerwear_all

    bmi = compute_bmi(profile.height_cm, profile.weight_kg)
    fit_note = _fit_note_from_bmi(bmi)

    outfits: List[Dict[str, Any]] = []

    board_key = _choose_board_key(
        event_type=profile.event_type,
        style=style,
        yagmur=yagmur,
        sicaklik=sicaklik,
        color_palette=palette,
    )

    for i in range(max(3, min(8, count))):
        # Prefer shirt/chinos/loafer for formal contexts.
        if formal:
            top = _pick_first(tops, lambda t: "shirt" in t.key) or _select_index(tops, i)
            bottom = _pick_first(bottom_candidates, lambda b: "short" not in b.key and "chinos" in b.key) or _select_index(bottom_candidates, i)
            shoes = _pick_first(shoes_candidates, lambda s: "boot" not in s.key and "loafer" in s.key) or _select_index(shoes_candidates, i)
        else:
            top = _select_index(tops, i)
            bottom = _select_index(bottom_candidates, i)
            shoes = _select_index(shoes_candidates, i)

        # Auto-correct obvious nonsense combos.
        if formal and "short" in bottom.key:
            bottom = _pick_first(bottoms_all, lambda b: "chinos" in b.key) or bottom
        if formal and "boot" in shoes.key:
            shoes = _pick_first(shoes_all, lambda s: "loafer" in s.key) or shoes
        if yagmur == "var" and not formal and "loafer" in shoes.key:
            shoes = _pick_first(shoes_all, lambda s: "boot" in s.key or "sneaker" in s.key) or shoes

        pieces = [
            item_to_piece_dict(top, gender=profile.gender, color_palette=palette, event_type=profile.event_type),
            item_to_piece_dict(bottom, gender=profile.gender, color_palette=palette, event_type=profile.event_type),
            item_to_piece_dict(shoes, gender=profile.gender, color_palette=palette, event_type=profile.event_type),
        ]

        # Outerwear enforcement: rain/cold always layered.
        must_have_outer = outer_strategy in ("rain", "heavy", "medium") or cold
        if outer_candidates and (must_have_outer or (i % 2 == 0)):
            if outer_strategy == "rain":
                outer = _pick_first(outer_candidates, lambda o: "rain" in o.key) or _select_index(
                    outer_candidates, i
                )
            else:
                outer = _select_index(outer_candidates, i)
            pieces.insert(2, item_to_piece_dict(outer, gender=profile.gender, color_palette=palette, event_type=profile.event_type))

        # Accessory (umbrella when raining, otherwise rotate).
        accessory = None
        if yagmur == "var":
            umbrella = [a for a in accessories_all if "umbrella" in a.key]
            if umbrella:
                accessory = umbrella[0]
        elif i % 3 == 0:
            accessory = _select_index(accessories_all, i)

        if accessory:
            pieces.append(item_to_piece_dict(accessory, gender=profile.gender, color_palette=palette, event_type=profile.event_type))

        top_img = _pick_piece_image(pieces, "top") or _avatar_asset("top")
        bottom_img = _pick_piece_image(pieces, "bottom") or _avatar_asset("bottom")
        shoes_img = _pick_piece_image(pieces, "shoes") or _avatar_asset("shoes")

        outerwear_img = _pick_piece_image(pieces, "outerwear")
        if not outerwear_img and cold:
            outerwear_img = _avatar_asset("outerwear")

        accessory_img = _pick_piece_image(pieces, "accessory")
        if not accessory_img and yagmur == "var":
            accessory_img = _avatar_asset("accessory")

        # Smart theme selection based on weather and context
        themes = ['casual', 'work', 'formal', 'winter', 'summer', 'rainy']
        
        # Choose theme intelligently based on conditions
        if yagmur == "var":
            current_theme = "rainy"
        elif sicaklik >= 35:
            current_theme = "summer"
        elif sicaklik <= 10:
            current_theme = "winter"
        elif profile.event_type and profile.event_type.lower() in ["iş", "work", "ofis"]:
            current_theme = "work"
        elif profile.event_type and profile.event_type.lower() in ["davet", "party", "formal"]:
            current_theme = "formal"
        else:
            # Cycle through remaining themes for variety
            available_themes = [t for t in themes if t not in ["rainy", "winter", "summer", "work", "formal"]]
            current_theme = available_themes[i % len(available_themes)] if available_themes else "casual"
        
        reasons = _get_theme_specific_reasons(current_theme, sicaklik, yagmur, ruzgar, profile, style, palette)
        
        # Add fit note if applicable
        if fit_note:
            reasons = reasons[:3] + [fit_note]

        title_parts = []
        if style:
            title_parts.append(style.capitalize())
        else:
            title_parts.append("Günlük")
        if profile.event_type:
            title_parts.append(profile.event_type.capitalize())
        if outer_strategy in ("heavy", "rain"):
            title_parts.append("Katmanlı")
        title = " ".join(title_parts) + f" Kombin #{i + 1}"

        outfits.append(
            {
                "title": title,
                "reasons": reasons,
                "pieces": pieces,
                "board_image": _board_image_url(board_key),
                "avatar_layers": {
                    "body": _avatar_asset("body"),
                    "top": top_img,
                    "bottom": bottom_img,
                    "shoes": shoes_img,
                    "outerwear": outerwear_img or "",
                    "accessory": accessory_img or "",
                },
                "meta": {
                    "base_outfit": base_outfit,
                    "mevsim": mevsim,
                    "ortam": ortam,
                    "bmi": round(bmi, 1) if bmi is not None else None,
                },
            }
        )

    return outfits

def _get_theme_specific_reasons(theme_type: str, sicaklik: int, yagmur: str, ruzgar: str, 
                               profile: UserProfile, style: str, palette: str) -> List[str]:
    """Generate theme-specific reasons for different outfit types."""
    
    theme_reasons = {
        'winter': [
            "Soğuk kış günleri için sıcak tutan mont ve katmanlar.",
            "Karlı havada konfor sağlayan kalın kumaşlar.",
            "Rüzgarlı kış günlerinde koruyucu dış giyim.",
            "Kış stilinde şık ve fonksiyonel kombin."
        ],
        'summer': [
            "Dubai gibi sıcak iklimler için ultra hafif ve nefes alan parçalar.",
            "40°C+ sıcaklıkta serin tutan pamuk ve linen kumaşlar.",
            "Güneş korumalı açık renkli ve bol kesimli giyim.",
            "Sıcak çöl havasında modern ve pratik yaz kombinleri."
        ],
        'rainy': [
            "Yağışlı hava için suya dayanıklı katmanlar.",
            "Şemsiye ile tamamlanan yağmurlu gün kombini.",
            "Islak zeminde güvenli sağlam bot seçimi.",
            "Yağmurlu havada şık ve kuru kalma."
        ],
        'work': [
            "İş ortamı için profesyonel gömlek ve pantolon.",
            "Ofis stilinde resmi ve şık görünüm.",
            "Toplantılarda güven veren klasik parçalar.",
            "İş hayatında pratik ve elegant kombin."
        ],
        'casual': [
            "Günlük hayatta rahat kot ve tişört kombini.",
            "Sokak stilinde modern ve konforlu parçalar.",
            "Arkadaş buluşmaları için şık günlük outfit.",
            "Rahatlık ve tarzı birleştiren casual stil."
        ],
        'formal': [
            "Özel davetler için elegant ceket ve gömlek.",
            "Resmi ortamlarda zarif ve klasik görünüm.",
            "Şık aksesuarlarla tamamlanan formal stil.",
            "Özel günlerde dikkat çeken sofistike kombin."
        ]
    }
    
    # Determine theme based on conditions
    if yagmur == "var":
        theme_type = "rainy"
    elif sicaklik <= 10:
        theme_type = "winter"
    elif sicaklik >= 28:
        theme_type = "summer"
    elif profile.event_type in ["work", "meeting"]:
        theme_type = "work"
    elif profile.event_type in ["special", "date"]:
        theme_type = "formal"
    else:
        theme_type = "casual"
    
    # Get theme-specific reasons
    base_reasons = theme_reasons.get(theme_type, theme_reasons['casual'])
    
    # Add some variation based on style and palette
    final_reasons = base_reasons[:2]  # Start with first 2 theme reasons
    
    # Add style-specific reason if different from theme
    if style and style not in ["casual", "formal", "work"]:
        style_reasons = {
            "sporty": "Spor ve dinamik görünüm için hareketli parçalar.",
            "classic": "Klasik ve zamansız parçalarla elegant stil.",
            "street": "Sokak modasına uygun modern ve cesur parçalar.",
            "minimalist": "Sade ve minimalist çizgilerle modern görünüm."
        }
        if style in style_reasons:
            final_reasons.append(style_reasons[style])
    
    # Add palette-specific reason
    if palette:
        palette_reasons = {
            "neutral": "Nötr renk paleti ile her ortama uyumlu stil.",
            "dark": "Koyu renkler ile gizemli ve şık görünüm.",
            "pastel": "Pastel tonlarla yumuşak ve romantik stil.",
            "vibrant": "Canlı renkler ile enerjik ve dikkat çekici görünüm."
        }
        if palette in palette_reasons:
            final_reasons.append(palette_reasons[palette])
    
    # Ensure we have at least 2-4 reasons
    if len(final_reasons) < 2:
        final_reasons.append("Gün boyu konfor ve pratik kullanım.")
    
    return final_reasons[:4]
