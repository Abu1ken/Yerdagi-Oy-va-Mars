"""Seed data (part 2 of 2): 15 more real Earth locations used as analogs."""

from __future__ import annotations

LOCATIONS_2: list[dict] = [
    {
        "name": "Lava Beds National Monument",
        "country": "USA",
        "lat": 41.71,
        "lon": -121.51,
        "type": "cave",
        "elevation_m": 1300.0,
        "description": (
            "Kaliforniyadagi 700 dan ortiq lava quvuridan iborat hudud; NASA tomonidan "
            "Mars/Oy lava naylari va g'or yashash muhiti analogi sifatida o'rganiladi."
        ),
        "source_url": "https://www.usgs.gov/volcanoes/lava-beds",
        "estimated": True,
        "features": {
            "avg_temp_c": 10.0, "temp_range_c": 25.0, "annual_rainfall_mm": 400.0,
            "humidity_pct": 50.0, "terrain_roughness": 5, "iron_oxide_level": 6,
            "basalt_level": 9, "radiation_level": 6, "dust_level": 4,
            "lava_tubes": True, "ice_presence": False,
        },
        "reasons": [
            {"planet": "mars", "category": "structure",
             "text": "Ko'plab lava quvurlari Mars lava naylari va yashash muammosi analogi."},
            {"planet": "moon", "category": "structure",
             "text": "Yer osti quvurlari Oy lava naylarining yer usti analogi."},
        ],
    },
    {
        "name": "Namib Desert",
        "country": "Namibia",
        "lat": -24.75,
        "lon": 15.3,
        "type": "desert",
        "elevation_m": 500.0,
        "description": (
            "Dunyodagi eng qadimiy cho'l; qizil qum konlari va temir oksidiga boy sirt "
            "Mars qumtepalari tadqiqotlarida analog sifatida ishlatiladi."
        ),
        "source_url": "https://earthobservatory.nasa.gov/images/147842/namib-desert",
        "estimated": True,
        "features": {
            "avg_temp_c": 22.0, "temp_range_c": 35.0, "annual_rainfall_mm": 20.0,
            "humidity_pct": 25.0, "terrain_roughness": 6, "iron_oxide_level": 8,
            "basalt_level": 5, "radiation_level": 8, "dust_level": 8,
            "lava_tubes": False, "ice_presence": False,
        },
        "reasons": [
            {"planet": "mars", "category": "dust",
             "text": "Temir oksidiga boy qizil qum va kuchli chang Mars qumtepalariga o'xshaydi."},
        ],
    },
    {
        "name": "Great Sand Sea",
        "country": "Egypt",
        "lat": 27.0,
        "lon": 26.0,
        "type": "desert",
        "elevation_m": 200.0,
        "description": (
            "Misrning g'arbiy qismidagi ulkan qumtepa maydoni; NASA tomonidan Marsdagi "
            "qumtepa morfologiyasini o'rganish uchun analog maydon sifatida tanlangan."
        ),
        "source_url": "https://earthobservatory.nasa.gov/images/4100/great-sand-sea-egypt",
        "estimated": True,
        "features": {
            "avg_temp_c": 25.0, "temp_range_c": 35.0, "annual_rainfall_mm": 5.0,
            "humidity_pct": 20.0, "terrain_roughness": 6, "iron_oxide_level": 8,
            "basalt_level": 5, "radiation_level": 9, "dust_level": 9,
            "lava_tubes": False, "ice_presence": False,
        },
        "reasons": [
            {"planet": "mars", "category": "geology",
             "text": "Uzun bo'ylama qumtepalar Mars qumtepa maydonlarining analogni."},
            {"planet": "mars", "category": "dust",
             "text": "Kam yog'in va kuchli chang Marsdagi chang bo'ronlariga o'xshaydi."},
        ],
    },
    {
        "name": "Death Valley",
        "country": "USA",
        "lat": 36.24,
        "lon": -116.83,
        "type": "desert",
        "elevation_m": -86.0,
        "description": (
            "Shimoliy Amerikadagi eng past va eng issiq joy; tuzli tekisliklar va quruq "
            "iqlim Mars cho'l analoglarida qo'llaniladi."
        ),
        "source_url": "https://www.usgs.gov/places/death-valley",
        "estimated": True,
        "features": {
            "avg_temp_c": 25.0, "temp_range_c": 40.0, "annual_rainfall_mm": 60.0,
            "humidity_pct": 25.0, "terrain_roughness": 7, "iron_oxide_level": 7,
            "basalt_level": 6, "radiation_level": 8, "dust_level": 7,
            "lava_tubes": False, "ice_presence": False,
        },
        "reasons": [
            {"planet": "mars", "category": "temperature",
             "text": "Katta kun-tun harorat tebranishi Marsning sutkalik rejimiga o'xshaydi."},
        ],
    },
    {
        "name": "Vatnajokull Ice Caves",
        "country": "Iceland",
        "lat": 64.4,
        "lon": -16.8,
        "type": "glacier",
        "elevation_m": 1000.0,
        "description": (
            "Yevropadagi eng katta muzlik ostidagi muz g'orlari; subglyatsial vulqonizm "
            "Mars va Yevropa muzlari tadqiqotlarida analog."
        ),
        "source_url": "https://earthobservatory.nasa.gov/images/144724/vatnajokull-iceland",
        "estimated": True,
        "features": {
            "avg_temp_c": -3.0, "temp_range_c": 20.0, "annual_rainfall_mm": 1200.0,
            "humidity_pct": 85.0, "terrain_roughness": 6, "iron_oxide_level": 4,
            "basalt_level": 8, "radiation_level": 5, "dust_level": 3,
            "lava_tubes": False, "ice_presence": True,
        },
        "reasons": [
            {"planet": "mars", "category": "water",
             "text": "Muz va subglyatsial suv Mars qutb muzliklari analogi."},
        ],
    },
    {
        "name": "Greenland Ice Sheet",
        "country": "Greenland",
        "lat": 72.0,
        "lon": -40.0,
        "type": "glacier",
        "elevation_m": 2500.0,
        "description": (
            "Dunyodagi ikkinchi eng katta muz qatlami; NASA Operation IceBridge va Mars "
            "qutb muzliklari tadqiqotlarida kalibrlash maydoni."
        ),
        "source_url": "https://www.nasa.gov/feature/goddard/2020/greenland-ice-sheet",
        "estimated": True,
        "features": {
            "avg_temp_c": -25.0, "temp_range_c": 30.0, "annual_rainfall_mm": 300.0,
            "humidity_pct": 70.0, "terrain_roughness": 4, "iron_oxide_level": 4,
            "basalt_level": 5, "radiation_level": 7, "dust_level": 4,
            "lava_tubes": False, "ice_presence": True,
        },
        "reasons": [
            {"planet": "mars", "category": "water",
             "text": "Keng muz qatlami va chang qatlamlari Mars qutb muzliklariga o'xshaydi."},
        ],
    },
    {
        "name": "Blood Falls (Taylor Glacier)",
        "country": "Antarctica",
        "lat": -77.72,
        "lon": 162.27,
        "type": "glacier",
        "elevation_m": 80.0,
        "description": (
            "Temirga boy tuzli suv muz ostidan chiqib, qizil rang beradi; Marsda suv va "
            "temir oksidi mavjudligi analogi sifatida o'rganiladi."
        ),
        "source_url": "https://astrobiology.nasa.gov/news/blood-falls/",
        "estimated": True,
        "features": {
            "avg_temp_c": -17.0, "temp_range_c": 25.0, "annual_rainfall_mm": 15.0,
            "humidity_pct": 40.0, "terrain_roughness": 5, "iron_oxide_level": 9,
            "basalt_level": 5, "radiation_level": 8, "dust_level": 5,
            "lava_tubes": False, "ice_presence": True,
        },
        "reasons": [
            {"planet": "mars", "category": "chemistry",
             "text": "Temir oksidi bilan bo'yalgan tuzli suv Marsdagi qizil konlarga o'xshaydi."},
        ],
    },
    {
        "name": "Mount Erebus",
        "country": "Antarctica",
        "lat": -77.53,
        "lon": 167.15,
        "type": "volcano",
        "elevation_m": 3794.0,
        "description": (
            "Yer yuzidagi eng janubiy faol vulqon; doimiy lava ko'li va muz bilan qoplangan "
            "qiyaliklari Oy/Mars ekstremal muhitlariga o'xshaydi."
        ),
        "source_url": "https://www.usgs.gov/volcanoes/erebus",
        "estimated": True,
        "features": {
            "avg_temp_c": -30.0, "temp_range_c": 25.0, "annual_rainfall_mm": 100.0,
            "humidity_pct": 55.0, "terrain_roughness": 8, "iron_oxide_level": 5,
            "basalt_level": 9, "radiation_level": 7, "dust_level": 5,
            "lava_tubes": False, "ice_presence": True,
        },
        "reasons": [
            {"planet": "moon", "category": "temperature",
             "text": "O'ta sovuq muhitda faol bazalt lava ko'li — Oy rejimiga yaqin."},
        ],
    },
    {
        "name": "Kawah Ijen",
        "country": "Indonesia",
        "lat": -8.06,
        "lon": 114.24,
        "type": "volcano",
        "elevation_m": 2799.0,
        "description": (
            "Oltingugurt va kislotali krater ko'li bilan mashhur vulqon; Marsdagi kislotali "
            "gidrotermal muhitlar analogi."
        ),
        "source_url": "https://earthobservatory.nasa.gov/images/86052/kawah-ijen-indonesia",
        "estimated": True,
        "features": {
            "avg_temp_c": 12.0, "temp_range_c": 15.0, "annual_rainfall_mm": 2000.0,
            "humidity_pct": 90.0, "terrain_roughness": 7, "iron_oxide_level": 6,
            "basalt_level": 8, "radiation_level": 5, "dust_level": 4,
            "lava_tubes": False, "ice_presence": False,
        },
        "reasons": [
            {"planet": "mars", "category": "chemistry",
             "text": "Kislotali krater ko'li va sulfat konlari Mars gidrotermal muhitiga o'xshaydi."},
        ],
    },
    {
        "name": "Pinacate Volcanic Field",
        "country": "Mexico",
        "lat": 31.79,
        "lon": -113.5,
        "type": "volcano",
        "elevation_m": 1200.0,
        "description": (
            "Ko'plab kraterlar va bazalt oqimlardan iborat vulqon maydoni; Apollo "
            "astronavtlari tomonidan mashq maydoni sifatida ishlatilgan."
        ),
        "source_url": "https://www.nasa.gov/analogs/pinacate/",
        "estimated": True,
        "features": {
            "avg_temp_c": 22.0, "temp_range_c": 30.0, "annual_rainfall_mm": 100.0,
            "humidity_pct": 30.0, "terrain_roughness": 7, "iron_oxide_level": 6,
            "basalt_level": 9, "radiation_level": 8, "dust_level": 7,
            "lava_tubes": True, "ice_presence": False,
        },
        "reasons": [
            {"planet": "moon", "category": "geology",
             "text": "Kraterlar maydoni va bazalt oqimlari Oy yuzasining analogni."},
            {"planet": "mars", "category": "geology",
             "text": "Yupqa bazalt qatlamlari Mars vulqon tekisliklariga o'xshaydi."},
        ],
    },
    {
        "name": "Salar de Uyuni",
        "country": "Bolivia",
        "lat": -20.13,
        "lon": -67.49,
        "type": "other",
        "elevation_m": 3656.0,
        "description": (
            "Dunyodagi eng katta tuz tekisligi; o'ta tekis yuzasi radar/sensorlarni "
            "kalibrlashda va Mars tekisliklari analogiyasida ishlatiladi."
        ),
        "source_url": "https://earthobservatory.nasa.gov/images/48674/salar-de-uyuni-bolivia",
        "estimated": False,
        "features": {
            "avg_temp_c": 10.0, "temp_range_c": 25.0, "annual_rainfall_mm": 200.0,
            "humidity_pct": 40.0, "terrain_roughness": 3, "iron_oxide_level": 5,
            "basalt_level": 4, "radiation_level": 9, "dust_level": 6,
            "lava_tubes": False, "ice_presence": False,
        },
        "reasons": [
            {"planet": "mars", "category": "geology",
             "text": "O'ta tekis tuz qatlami Marsdagi cho'kindi tekisliklarga o'xshaydi."},
            {"planet": "moon", "category": "radiation",
             "text": "Balandlik va tiniq havo yuqori radiatsiya rejimini beradi."},
        ],
    },
    {
        "name": "Tsingy de Bemaraha",
        "country": "Madagascar",
        "lat": -18.9,
        "lon": 44.8,
        "type": "other",
        "elevation_m": 300.0,
        "description": (
            "O'tkir karst ignalari (tsingy) bilan qoplangan relyef; o'ta notekis yuzasi "
            "Mars va Oy relyefining yer usti analogi."
        ),
        "source_url": "https://earthobservatory.nasa.gov/images/149814/tsingy-de-bemaraha-madagascar",
        "estimated": True,
        "features": {
            "avg_temp_c": 26.0, "temp_range_c": 15.0, "annual_rainfall_mm": 1000.0,
            "humidity_pct": 80.0, "terrain_roughness": 8, "iron_oxide_level": 4,
            "basalt_level": 4, "radiation_level": 6, "dust_level": 4,
            "lava_tubes": False, "ice_presence": False,
        },
        "reasons": [
            {"planet": "moon", "category": "geology",
             "text": "O'tkir karst ignalari Oy regolit relyefining notekisligini eslatadi."},
        ],
    },
    {
        "name": "Richat Structure (Eye of the Sahara)",
        "country": "Mauritania",
        "lat": 21.12,
        "lon": -11.4,
        "type": "crater",
        "elevation_m": 400.0,
        "description": (
            "Sahroi Kabirdagi konsentrik halqali struktura; zarba krateriga o'xshash "
            "morfologiyasi tufayli Mars/Oy krater tadqiqotlarida qo'llaniladi."
        ),
        "source_url": "https://earthobservatory.nasa.gov/images/92306/richat-structure-mauritania",
        "estimated": True,
        "features": {
            "avg_temp_c": 27.0, "temp_range_c": 30.0, "annual_rainfall_mm": 100.0,
            "humidity_pct": 25.0, "terrain_roughness": 5, "iron_oxide_level": 8,
            "basalt_level": 5, "radiation_level": 9, "dust_level": 9,
            "lava_tubes": False, "ice_presence": False,
        },
        "reasons": [
            {"planet": "moon", "category": "geology",
             "text": "Halqali struktura va og'ir chang sharoyiti Oy krater analoglariga o'xshaydi."},
            {"planet": "mars", "category": "chemistry",
             "text": "Temir oksidiga boy qizil qatlamlar Mars yuzasiga o'xshaydi."},
        ],
    },
    {
        "name": "Erta Ale",
        "country": "Ethiopia",
        "lat": 13.6,
        "lon": 40.67,
        "type": "volcano",
        "elevation_m": 613.0,
        "description": (
            "Uzoq vaqt saqlanib turuvchi lava ko'liga ega bazalt qalqonsimon vulqon; "
            "Mars/Oy bazalt lava rejimlarining analogi."
        ),
        "source_url": "https://earthobservatory.nasa.gov/images/88545/erta-ale-ethiopia",
        "estimated": True,
        "features": {
            "avg_temp_c": 33.0, "temp_range_c": 18.0, "annual_rainfall_mm": 100.0,
            "humidity_pct": 30.0, "terrain_roughness": 7, "iron_oxide_level": 7,
            "basalt_level": 10, "radiation_level": 6, "dust_level": 6,
            "lava_tubes": True, "ice_presence": False,
        },
        "reasons": [
            {"planet": "moon", "category": "geology",
             "text": "Bazalt lava ko'li Oy mare bazaltlariga yaqin analog."},
            {"planet": "mars", "category": "geology",
             "text": "Faol bazalt vulqonizm Marsning erta tarixidagi lava rejimini eslatadi."},
        ],
    },
    {
        "name": "White Desert (Farafra)",
        "country": "Egypt",
        "lat": 27.4,
        "lon": 28.1,
        "type": "desert",
        "elevation_m": 250.0,
        "description": (
            "Bo'r konlaridan hosil bo'lgan oq qoya shakllari bilan mashhur cho'l; Marsdagi "
            "oq gips/bo'r qatlamlari analogi."
        ),
        "source_url": "https://earthobservatory.nasa.gov/images/147997/farafra-oasis-egypt",
        "estimated": True,
        "features": {
            "avg_temp_c": 25.0, "temp_range_c": 35.0, "annual_rainfall_mm": 5.0,
            "humidity_pct": 20.0, "terrain_roughness": 5, "iron_oxide_level": 6,
            "basalt_level": 4, "radiation_level": 8, "dust_level": 8,
            "lava_tubes": False, "ice_presence": False,
        },
        "reasons": [
            {"planet": "mars", "category": "chemistry",
             "text": "Gips/bo'r konlari Marsdagi sulfat qatlamlariga o'xshaydi."},
        ],
    },
]
