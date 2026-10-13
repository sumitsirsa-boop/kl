"""Timeline for the 3-ticket COMBO offer video (Sumit Lottery Agency, Mansa).

Line and word times come from ElevenLabs Scribe alignment of assets/combo/voiceover.mp3.
Build with:  python3 video/build_audio.py --project combo && python3 video/render.py --project combo
"""

FPS = 30
W, H = 1080, 1920
DURATION = 84.5

OUTPUT_FILE = "sumit_lottery_combo_offer.mp4"
BUILD_NAME = "combo"
VOICE_CLIPS = [(0.0, "combo/voiceover.mp3", 0.0, None)]

# Festive red/gold look, like the combo poster
BG_COLORS = ((70, 0, 18), (150, 16, 32), (60, 0, 38))
RAY_COLOR = (255, 200, 70)
HEADER_SPAN = (5.9, 60.0)
BIG_MODE = [(0.0, 5.9), (60.1, DURATION)]
SHAKES = ((5.4, 14), (14.5, 10), (26.3, 10), (37.7, 14), (56.4, 16))
BOOST_SCENES = ("price",)
CAPTION_BOTTOM = 1858

LINES = [
    (0.15, 1.36, "धमाकेदार ऑफ़र!"),
    (1.48, 5.76, "सुमित लॉटरी एजेंसी, मानसा लेकर आए हैं — तीन ज़बरदस्त टिकटों का कॉम्बो!"),
    (6.00, 9.68, "एक ही कॉम्बो में — तीन करोड़पति बनने के मौके!"),
    (9.78, 13.44, "पहला टिकट — नागालैंड स्टेट डियर पूजा बम्पर।"),
    (13.48, 15.52, "फ़र्स्ट प्राइज़ — ₹3 करोड़!"),
    (15.76, 20.16, "ड्रॉ — 24 अक्टूबर, शाम 6 बजे। टिकट — ₹500"),
    (20.60, 25.04, "दूसरा टिकट — पंजाब स्टेट डियर 200 मंथली लॉटरी।"),
    (25.08, 27.28, "फ़र्स्ट प्राइज़ — ₹1.50 करोड़!"),
    (27.52, 31.92, "ड्रॉ — 7 नवंबर, शाम 6 बजे। टिकट — ₹200"),
    (32.19, 35.92, "और तीसरा — पंजाब स्टेट डियर दिवाली बम्पर।"),
    (36.08, 38.80, "फ़र्स्ट प्राइज़ — पूरे ₹12 करोड़!"),
    (39.08, 43.52, "ड्रॉ — 16 नवंबर, शाम 6 बजे। टिकट — ₹500"),
    (44.44, 47.68, "सबसे खास बात — तीनों में फ़र्स्ट प्राइज़ गारंटीड है!"),
    (47.84, 51.52, "यानी पहला इनाम सिर्फ़ बिके हुए टिकटों में से ही निकाला जाएगा।"),
    (51.80, 54.80, "तीनों टिकटों की कीमत होती है ₹1200..."),
    (54.84, 57.84, "लेकिन कॉम्बो में — सिर्फ़ ₹1199!"),
    (58.03, 59.92, "और साथ में — फ़्री डिलीवरी!"),
    (60.16, 64.64, "अभी ऑर्डर करें — सुमित लॉटरी एजेंसी, वन वे ट्रैफ़िक रोड, मानसा।"),
    (64.92, 70.56, "कॉल या व्हाट्सऐप करें — 89688 69862"),
    (70.60, 75.84, "या फिर — 70598 77770"),
    (76.79, 80.08, "याद रखिए — लॉटरी में जोखिम है, ज़िम्मेदारी से खेलें।"),
    (80.16, 82.40, "18 साल से कम उम्र के लोगों के लिए नहीं।"),
]

# (scene name, start, ticket key) – the three ticket scenes share one renderer
SCENES = [
    ("intro", 0.0),
    ("hook", 5.9),
    ("ticket1", 9.7),
    ("ticket2", 20.5),
    ("ticket3", 32.1),
    ("guarantee", 43.9),
    ("price", 51.7),
    ("contact", 60.1),
    ("responsible", 76.6),
]

CONTACT_POPUPS = [17.2, 29.0, 40.4]


def scene_at(t):
    name, start = SCENES[0]
    end = DURATION
    for i, (n, s) in enumerate(SCENES):
        if t >= s:
            name, start = n, s
            end = SCENES[i + 1][1] if i + 1 < len(SCENES) else DURATION
    return name, start, end


SFX = [
    (0.00, "boom", 0.9), (0.10, "rocket", 0.6), (0.20, "sparkle", 0.5),
    (1.50, "whoosh", 0.5), (4.10, "whoosh", 0.6), (5.40, "crash", 0.8), (5.40, "boom", 0.9), (5.6, "coins", 0.6),
    (5.90, "whoosh", 0.7), (6.10, "pop", 0.8), (6.35, "pop", 0.8), (6.60, "pop", 0.8), (7.70, "ding", 0.7),
] + [x for s, prize, date, price in ((9.7, 13.6, 16.6, 19.4), (20.5, 25.1, 28.3, 31.2), (32.1, 36.1, 39.8, 42.8))
     for x in ((s, "whoosh", 0.8), (s + 0.4, "sparkle", 0.6), (prize, "boom", 0.8), (prize, "coins", 0.6),
               (prize + 0.1, "ding", 0.6), (date, "page", 0.7), (date + 0.2, "tick", 0.5), (price, "cash", 0.8))] + [
    (37.7, "rocket", 0.6), (37.9, "crash", 0.6),
    (43.90, "whoosh", 0.7), (46.90, "stamp", 0.9), (47.15, "stamp", 0.9), (47.40, "stamp", 0.9), (48.30, "ding", 0.7),
    (51.70, "whoosh", 0.7), (52.30, "pop", 0.7), (52.70, "pop", 0.7), (53.10, "pop", 0.7), (53.70, "cash", 0.7),
    (54.85, "whoosh", 0.5), (55.20, "drumroll", 0.7), (56.40, "crash", 0.9), (56.40, "boom", 1.0),
    (56.50, "coins", 0.7), (56.60, "rocket", 0.5), (58.90, "whoosh", 0.7), (59.30, "notify", 0.7),
    (60.10, "whoosh", 0.7), (60.30, "bell", 0.6), (61.50, "pop", 0.8),
    (66.70, "notify", 0.8), (71.30, "notify", 0.8),
    (76.60, "whoosh", 0.5), (77.00, "chime", 0.6), (80.20, "pop", 0.7), (82.60, "sparkle", 0.6),
] + [(t, "whoosh", 0.35) for t in CONTACT_POPUPS]
