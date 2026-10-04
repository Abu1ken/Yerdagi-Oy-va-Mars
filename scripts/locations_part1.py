"""Seed data (part 1 of 2): 15 real Earth locations used as Moon/Mars analogs.

Every entry is a plain dict consumed by :mod:`scripts.seed`.  Values are rounded
literature averages; entries whose numbers are approximations rather than direct
measurements set ``"estimated": True`` so the UI can show a disclaimer.
``source_url`` always points at a NASA / USGS / scientific reference.
"""

from __future__ import annotations

LOCATIONS_1: list[dict] = [
    {
        "name": "Atacama Desert",
        "country": "Chile",
        "lat": -23.5,
        "lon": -69.2,
        "type": "desert",
        "elevation_m": 2400.0,
        "description": (
            "Dunyodagi eng qurg'oqchil cho'l; ayrim hududlarda yillik yog'in 1-3 mm, "
            "tuproq temir oksidiga boy va o'ta tuzli. Marsdagi quruq, oksidlangan "
            "yuzaning eng mashhur Yerdagi analogi."
        ),
        "source_url": "https://earthobservatory.nasa.gov/images/88643/atacama-desert",
        "estimated": False,
        "features": {
            "avg_temp_c": 15.0, "temp_range_c": 25.0, "annual_rainfall_mm": 3.0,
            "humidity_pct": 10.0, "terrain_roughness": 6, "iron_oxide_level": 8,
            "basalt_level": 6, "radiation_level": 9, "dust_level": 8,
            "lava_tubes": False, "ice_presence": False,
        },
        "reasons": [
            {"planet": "mars", "category": "water",
             "text": "Yillik yog'in 3 mm dan kam — Marsning deyarli suvsiz yuzasi bilan mos keladi."},
            {"planet": "mars", "category": "chemistry",
             "text": "Tuproqdagi yuqori temir oksidi Marsning qizil regolitiga o'xshaydi."},
            {"planet": "moon", "category": "radiation",
             "text": "Yuqori balandlik va quruq havo yupqa asteroid muhitga o'xshash radiatsiya rejimini beradi."},
        ],
    },
    {
        "name": "Mojave Desert",
        "country": "USA",
        "lat": 35.0,
        "lon": -115.5,
        "type": "desert",
        "elevation_m": 800.0,
        "description": (
            "Kaliforniya janubi-sharqidagi quruq cho'l; NASA JPL va Mars roverlar sinov "
            "maydonlari shu hududda joylashgan."
        ),
        "source_url": "https://www.usgs.gov/places/mojave-desert",
        "estimated": True,
        "features": {
            "avg_temp_c": 18.0, "temp_range_c": 30.0, "annual_rainfall_mm": 150.0,
            "humidity_pct": 25.0, "terrain_roughness": 6, "iron_oxide_level": 7,
            "basalt_level": 6, "radiation_level": 8, "dust_level": 7,
            "lava_tubes": False, "ice_presence": False,
        },
        "reasons": [
            {"planet": "mars", "category": "geology",
             "text": "Toshloq, quruq relyef Mars roverlarining sinov muhitiga o'xshaydi."},
        ],
    },
    {
        "name": "Devon Island (Haughton Crater)",
        "country": "Canada",
        "lat": 75.4,
        "lon": -89.8,
        "type": "crater",
        "elevation_m": 200.0,
        "description": (
            "Kanada Arktikasidagi Devon oroli — muzliksiz qutb cho'li va Haughton zarba "
            "krateri; Mars Society va NASA analog tadqiqotlarining asosiy maydoni."
        ),
        "source_url": "https://www.nasa.gov/analogs/devon-island/",
        "estimated": True,
        "features": {
            "avg_temp_c": -15.0, "temp_range_c": 40.0, "annual_rainfall_mm": 200.0,
            "humidity_pct": 60.0, "terrain_roughness": 7, "iron_oxide_level": 6,
            "basalt_level": 6, "radiation_level": 8, "dust_level": 5,
            "lava_tubes": False, "ice_presence": True,
        },
        "reasons": [
            {"planet": "mars", "category": "temperature",
             "text": "Sovuq qutb cho'li va zarba krateri Marsning shimoliy hududlariga o'xshaydi."},
            {"planet": "mars", "category": "water",
             "text": "Yog'in kam, suv asosan muz shaklida — Mars muz-analoglariga mos."},
        ],
    },
    {
        "name": "Kilauea Volcano",
        "country": "USA",
        "lat": 19.42,
        "lon": -155.29,
        "type": "volcano",
        "elevation_m": 1247.0,
        "description": (
            "Gavayi orolida joylashgan dunyodagi eng faol vulqonlardan biri; bazalt lava "
            "oqimlari va lava quvurlari Oy mare bazaltlariga yaqin."
        ),
        "source_url": "https://www.usgs.gov/volcanoes/kilauea",
        "estimated": False,
        "features": {
            "avg_temp_c": 20.0, "temp_range_c": 15.0, "annual_rainfall_mm": 1500.0,
            "humidity_pct": 80.0, "terrain_roughness": 7, "iron_oxide_level": 7,
            "basalt_level": 10, "radiation_level": 6, "dust_level": 4,
            "lava_tubes": True, "ice_presence": False,
        },
        "reasons": [
            {"planet": "moon", "category": "geology",
             "text": "Bazalt lava ko'llari va quvurlari Oy mare bazaltlariga o'xshaydi."},
            {"planet": "mars", "category": "structure",
             "text": "Faol lava naylari Marsdagi yashash uchun potentsial lava naylarining analogi."},
        ],
    },
    {
        "name": "Mauna Kea",
        "country": "USA",
        "lat": 19.82,
        "lon": -155.47,
        "type": "volcano",
        "elevation_m": 4205.0,
        "description": (
            "Gavayi orolidagi so'ngan vulqon; troposferadan yuqori balandligi tufayli "
            "yupqa atmosfera sharoiti Oy/Mars misollarida o'rganilgan."
        ),
        "source_url": "https://www.usgs.gov/volcanoes/mauna-kea",
        "estimated": True,
        "features": {
            "avg_temp_c": 5.0, "temp_range_c": 20.0, "annual_rainfall_mm": 400.0,
            "humidity_pct": 55.0, "terrain_roughness": 7, "iron_oxide_level": 6,
            "basalt_level": 9, "radiation_level": 8, "dust_level": 5,
            "lava_tubes": False, "ice_presence": True,
        },
        "reasons": [
            {"planet": "moon", "category": "radiation",
             "text": "Balandlik oshgani sayin radiatsiya ortadi — Oy yuzasiga yaqin rejim."},
            {"planet": "mars", "category": "temperature",
             "text": "O'rtacha harorat 5 °C va quruq havo sovuq Mars kunlariga o'xshaydi."},
        ],
    },
    {
        "name": "Askja Caldera",
        "country": "Iceland",
        "lat": 65.03,
        "lon": -16.75,
        "type": "volcano",
        "elevation_m": 1100.0,
        "description": (
            "Islandiyadagi kaldera; chang bo'ronlari va bazalt relyefi tufayli 1960-yillarda "
            "Apollo astronavtlari mashq qilgan joylardan biri."
        ),
        "source_url": "https://www.usgs.gov/volcanoes/askja",
        "estimated": True,
        "features": {
            "avg_temp_c": -3.0, "temp_range_c": 20.0, "annual_rainfall_mm": 500.0,
            "humidity_pct": 75.0, "terrain_roughness": 6, "iron_oxide_level": 5,
            "basalt_level": 9, "radiation_level": 6, "dust_level": 3,
            "lava_tubes": False, "ice_presence": True,
        },
        "reasons": [
            {"planet": "moon", "category": "geology",
             "text": "Bazalt lava maydonlari va kaldera tuzilishi Oy marelariga o'xshaydi."},
        ],
    },
    {
        "name": "Dallol",
        "country": "Ethiopia",
        "lat": 14.24,
        "lon": 40.30,
        "type": "volcano",
        "elevation_m": -48.0,
        "description": (
            "Dunyodagi eng issiq joylardan biri; kislotali tuz ko'llari, oltingugurt va "
            "temir konlariga boy gidrotermal maydon — Marsdagi gidrotermal muhit analogi."
        ),
        "source_url": "https://earthobservatory.nasa.gov/images/91942/dallol-ethiopia",
        "estimated": True,
        "features": {
            "avg_temp_c": 34.0, "temp_range_c": 20.0, "annual_rainfall_mm": 100.0,
            "humidity_pct": 30.0, "terrain_roughness": 5, "iron_oxide_level": 7,
            "basalt_level": 8, "radiation_level": 6, "dust_level": 6,
            "lava_tubes": False, "ice_presence": False,
        },
        "reasons": [
            {"planet": "mars", "category": "chemistry",
             "text": "Kislotali tuz va temir birikmalari Marsdagi gidrotermal konlar analogni eslatadi."},
        ],
    },
    {
        "name": "Rio Tinto",
        "country": "Spain",
        "lat": 37.69,
        "lon": -6.61,
        "type": "other",
        "elevation_m": 100.0,
        "description": (
            "Qizil, temir oksidiga to'yingan kislotali daryo; astrobiologik tadqiqotlarda "
            "Marsning o'tmishdagi suvli muhiti analogi sifatida o'rganiladi."
        ),
        "source_url": "https://astrobiology.nasa.gov/news/rio-tinto-a-mars-analog/",
        "estimated": True,
        "features": {
            "avg_temp_c": 17.0, "temp_range_c": 25.0, "annual_rainfall_mm": 550.0,
            "humidity_pct": 55.0, "terrain_roughness": 5, "iron_oxide_level": 9,
            "basalt_level": 4, "radiation_level": 6, "dust_level": 5,
            "lava_tubes": False, "ice_presence": False,
        },
        "reasons": [
            {"planet": "mars", "category": "chemistry",
             "text": "Temir oksidi darajasi 9/10 — Marsning qizil tuprog'iga kuchli o'xshashlik."},
        ],
    },
    {
        "name": "Cueva de los Verdes (Lanzarote Lava Tubes)",
        "country": "Spain",
        "lat": 29.05,
        "lon": -13.65,
        "type": "cave",
        "elevation_m": 350.0,
        "description": (
            "Lanzarote orolidagi uzun lava quvurlari; ESA astronavtlar tayyorgarligi "
            "(PANGEA) va Mars lava naylari tadqiqotlari uchun ishlatiladi."
        ),
        "source_url": "https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/CAVES",
        "estimated": True,
        "features": {
            "avg_temp_c": 20.0, "temp_range_c": 12.0, "annual_rainfall_mm": 120.0,
            "humidity_pct": 60.0, "terrain_roughness": 4, "iron_oxide_level": 6,
            "basalt_level": 9, "radiation_level": 5, "dust_level": 3,
            "lava_tubes": True, "ice_presence": False,
        },
        "reasons": [
            {"planet": "mars", "category": "structure",
             "text": "Yer osti lava quvurlari Marsdagi lava naylariga bevosita o'xshaydi."},
            {"planet": "moon", "category": "structure",
             "text": "Yopiq lava quvurlari Oy lava naylari analogi hisoblanadi."},
        ],
    },
    {
        "name": "Antarctic Dry Valleys",
        "country": "Antarctica",
        "lat": -77.5,
        "lon": 161.5,
        "type": "desert",
        "elevation_m": 800.0,
        "description": (
            "Antarktidaning muzliksiz qutb cho'llari; Yerdagi eng sovuq va quruq cho'l bo'lib, "
            "NASA tomonidan Mars yuzasining eng yaqin analoglaridan biri deb tan olingan."
        ),
        "source_url": "https://www.nasa.gov/analogs/mcmurdo-dry-valleys/",
        "estimated": True,
        "features": {
            "avg_temp_c": -20.0, "temp_range_c": 25.0, "annual_rainfall_mm": 20.0,
            "humidity_pct": 30.0, "terrain_roughness": 6, "iron_oxide_level": 6,
            "basalt_level": 6, "radiation_level": 8, "dust_level": 6,
            "lava_tubes": False, "ice_presence": True,
        },
        "reasons": [
            {"planet": "mars", "category": "temperature",
             "text": "O'rtacha harorat -20 °C va quruq shamollar Marsning sovuq cho'llariga o'xshaydi."},
            {"planet": "mars", "category": "water",
             "text": "Yog'in deyarli yo'q, suv asosan muz shaklida — Mars qutb analoglariga mos."},
        ],
    },
    {
        "name": "Danakil Depression",
        "country": "Ethiopia",
        "lat": 13.5,
        "lon": 40.5,
        "type": "desert",
        "elevation_m": -125.0,
        "description": (
            "Tektonik cho'kish natijasida hosil bo'lgan tuz cho'li; dunyodagi eng past va "
            "eng issiq quruqliklardan biri, Mars tuz konlari analogi."
        ),
        "source_url": "https://earthobservatory.nasa.gov/images/87470/danakil-depression-ethiopia",
        "estimated": True,
        "features": {
            "avg_temp_c": 35.0, "temp_range_c": 20.0, "annual_rainfall_mm": 100.0,
            "humidity_pct": 35.0, "terrain_roughness": 5, "iron_oxide_level": 7,
            "basalt_level": 8, "radiation_level": 6, "dust_level": 6,
            "lava_tubes": False, "ice_presence": False,
        },
        "reasons": [
            {"planet": "mars", "category": "chemistry",
             "text": "Keng tuz va sulfat konlari Marsdagi tuz cho'kmalariga o'xshaydi."},
        ],
    },
    {
        "name": "Wadi Rum",
        "country": "Jordan",
        "lat": 29.58,
        "lon": 35.42,
        "type": "desert",
        "elevation_m": 900.0,
        "description": (
            "Qizil qumtosh va granit qoyalardan iborat cho'l vodiysi; Marsdagi qizil yuzani "
            "eslatishi sababli ko'plab analog-missiyalarda ishlatiladi."
        ),
        "source_url": "https://www.nasa.gov/analogs/wadi-rum/",
        "estimated": True,
        "features": {
            "avg_temp_c": 22.0, "temp_range_c": 30.0, "annual_rainfall_mm": 60.0,
            "humidity_pct": 25.0, "terrain_roughness": 7, "iron_oxide_level": 7,
            "basalt_level": 5, "radiation_level": 7, "dust_level": 7,
            "lava_tubes": False, "ice_presence": False,
        },
        "reasons": [
            {"planet": "mars", "category": "chemistry",
             "text": "Qizil qumtosh va temir oksidi Mars yuzasining rangiga o'xshaydi."},
            {"planet": "mars", "category": "geology",
             "text": "Yotiq qatlamli qoyalar Marsdagi cho'kindi tuzilmalarga o'xshaydi."},
        ],
    },
    {
        "name": "Lut Desert",
        "country": "Iran",
        "lat": 30.3,
        "lon": 59.2,
        "type": "desert",
        "elevation_m": 300.0,
        "description": (
            "Yerda qayd etilgan eng issiq sirt harorati (~70.7 °C) kuzatilgan qum cho'li; "
            "kalta (yardang) relyefi Mars relyefiga o'xshaydi."
        ),
        "source_url": "https://earthobservatory.nasa.gov/images/89049/lut-desert-iran",
        "estimated": True,
        "features": {
            "avg_temp_c": 28.0, "temp_range_c": 45.0, "annual_rainfall_mm": 50.0,
            "humidity_pct": 20.0, "terrain_roughness": 6, "iron_oxide_level": 7,
            "basalt_level": 5, "radiation_level": 8, "dust_level": 9,
            "lava_tubes": False, "ice_presence": False,
        },
        "reasons": [
            {"planet": "mars", "category": "dust",
             "text": "Kuchli chang rejimi va yardang relyefi Marsdagi chang bo'ronlariga o'xshaydi."},
            {"planet": "moon", "category": "temperature",
             "text": "Harorat tebranishi 45 °C — jazirama kunduz sovuq kechaga o'tadi."},
        ],
    },
    {
        "name": "Tolbachik (Kamchatka)",
        "country": "Russia",
        "lat": 55.83,
        "lon": 160.33,
        "type": "volcano",
        "elevation_m": 3682.0,
        "description": (
            "Kamchatkadagi bazalt vulqonlar guruhi; keng lava maydonlari va kul qatlamlari "
            "Oy mare bazaltlariga yaqin analog hisoblanadi."
        ),
        "source_url": "https://www.usgs.gov/volcanoes/tolbachik",
        "estimated": True,
        "features": {
            "avg_temp_c": -4.0, "temp_range_c": 25.0, "annual_rainfall_mm": 900.0,
            "humidity_pct": 80.0, "terrain_roughness": 8, "iron_oxide_level": 6,
            "basalt_level": 10, "radiation_level": 6, "dust_level": 4,
            "lava_tubes": False, "ice_presence": True,
        },
        "reasons": [
            {"planet": "moon", "category": "geology",
             "text": "Bazalt darajasi 10/10 — Oy mare bazalt tekisliklariga juda yaqin."},
            {"planet": "moon", "category": "geology",
             "text": "Keng lava maydonlari Oy marelarining yer usti analogi."},
        ],
    },
    {
        "name": "Mount Etna",
        "country": "Italy",
        "lat": 37.75,
        "lon": 14.99,
        "type": "volcano",
        "elevation_m": 3357.0,
        "description": (
            "Yevropaning eng faol vulqoni; ESA astronavtlari uchun tayyorgarlik maydoni va "
            "bazalt relyefi tufayli Oy/Mars analogi."
        ),
        "source_url": "https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/Etna",
        "estimated": True,
        "features": {
            "avg_temp_c": 8.0, "temp_range_c": 20.0, "annual_rainfall_mm": 700.0,
            "humidity_pct": 70.0, "terrain_roughness": 8, "iron_oxide_level": 6,
            "basalt_level": 9, "radiation_level": 6, "dust_level": 4,
            "lava_tubes": False, "ice_presence": True,
        },
        "reasons": [
            {"planet": "moon", "category": "geology",
             "text": "Bazalt oqimlar va kul qatlamlari Oy yuzasining tuzilishiga o'xshaydi."},
        ],
    },
]
