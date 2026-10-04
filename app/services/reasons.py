"""Human readable explanation generator.

For a location and a planet the generator:

1. computes every feature's share of the total weighted distance
   (:func:`app.services.similarity.feature_contributions`),
2. keeps the ``top_n`` most influential features,
3. turns each into a natural-language sentence that states both the measured
   value and the planetary ideal, explaining *why* the location is (or is not)
   a good analog.

Complexity: O(F log F) for the sort inside ``feature_contributions`` followed by
O(top_n) formatting; ``top_n`` is a small constant (3-5).
"""

from __future__ import annotations

from typing import Mapping

from app.services.similarity import (
    FEATURE_INDEX,
    Profile,
    feature_contributions,
    signed_delta,
)

# A normalised delta below this is treated as "matches the planetary ideal".
CLOSE_THRESHOLD = 0.12

PLANET_LABEL = {"moon": "Oy", "mars": "Mars"}

# Category used for grouping reasons in the UI.
FEATURE_CATEGORY: Mapping[str, str] = {
    "avg_temp_c": "temperature",
    "temp_range_c": "temperature",
    "annual_rainfall_mm": "water",
    "humidity_pct": "water",
    "terrain_roughness": "geology",
    "iron_oxide_level": "chemistry",
    "basalt_level": "geology",
    "radiation_level": "radiation",
    "dust_level": "dust",
    "lava_tubes": "structure",
    "ice_presence": "water",
}

