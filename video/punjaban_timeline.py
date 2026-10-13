"""Timeline for the Diwali Bumper 2026 video presented by a Punjabi girl holding the ticket.

Line and word times come from ElevenLabs Scribe alignment of assets/punjaban/voiceover.mp3.
Build with:  python3 video/build_audio.py --project punjaban && python3 video/render.py --project punjaban
"""

FPS = 30
W, H = 1080, 1920
DURATION = 62.8

OUTPUT_FILE = "diwali_bumper_punjaban.mp4"
BUILD_NAME = "punjaban"
VOICE_CLIPS = [(0.0, "punjaban/voiceover.mp3", 0.0, None)]

# Warm phulkari look: magenta to marigold, soft rays
BG_COLORS = ((110, 8, 60), (196, 34, 92), (232, 110, 40))
RAY_COLOR = (255, 225, 120)
RAY_INTENSITY = 0.45
HEADER_SPAN = (99.0, 99.0)  # no header bar in this style
SHAKES = ((12.85, 16), (15.5, 10))
BOOST_SCENES = ("jackpot",)
CAPTION_BOTTOM = 1858

LINES = [
    (0.14, 1.12, "सत श्री अकाल जी!"),
    (1.16, 2.48, "की हाल ए सारेयाँ दा?"),
    (2.60, 6.64, "देखो, मेरे हाथ में है — इस दिवाली का सबसे वड्डा टिकट!"),
    (6.80, 10.00, "पंजाब स्टेट डियर दिवाली बम्पर 2026 —"),
    (10.36, 12.72, "पंजाब सरकार की ऑफिशियल लॉटरी।"),
    (12.84, 15.36, "फ़र्स्ट प्राइज़ — पूरे ₹12 करोड़!"),
    (15.40, 16.40, "ओ भी गारंटीड!"),
    (16.52, 20.08, "क्योंकि फ़र्स्ट प्राइज़ सिर्फ़ बिके हुए टिकटों में से ही निकलेगा।"),
    (20.16, 22.88, "सेकंड प्राइज़ — ₹1-1 करोड़ के 3 इनाम।"),
    (22.92, 26.08, "थर्ड प्राइज़ — ₹50-50 लाख के 3 इनाम।"),
    (26.13, 29.12, "और 11 कंसोलेशन प्राइज़ — ₹10-10 लाख के।"),
    (29.16, 32.56, "कुल मिलाकर — 1,90,000 से ज़्यादा इनाम!"),
    (32.68, 37.28, "टिकट 12 राशियों में मिलता है — अपनी राशि वाला टिकट चुनो, मेष हो या मीन!"),
    (37.44, 40.40, "ड्रॉ होगा — 16 नवंबर, शाम 6 बजे।"),
    (40.45, 42.48, "और टिकट सिर्फ़ — ₹500 का।"),
    (42.52, 43.84, "तो फिर देर किस गल दी?"),
    (43.92, 47.84, "आज ही पहुँचो — सुमित लॉटरी एजेंसी, वन वे ट्रैफ़िक रोड, मानसा।"),
    (47.92, 52.00, "कॉल करो — 89688 69862"),
    (52.04, 56.64, "या फिर — 70598 77770"),
    (56.76, 60.00, "ज़िम्मेदारी नाल खेलो, और दिवाली दियाँ लख-लख वधाइयाँ!"),
    (60.05, 60.80, "बल्ले बल्ले!"),
]

SCENES = [
    ("hello", 0.0),
    ("show", 2.55),
    ("name", 6.75),
    ("jackpot", 12.75),     # B-roll
    ("sold", 16.45),
    ("prizes", 20.05),      # B-roll
    ("total", 29.10),
    ("rashi", 32.60),       # B-roll
    ("date", 37.35),
    ("contact", 42.50),
    ("bye", 56.70),
]
BROLL_SCENES = ("jackpot", "prizes", "rashi")


def scene_at(t):
    name, start = SCENES[0]
    end = DURATION
    for i, (n, s) in enumerate(SCENES):
        if t >= s:
            name, start = n, s
            end = SCENES[i + 1][1] if i + 1 < len(SCENES) else DURATION
    return name, start, end


SFX = [
    (0.00, "bell", 0.6), (0.15, "pop", 0.8), (1.20, "pop", 0.7),
    (2.55, "whoosh", 0.6), (2.65, "pop", 0.8), (3.30, "sparkle", 0.6), (5.55, "pop", 0.8), (5.60, "ding", 0.5),
    (6.75, "whoosh", 0.6), (6.95, "pop", 0.7), (10.40, "stamp", 0.9),
    (12.75, "whoosh", 0.8), (12.85, "boom", 1.0), (12.85, "crash", 0.8), (13.0, "rocket", 0.6), (13.1, "coins", 0.7),
    (14.0, "rocket", 0.5), (15.50, "stamp", 1.0),
    (16.45, "whoosh", 0.7), (17.00, "pop", 0.7), (19.40, "check", 0.8),
    (20.05, "whoosh", 0.7), (20.30, "ding", 0.6), (23.00, "ding", 0.6), (26.30, "ding", 0.6),
] + [(26.9 + i * 0.09, "pop", 0.4) for i in range(11)] + [
    (29.10, "whoosh", 0.6), (29.30, "counter", 0.5), (31.0, "ding", 0.8),
    (32.60, "whoosh", 0.7), (32.80, "chime", 0.6), (36.32, "pop", 0.8), (37.04, "pop", 0.8),
    (37.35, "whoosh", 0.6), (37.60, "page", 0.7), (39.4, "tick", 0.5), (40.60, "cash", 0.8),
    (42.50, "whoosh", 0.6), (42.60, "pop", 0.7), (43.95, "pop", 0.8), (44.10, "sparkle", 0.5),
    (48.70, "notify", 0.8), (52.70, "notify", 0.8),
    (56.70, "whoosh", 0.6), (57.0, "chime", 0.5), (58.0, "rocket", 0.6), (58.9, "rocket", 0.5),
    (60.05, "dhol", 0.9), (60.40, "cracker", 0.6),
]
