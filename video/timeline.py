"""Shared timeline: voiceover lines with start/end times (seconds).

Times come from silence detection on assets/voiceover.mp3 (ElevenLabs take),
so captions, motion graphics and sound effects all line up with the speech.
"""

FPS = 30
W, H = 1080, 1920
# The agency contact line (assets/voiceover_contact.mp3) is spliced into the main
# voiceover at CONTACT_AT; everything after that point moves later by SHIFT.
CONTACT_AT = 69.75
CONTACT_LEAD = 0.25
CONTACT_LEN = 14.2
SHIFT = CONTACT_LEAD + CONTACT_LEN + 0.4
CONTACT_START = CONTACT_AT + CONTACT_LEAD
DURATION = 75.0 + SHIFT  # main voiceover is 73.36s, plus a short tail for the end card


def sh(t):
    return t + SHIFT if t >= CONTACT_AT else t


# (start, end, hindi caption)
_BASE_LINES = [
    (0.00, 0.90, "नमस्कार दोस्तों!"),
    (1.43, 5.12, "आज मैं आपको बताने वाला हूँ एक बहुत ही खास लॉटरी टिकट के बारे में।"),
    (5.75, 9.57, "ये है — पंजाब स्टेट डियर 1000 क्वार्टरली लॉटरी!"),
    (10.31, 13.77, "और ये लॉटरी है पंजाब सरकार की, यानी पूरी तरह ऑफिशियल।"),
    (14.57, 19.15, "इसका पाँचवाँ ड्रॉ होगा — 9 जनवरी 2027 को, शाम 7 बजे से।"),
    (19.81, 21.41, "और हाँ, लोहड़ी के मौके पर!"),
    (21.98, 24.75, "टिकट की MRP है — सिर्फ़ ₹1000"),
    (25.60, 26.77, "और अब सबसे बड़ी बात..."),
    (27.32, 29.89, "फ़र्स्ट प्राइज़ है — पूरे ₹50 लाख!"),
    (30.77, 32.25, "सेकंड प्राइज़ है ₹10 लाख।"),
    (32.63, 33.87, "और थर्ड प्राइज़ में,"),
    (34.25, 37.06, "40 विजेताओं को मिलेंगे ₹9,000 - ₹9,000"),
    (37.88, 41.25, "इसके साथ 3 कंसोलेशन प्राइज़, ₹5-5 लाख के।"),
    (41.86, 44.68, "और 8वें रैंक तक, कुल 2000 से ज़्यादा इनाम!"),
    (45.48, 50.78, "इस स्कीम में A, B, C और D — 4 सीरीज़ में, कुल 40,000 टिकट हैं।"),
    (51.72, 56.47, "ड्रॉ आप लाइव देख सकते हैं — punjablotteries.com/livedraw पर।"),
    (57.12, 62.34, "टिकट हमेशा ऑथराइज़्ड सेलर से ही खरीदें, और रिज़ल्ट पंजाब सरकार के गज़ट से ज़रूर चेक करें।"),
    (63.04, 65.04, "जीतने पर 30 दिन के अंदर क्लेम करें।"),
    (65.68, 69.31, "याद रखिए — लॉटरी में जोखिम है, इसलिए ज़िम्मेदारी से खेलें।"),
    (70.19, 73.36, "ऐसी ही जानकारी के लिए, वीडियो को लाइक और शेयर ज़रूर करें!"),
]

CONTACT_LINES = [
    (CONTACT_START + 0.00, CONTACT_START + 4.10, "टिकट खरीदने के लिए पहुँचिए — सुमित लॉटरी एजेंसी, वन वे ट्रैफ़िक रोड, मानसा!"),
    (CONTACT_START + 4.59, CONTACT_START + 9.01, "संपर्क करें — 70598 77770"),
    (CONTACT_START + 9.52, CONTACT_START + 14.10, "या फिर — 89688 69862 पर।"),
]
LINES = sorted([(sh(a), sh(b), txt) for a, b, txt in _BASE_LINES] + CONTACT_LINES)


