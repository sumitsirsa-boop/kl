# Punjab State Dear 1000 – Ticket Explainer Video

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

## Rebuild
```
python3 video/build_audio.py   # soundtrack + lip-sync data -> build/
python3 video/render.py        # renders output/punjab_dear_1000_ticket.mp4
python3 video/render.py --still 28.5   # preview a single frame
```
Timings, captions and the SFX cue sheet live in `video/timeline.py`.
Fonts: Anton, Poppins, Hind (SIL Open Font License).
