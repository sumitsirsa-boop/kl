"""Timeline for the Punjab State Dear Diwali Bumper 2026 video.

Line and word times come from ElevenLabs Scribe alignment of assets/diwali/voiceover.mp3.
Build with:  python3 video/build_audio.py --project diwali && python3 video/render.py --project diwali
"""

FPS = 30
W, H = 1080, 1920
DURATION = 97.5

OUTPUT_FILE = "punjab_dear_diwali_bumper_2026.mp4"
BUILD_NAME = "diwali"
VOICE_CLIPS = [(0.0, "diwali/voiceover.mp3", 0.0, None)]

# Diwali night look: deep maroon/purple with gold rays
BG_COLORS = ((45, 6, 45), (120, 22, 60), (70, 10, 80))
RAY_COLOR = (255, 190, 70)
HEADER_SPAN = (5.55, 86.8)
BIG_MODE = [(0.0, 5.55), (70.7, DURATION)]
SHAKES = ((17.05, 20), (9.75, 10), (19.0, 12), (20.1, 10))
BOOST_SCENES = ("jackpot",)
CAPTION_BOTTOM = 1858  # leaves room for the agency ticker at the very bottom

LINES = [
    (0.14, 1.36, "नमस्कार दोस्तों!"),
    (1.40, 5.52, "दिवाली आ रही है, और इस दिवाली किस्मत चमकाने का सबसे बड़ा मौका!"),
    (5.60, 9.44, "पेश है — पंजाब स्टेट डियर दिवाली बम्पर 2026!"),
    (9.72, 12.72, "ये है पंजाब सरकार की ऑफिशियल लॉटरी।"),
    (12.76, 16.96, "पंजाब लॉटरी के इतिहास में, पहली बार इतना बड़ा इनाम रखा गया है..."),
    (17.10, 20.00, "फ़र्स्ट प्राइज़ — पूरे ₹12 करोड़!"),
    (20.02, 20.96, "वो भी गारंटीड!"),
    (21.17, 25.76, "और ध्यान दीजिए — फ़र्स्ट प्राइज़ सिर्फ़ बिके हुए टिकटों में से ही निकाला जाएगा।"),
    (25.98, 30.88, "इसका ड्रॉ होगा — 16 नवंबर 2026 को, शाम 6 बजे से।"),
    (31.09, 33.92, "और टिकट की MRP है — सिर्फ़ ₹500"),
    (34.19, 36.96, "इस बार टिकट 12 राशियों में जारी किया गया है —"),
    (37.16, 45.68, "मेष, वृषभ, मिथुन, कर्क, सिंह, कन्या, तुला, वृश्चिक, धनु, मकर, कुंभ और मीन।"),
    (45.97, 50.64, "हर राशि में 3 लाख टिकट, यानी कुल 36 लाख टिकट।"),
    (50.68, 53.52, "सेकंड प्राइज़ — ₹1-1 करोड़ के 3 इनाम।"),
    (53.73, 57.44, "और थर्ड प्राइज़ — ₹50-50 लाख के 3 इनाम।"),
    (57.76, 61.44, "साथ में 11 कंसोलेशन प्राइज़, ₹10-10 लाख के।"),
    (61.65, 65.68, "और 9वें रैंक तक, कुल 1,90,000 से भी ज़्यादा इनाम!"),
    (66.04, 70.56, "ड्रॉ लाइव देखिए — punjablotteries.com/livedraw पर।"),
    (70.88, 76.00, "टिकट खरीदने के लिए पहुँचिए — सुमित लॉटरी एजेंसी, वन वे ट्रैफ़िक रोड, मानसा!"),
    (76.36, 81.84, "संपर्क करें — 70598 77770"),
    (82.04, 86.56, "या फिर — 89688 69862 पर।"),
    (87.47, 90.64, "याद रखिए — लॉटरी में जोखिम है, ज़िम्मेदारी से खेलें।"),
    (90.88, 93.44, "आप सभी को दिवाली की ढेरों शुभकामनाएँ!"),
    (93.72, 95.76, "वीडियो को लाइक और शेयर ज़रूर करें!"),
]