# Templates keyed by (planet, feature). ``close`` == behaves like the planet,
# ``high`` == the location has more of the feature, ``low`` == less.
REASON_TEMPLATES: dict[tuple[str, str], dict[str, str]] = {
    # ------------------------------ Mars ------------------------------- #
    ("mars", "avg_temp_c"): {
        "close": "O'rtacha harorat {value} — Mars yuzasidagi o'ta sovuq rejimga ({ideal}) mos keladi.",
        "high": "O'rtacha harorat {value} Mars idealidan ({ideal}) issiqroq, ammo quruq iqlim analogiyani saqlaydi.",
        "low": "O'rtacha harorat {value} Mars idealidan ({ideal}) sovuqroq — muzlik haroratiga yaqin.",
    },
    ("mars", "temp_range_c"): {
        "close": "Kun-tun harorat tebranishi {value} — Marsning keskin sutkalik tebranishiga ({ideal}) o'xshaydi.",
        "high": "Harorat tebranishi {value} Mars idealidan ({ideal}) ham katta — ekstremal kontinental sharoit.",
        "low": "Harorat tebranishi {value} Mars idealidan ({ideal}) kichik, iqlim barqarorroq.",
    },
    ("mars", "annual_rainfall_mm"): {
        "close": "Yillik yog'in {value} — Marsdagi deyarli nol yog'inga ({ideal}) mos.",
        "high": "Yillik yog'in {value} Mars idealidan ({ideal}) yuqori, lekin boshqa omillar analogiyani qo'llab-quvvatlaydi.",
        "low": "Yillik yog'in {value} — Marsning suvsiz yuzasini ({ideal}) takrorlaydi.",
    },
    ("mars", "humidity_pct"): {
        "close": "Nisbiy namlik {value} — Mars atmosferasidagi o'ta quruq sharoitga ({ideal}) o'xshash.",
        "high": "Namlik {value} Mars idealidan ({ideal}) yuqori, biroq asosiy ko'rsatkichlar mos.",
        "low": "Namlik {value} Mars idealidan ({ideal}) past — yana quruqroq, o'ta antibakterial muhit.",
    },
    ("mars", "terrain_roughness"): {
        "close": "Relyef notekisligi {value} — Marsdagi krater va vodiy relyefiga ({ideal}) mos.",
        "high": "Relyef {value} Mars idealidan ({ideal}) notekisroq, jarlik va qoyalar ko'p.",
        "low": "Relyef {value} Mars idealidan ({ideal}) tekisroq — keng tekislik.",
    },
    ("mars", "iron_oxide_level"): {
        "close": "Yuqori temir oksidi darajasi {value} — Marsning qizil regolitini ({ideal}) eslatadi.",
        "high": "Temir oksidi juda yuqori ({value}); Marsning qizil changi bilan kuchli moslik.",
        "low": "Temir oksidi {value} Mars idealidan ({ideal}) past, qizil komponent kamroq.",
    },
    ("mars", "basalt_level"): {
        "close": "Bazalt darajasi {value} — Marsning bazalt qobig'iga ({ideal}) mos.",
        "high": "Bazalt darajasi {value} Mars idealidan ({ideal}) yuqori — vulkanik magma ko'p.",
        "low": "Bazalt darajasi {value} Mars idealidan ({ideal}) past, cho'kindi jinslar ustun.",
    },
    ("mars", "radiation_level"): {
        "close": "Radiatsiya darajasi {value} — yupqa atmosferali Mars yuzasiga ({ideal}) yaqin.",
        "high": "Radiatsiya {value} Mars idealidan ({ideal}) yuqori — yupqa atmosferaga ega.",
        "low": "Radiatsiya {value} Mars idealidan ({ideal}) past — zich atmosfera himoya qiladi.",
    },
    ("mars", "dust_level"): {
        "close": "Chang darajasi {value} — Marsdagi global chang bo'ronlariga ({ideal}) o'xshaydi.",
        "high": "Chang {value} Mars idealidan ({ideal}) yuqori — chang bo'roni sharoitiga juda yaqin.",
        "low": "Chang {value} Mars idealidan ({ideal}) past, sirt ancha barqaror.",
    },
    ("mars", "lava_tubes"): {
        "close": "Lava quvurlari mavjud — Marsdagi yer osti lava naylariga o'xshash yashash muhiti.",
        "high": "Lava quvurlari mavjud — Marsda ham potentsial lava naylar bor, bevosita analogiya.",
        "low": "Lava quvurlari yo'q — Mars lava naylariga ega, bu jihatdan kamchilik.",
    },
    ("mars", "ice_presence"): {
        "close": "Muz mavjudligi Mars qutb muzliklari bilan mos — suv/CO₂ muz saxonalari analogi.",
        "high": "Muz mavjud — Mars qutb muzliklari bilan qo'shimcha o'xshashlik.",
        "low": "Muz yo'q — Marsda qutb muzliklari bor, bu farqni hisobga olish kerak.",
    },
    # ------------------------------ Moon ------------------------------- #
    ("moon", "avg_temp_c"): {
        "close": "O'rtacha harorat {value} — Oyning o'ta sovuq tungi rejimiga ({ideal}) mos.",
        "high": "O'rtacha harorat {value} Oy idealidan ({ideal}) issiqroq, quyoshli kunduzni eslatadi.",
        "low": "O'rtacha harorat {value} — Oyning sovuq qutb kraterlariga ({ideal}) yaqin.",
    },
    ("moon", "temp_range_c"): {
        "close": "Harorat tebranishi {value} — Oyning ~300°C sutkalik tebranishiga ({ideal}) o'xshaydi.",
        "high": "Harorat tebranishi {value} — Oy darajasidagi ekstremal tebranish, magniyi kuchli.",
        "low": "Harorat tebranishi {value} Oy idealidan ({ideal}) kichik.",
    },
    ("moon", "annual_rainfall_mm"): {
        "close": "Yillik yog'in {value} — Oyda yog'in yo'q ({ideal}), mutlaq quruqlik mos keladi.",
        "high": "Yillik yog'in {value} Oydagi nol yog'in ({ideal}) bilan farq qiladi.",
        "low": "Yillik yog'in {value} — Oydagi suvsizlikka ({ideal}) to'liq mos.",
    },
    ("moon", "humidity_pct"): {
        "close": "Namlik {value} — Oydagi vakuum sharoitiga ({ideal}) yaqin, suv bug'i yo'q.",
        "high": "Namlik {value} Oy idealidan ({ideal}) yuqori, ammo o'ta quruq baribir.",
        "low": "Namlik {value} — Oydagi suvsiz muhitni ({ideal}) takrorlaydi.",
    },
    ("moon", "terrain_roughness"): {
        "close": "Relyef notekisligi {value} — Oydagi regolit va krater relyefiga ({ideal}) mos.",
        "high": "Relyef {value} Oy idealidan ({ideal}) notekisroq — qo'pol, toshloq sirt.",
        "low": "Relyef {value} Oy idealidan ({ideal}) tekisroq — Oy marelariga o'xshash tekislik.",
    },
    ("moon", "iron_oxide_level"): {
        "close": "Temir oksidi darajasi {value} — Oyning temirga boy regolitiga ({ideal}) mos.",
        "high": "Temir oksidi {value} Oy idealidan ({ideal}) yuqori.",
        "low": "Temir oksidi {value} Oy idealidan ({ideal}) past.",
    },
    ("moon", "basalt_level"): {
        "close": "Bazalt darajasi {value} — Oy marelarining bazalt tekisliklariga ({ideal}) mos.",
        "high": "Bazalt {value} — Oy bazalt marelariga juda yaqin, kuchli analog.",
        "low": "Bazalt {value} Oy idealidan ({ideal}) past, anorthozit yuqori bo'lishi mumkin.",
    },
    ("moon", "radiation_level"): {
        "close": "Radiatsiya darajasi {value} — atmosferasiz Oy yuzasiga ({ideal}) yaqin.",
        "high": "Radiatsiya {value} — Oy yuzasidagi yuqori nurlanishga juda yaqin.",
        "low": "Radiatsiya {value} Oy idealidan ({ideal}) past — atmosfera qalqoni mavjud.",
    },
    ("moon", "dust_level"): {
        "close": "Chang darajasi {value} — Oy regolit changiga ({ideal}) o'xshaydi.",
        "high": "Chang {value} Oy idealidan ({ideal}) yuqori — regolit changi ko'p.",
        "low": "Chang {value} Oy idealidan ({ideal}) past, sirt changdan tozalangan.",
    },
    ("moon", "lava_tubes"): {
        "close": "Lava quvurlari mavjud — Oy lava naylari (masalan, Marius Hills) analogi.",
        "high": "Lava quvurlari mavjud — Oy lava naylariga bevosita o'xshash.",
        "low": "Lava quvurlari yo'q — Oyda lava naylari bor, bu jihatdan kamchilik.",
    },
    ("moon", "ice_presence"): {
        "close": "Muz mavjud — Oy qutb kraterlaridagi suv muziga o'xshash.",
        "high": "Muz mavjud — Oyning sovuq tuzoqlariga qo'shimcha o'xshashlik.",
        "low": "Muz yo'q — Oyda faqat qutb kraterlarida muz bor.",
    },
}


