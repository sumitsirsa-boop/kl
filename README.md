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

## Rebuild
```
python3 video/build_audio.py   # soundtrack + lip-sync data -> build/
python3 video/render.py        # renders output/punjab_dear_1000_ticket.mp4
python3 video/render.py --still 28.5   # preview a single frame

# Diwali Bumper video
python3 video/build_audio.py --project diwali
python3 video/render.py --project diwali
```
The Diwali video's timings live in `video/diwali_timeline.py`, its scenes in `video/diwali_scenes.py`.
Timings, captions and the SFX cue sheet live in `video/timeline.py`.
Fonts: Anton, Poppins, Hind (SIL Open Font License).
