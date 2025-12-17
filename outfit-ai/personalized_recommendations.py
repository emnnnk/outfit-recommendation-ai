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


def _bottom_preference(event_type: Optional[str], style: Optional[str], sicaklik: int) -> str:
    if sicaklik >= 28 and (style in ["sporty", "casual", "street"]):
        return "shorts"
    if event_type in ["work", "meeting", "special"] or style in ["formal", "classic"]:
        return "chinos"
    return "jeans"


def _shoes_preference(event_type: Optional[str], style: Optional[str], sicaklik: int) -> str:
    if event_type == "sport" or style == "sporty":
        return "sneaker"
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

    bmi = compute_bmi(profile.height_cm, profile.weight_kg)
    fit_note = _fit_note_from_bmi(bmi)

    outfits: List[Dict[str, Any]] = []

    for i in range(max(3, min(8, count))):
        top = _select_index(tops, i)
        bottom = _select_index(bottom_candidates, i)
        shoes = _select_index(shoes_candidates, i)

        pieces = [
            item_to_piece_dict(top, gender=profile.gender, color_palette=palette),
            item_to_piece_dict(bottom, gender=profile.gender, color_palette=palette),
            item_to_piece_dict(shoes, gender=profile.gender, color_palette=palette),
        ]

        # Outerwear only for some outfits to create variety.
        if outer_candidates and (i % 2 == 0):
            outer = _select_index(outer_candidates, i)
            pieces.insert(2, item_to_piece_dict(outer, gender=profile.gender, color_palette=palette))

        # Accessory (umbrella when raining, otherwise rotate).
        accessory = None
        if yagmur == "var":
            umbrella = [a for a in accessories_all if "umbrella" in a.key]
            if umbrella:
                accessory = umbrella[0]
        elif i % 3 == 0:
            accessory = _select_index(accessories_all, i)

        if accessory:
            pieces.append(item_to_piece_dict(accessory, gender=profile.gender, color_palette=palette))

        reasons: List[str] = []
        # Weather reasons
        if yagmur == "var":
            reasons.append("Yağış ihtimaline karşı suya dayanıklı katman / şemsiye.")
        if ruzgar == "kuvvetli":
            reasons.append("Kuvvetli rüzgâr için ekstra katman önerisi.")
        if sicaklik <= 10:
            reasons.append("Düşük sıcaklık için sıcak tutan parçalar.")
        elif sicaklik >= 28:
            reasons.append("Sıcak havada nefes alan, hafif parçalar.")

        # Event/style/palette reasons
        if profile.event_type:
            reasons.append(f"{profile.event_type} için uygun parça seçimi.")
        if style:
            reasons.append(f"{style} stile göre dengeli kombin.")
        if palette:
            reasons.append(f"{palette} renk paletine uygun alternatifler.")

        if fit_note:
            reasons.append(fit_note)

        # Keep 2-4 reasons as requested (but allow 5 if BMI note is present).
        reasons = reasons[:5] if fit_note else reasons[:4]
        if len(reasons) < 2:
            reasons = (reasons + ["Gün boyu konfor ve pratik kullanım."])[:2]

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
                "meta": {
                    "base_outfit": base_outfit,
                    "mevsim": mevsim,
                    "ortam": ortam,
                    "bmi": round(bmi, 1) if bmi is not None else None,
                },
            }
        )

    return outfits