# Scene boundaries (start times). Each scene runs until the next one starts.
_BASE_SCENES = [
    ("intro", 0.0),
    ("ticket", 5.55),
    ("draw_date", 14.40),
    ("lohri", 19.65),
    ("mrp", 21.80),
    ("drumroll", 25.45),
    ("jackpot", 27.20),
    ("prize2_3", 30.60),
    ("consolation", 37.70),
    ("series", 45.30),
    ("live", 51.55),
    ("tips", 56.95),
    ("responsible", 65.50),
    ("outro", 70.05),
]
SCENES = sorted([(n, sh(t)) for n, t in _BASE_SCENES] + [("contact", CONTACT_AT)], key=lambda x: x[1])


def scene_at(t):
    name, start = SCENES[0]
    end = DURATION
    for i, (n, s) in enumerate(SCENES):
        if t >= s:
            name, start = n, s
            end = SCENES[i + 1][1] if i + 1 < len(SCENES) else DURATION
    return name, start, end


# Sound effects cue sheet: (time, effect name, gain)
_BASE_SFX = [
    (0.00, "boom", 0.9), (0.05, "whoosh", 0.7), (0.30, "sparkle", 0.5),
    (5.55, "whoosh", 0.8), (6.10, "sparkle", 0.6),
    (10.35, "stamp", 1.0),
    (14.45, "whoosh", 0.6), (14.70, "page", 0.7), (15.05, "page", 0.7), (15.40, "page", 0.7), (15.80, "ding", 0.7),
    (17.00, "tick", 0.5), (17.50, "tick", 0.5), (18.00, "tick", 0.5), (18.50, "tick", 0.5),
    (19.65, "whoosh", 0.7), (19.75, "fire", 0.7), (19.80, "dhol", 0.9),
    (21.80, "whoosh", 0.7), (22.90, "cash", 0.9),
    (25.45, "drumroll", 0.8),
    (27.20, "crash", 0.9), (27.20, "boom", 1.0), (27.40, "counter", 0.5), (28.95, "ding", 0.8), (27.50, "coins", 0.7),
    (30.60, "whoosh", 0.7), (31.10, "ding", 0.6),
    (32.55, "whoosh", 0.6),
] + [(34.25 + i * 0.045, "pop", 0.35) for i in range(40)] + [
    (37.70, "whoosh", 0.7), (38.20, "pop", 0.8), (38.60, "pop", 0.8), (39.00, "pop", 0.8),
    (41.75, "whoosh", 0.5),
] + [(42.0 + i * 0.22, "click", 0.5) for i in range(9)] + [
    (44.10, "ding", 0.7),
    (45.30, "whoosh", 0.7), (46.10, "pop", 0.8), (46.50, "pop", 0.8), (46.90, "pop", 0.8), (47.30, "pop", 0.8),
    (49.30, "counter", 0.4), (50.20, "ding", 0.8),
    (51.55, "whoosh", 0.7), (52.00, "notify", 0.8), (52.60, "rattle", 0.5),
    (56.95, "whoosh", 0.6), (57.60, "check", 0.8), (60.30, "check", 0.8), (63.20, "check", 0.8),
    (65.50, "whoosh", 0.5), (65.90, "chime", 0.6),
    (70.05, "whoosh", 0.7), (71.30, "click", 1.0), (71.40, "pop", 0.7), (72.40, "click", 1.0), (72.50, "pop", 0.7),
    (73.40, "sparkle", 0.7),
]
SFX = [(sh(t), n, g) for t, n, g in _BASE_SFX] + [
    (CONTACT_AT, "whoosh", 0.7), (CONTACT_START + 0.3, "pop", 0.8), (CONTACT_START + 0.8, "sparkle", 0.6),
    (CONTACT_START + 2.4, "ding", 0.6), (CONTACT_START + 4.6, "notify", 0.8), (CONTACT_START + 9.6, "notify", 0.8),
]