# When each rashi name is spoken
RASHI_TIMES = [37.44, 37.96, 38.68, 39.49, 40.08, 40.72, 41.56, 42.32, 43.15, 43.92, 44.52, 45.28]

SCENES = [
    ("intro", 0.0),
    ("ticket", 5.55),
    ("history", 12.70),
    ("jackpot", 17.00),
    ("sold", 21.10),
    ("draw_date", 25.90),
    ("mrp", 31.00),
    ("rashi", 34.10),
    ("total", 45.90),
    ("prizes", 50.60),
    ("consolation", 57.60),
    ("live", 65.90),
    ("contact", 70.70),
    ("responsible", 86.90),
    ("outro", 90.80),
]

# Lower-third pop-ups with the agency's name and numbers, between the main beats
CONTACT_POPUPS = [13.0, 31.4, 46.3, 66.3]
CONTACT_START = 70.88  # used by the shared contact scene


def scene_at(t):
    name, start = SCENES[0]
    end = DURATION
    for i, (n, s) in enumerate(SCENES):
        if t >= s:
            name, start = n, s
            end = SCENES[i + 1][1] if i + 1 < len(SCENES) else DURATION
    return name, start, end


SFX = [
    (0.00, "boom", 0.8), (0.15, "rocket", 0.6), (1.90, "rocket", 0.5), (3.40, "rocket", 0.5), (0.4, "sparkle", 0.5),
    (5.55, "whoosh", 0.8), (6.10, "sparkle", 0.6),
    (9.75, "stamp", 1.0),
    (12.70, "whoosh", 0.6), (13.30, "bell", 0.6),
    (15.20, "drumroll", 0.8),
    (17.05, "crash", 0.9), (17.05, "boom", 1.0), (17.20, "counter", 0.5), (17.30, "coins", 0.7),
    (17.30, "rocket", 0.6), (18.10, "rocket", 0.5), (19.00, "ding", 0.8), (20.10, "stamp", 1.0),
    (21.10, "whoosh", 0.7), (23.40, "stamp", 0.6), (23.70, "stamp", 0.6), (24.00, "stamp", 0.6), (25.00, "ding", 0.7),
    (25.90, "whoosh", 0.6), (26.20, "page", 0.7), (26.50, "page", 0.7), (26.80, "page", 0.7), (27.70, "ding", 0.7),
    (29.70, "tick", 0.5), (30.10, "tick", 0.5), (30.50, "tick", 0.5),
    (31.00, "whoosh", 0.7), (32.30, "cash", 0.9),
    (34.10, "whoosh", 0.7), (34.40, "chime", 0.6),
] + [(t, "pop", 0.7) for t in RASHI_TIMES] + [
    (45.90, "whoosh", 0.6), (47.20, "counter", 0.4), (48.90, "ding", 0.8),
    (50.60, "whoosh", 0.7), (51.10, "ding", 0.6), (53.70, "whoosh", 0.7), (54.30, "ding", 0.6),
    (57.60, "whoosh", 0.7),
] + [(58.4 + i * 0.09, "pop", 0.4) for i in range(11)] + [
    (61.60, "whoosh", 0.5),
] + [(61.9 + i * 0.2, "click", 0.5) for i in range(10)] + [
    (64.00, "ding", 0.7),
    (65.90, "whoosh", 0.7), (66.30, "notify", 0.8), (66.80, "rattle", 0.5),
    (70.70, "whoosh", 0.7), (70.90, "bell", 0.6), (71.20, "pop", 0.8), (73.0, "sparkle", 0.5),
    (76.40, "notify", 0.8), (82.05, "notify", 0.8),
    (86.90, "whoosh", 0.5), (87.30, "chime", 0.6),
    (90.80, "whoosh", 0.7), (90.90, "rocket", 0.6), (91.70, "rocket", 0.5), (92.60, "cracker", 0.6),
    (94.45, "click", 1.0), (94.55, "pop", 0.7), (95.45, "click", 1.0), (95.55, "pop", 0.7), (96.30, "sparkle", 0.7),
] + [(t, "whoosh", 0.35) for t in CONTACT_POPUPS]