def _format_value(feature_name: str, value: float) -> str:
    """Pretty-print a raw feature value with its unit."""
    spec = FEATURE_INDEX[feature_name]
    if spec.kind == "boolean":
        return "mavjud" if value >= 0.5 else "yo'q"
    if spec.unit == "/10":
        return f"{value:.0f}/10"
    if spec.unit == "%":
        return f"{value:.0f}%"
    if spec.unit == "°C":
        return f"{value:.0f}°C"
    if spec.unit == "mm":
        return f"{value:.0f} mm"
    return f"{value:.1f}"


def generate_reasons(
    vector: Mapping[str, float],
    profile: Profile,
    planet: str,
    top_n: int = 5,
) -> list[dict]:
    """Return the ``top_n`` most influential reasons as dictionaries.

    Each item: ``{feature, category, text, contribution_pct}``.

    Complexity: O(F log F).
    """
    if planet not in ("moon", "mars"):
        raise ValueError(f"unknown planet: {planet!r}")
    if top_n <= 0:
        return []

    contributions = feature_contributions(vector, profile)
    ordered = [name for name in contributions if contributions[name] > 0]
    if not ordered:
        return []

    results: list[dict] = []
    for name in ordered[:top_n]:
        spec = FEATURE_INDEX[name]
        raw_value = float(vector.get(name, spec.min_value))

        if name not in profile:
            continue
        ideal_raw = float(profile[name][0])

        delta = signed_delta(vector, profile, name)
        if abs(delta) <= CLOSE_THRESHOLD:
            direction = "close"
        elif delta > 0:
            direction = "high"
        else:
            direction = "low"

        template = REASON_TEMPLATES.get((planet, name), {}).get(direction)
        if template is None:
            continue

        text = template.format(
            value=_format_value(name, raw_value),
            ideal=_format_value(name, ideal_raw),
        )

        results.append(
            {
                "feature": name,
                "category": FEATURE_CATEGORY.get(name, "general"),
                "text": text,
                "contribution_pct": round(contributions[name] * 100.0, 2),
            }
        )

    return results
