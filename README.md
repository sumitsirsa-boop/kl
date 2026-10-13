# Punjab Lottery – Ticket Explainer Videos

## 1. Punjab State Dear 1000 Quarterly

Final video: `output/punjab_dear_1000_ticket.mp4` (1080x1920 vertical, 90s, Reels/Shorts ready)

- **Voiceover:** Hindi presenter voice (ElevenLabs, voice "Bunty – Punchy, Crisp and Reel King") – `assets/voiceover.mp3`
  plus the agency contact line `assets/voiceover_contact.mp3` (Sumit Lottery Agency, Mansa – 70598 77770 / 89688 69862), spliced in before the Like & Share outro
- **Presenter:** animated 2D host, lip-synced to the voiceover (big on intro/outro, picture-in-picture elsewhere)
- **Motion graphics:** ticket fly-in + shine, Govt. of Punjab stamp, calendar flip to 09-01-2027, 7 PM clock, ₹1000 price tag,
  drum-roll → ₹50 lakh counter, 2nd/3rd/consolation prize cards, full prize table, A/B/C/D series → 40,000 tickets,
  live-draw phone, tips checklist, responsible-play card, Like & Share end card
- **B-rolls (procedural):** Lohri bonfire with kites, coin & note rain, confetti, lottery draw machine, spotlights
- **Sound effects (synthesized):** whoosh, boom, stamp, page flip, clock tick, dhol, cash register, drum roll, crash, coins, pops, clicks, chimes + background music bed ducked under the voice
- **Captions:** Hindi karaoke-style captions synced to speech

## 2. Punjab State Dear Diwali Bumper 2026 (Diwali theme)

Final video: `output/punjab_dear_diwali_bumper_2026.mp4` (1080x1920 vertical, 97.5s)

- Hindi voiceover (`assets/diwali/voiceover.mp3`) – ₹12 crore guaranteed 1st prize drawn out of sold tickets only,
  first time in Punjab lottery history, draw 16-11-2026 6 PM, MRP ₹500, 12 rashi series (36 lakh tickets),
  2nd/3rd/consolation prizes, full prize table (1,90,842 prizes), live draw, Sumit Lottery Agency contact
- Diwali look: maroon/gold, fireworks, diyas, rotating rangoli, marigold toran, Happy Diwali intro/outro
- Agency name, address and numbers run all the time in a bottom ticker, plus pop-up contact cards between scenes
- Extra synthesized SFX: rocket fireworks, crackers, temple bell
- Covers: `output/cover_diwali_reel_1080x1920.jpg` (Reels/FB) and `output/cover_diwali_feed_1080x1350.jpg` (feed) – `python3 video/cover.py`

## 3. Sumit Lottery Agency – 3-ticket COMBO offer

Final video: `output/sumit_lottery_combo_offer.mp4` (1080x1920 vertical, 84.5s; `_share.mp4` is a smaller copy)

- Hindi voiceover (`assets/combo/voiceover.mp3`): Nagaland Dear Puja Bumper (₹3 Cr, 24-10-2026, ₹500),
  Punjab Dear 200 Monthly (₹1.50 Cr, 07-11-2026, ₹200), Punjab Dear Diwali Bumper (₹12 Cr, 16-11-2026, ₹500);
  1st prize guaranteed from sold tickets in all three; ₹1200 → combo ₹1199 with free delivery; agency contact
- Ticket images are cropped from the combo poster (`assets/combo/poster.png`); all five agency numbers run in the ticker

## 4. Diwali Bumper 2026 – presented by a Punjabi girl ("Punjaban")

Final video: `output/diwali_bumper_punjaban.mp4` (1080x1920 vertical, 62.8s)

- Different style: an animated Punjabi girl (phulkari dupatta, paranda braid, jhumkas) holds the real ticket
  in both hands and talks about it; zoom lenses pop out of the ticket (title, Govt logo, sold-tickets line,
  draw date, MRP); Instagram-story stickers; phulkari border; full-screen B-roll cutaways (₹12 crore
  jackpot, prize ladder, rashi wheel) with her in a corner circle
- Female Punjabi-accented voice (ElevenLabs "Jasleen"), Hindi with Punjabi touches; agency ticker at the bottom
- Character: `video/presenter_girl.py`; scenes: `video/punjaban_scenes.py`

## Rebuild
```
python3 video/build_audio.py   # soundtrack + lip-sync data -> build/
python3 video/render.py        # renders output/punjab_dear_1000_ticket.mp4
python3 video/render.py --still 28.5   # preview a single frame

# Diwali Bumper video
python3 video/build_audio.py --project diwali
python3 video/render.py --project diwali

# Combo offer video
python3 video/build_audio.py --project combo
python3 video/render.py --project combo

# Punjabi girl presenter video
python3 video/build_audio.py --project punjaban
python3 video/render.py --project punjaban
```
The Diwali video's timings live in `video/diwali_timeline.py`, its scenes in `video/diwali_scenes.py`.
Timings, captions and the SFX cue sheet live in `video/timeline.py`.
Fonts: Anton, Poppins, Hind (SIL Open Font License).
