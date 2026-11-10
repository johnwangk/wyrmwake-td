# Wyrmwake TD - M1 prototype
Single self-contained file: `index.html`. Canvas 2D, inline JS and CSS, no build step, no CDN.
Open it in any browser, or serve the folder: `python3 -m http.server 8000`.

- All names, labels, descriptions and colors: the `CONFIG` object at the top of the `<script>`.
- Save: localStorage key `mergetd-dragon-proto.save.v1` (`{bestWave, wins}`). The key does not depend on the title.
- Debug URL flags (all off by default): `?speed=10` fast-forward, `?seed=123` fixed RNG, `?fps` FPS readout.
- Keyboard (desktop): S or Space summons, E boosts, P or Esc pauses, 1-3 picks a card.
- Tests (Playwright): `test/run.mjs <speed> <seed> bot|idle [tag]` plays a full match with touch drags. `test/extra.mjs` checks mouse drag and frame timing. `test/shots2.mjs` takes the boost, boss-banner and defeat screenshots.

## Files

```
index.html                      the game (all code + CONFIG at the top)
assets/manifest.json            the Designer's art manifest, copied verbatim from wyrmwake-art/
assets/sheets/dragons|enemies/  sprite strips (batch 1)
assets/tiles/                   grass, path, slot and Clutch tiles (batch 1)
assets/fonts/PressStart2P.ttf   UI font, SIL Open Font License (assets/fonts/OFL.txt)
tools/embed-manifest.py         refreshes the file:// fallback copy of the manifest inside index.html
release/live-ce3b724.html       backup of the live build (hotfixes go out from here)
test/                           Playwright checks (not needed on the site)
```

Everything uses relative paths with no CDN, so the folder works as-is on GitHub Pages.

## Rendering

The game draws to a fixed **360x640** canvas, letterboxed on #181425. The fit scale is
`s = min(availW/360, availH/640)` in CSS px. A whole-number scale (`floor(s)`) is used when
it still covers at least 80% of that fit; otherwise the fractional fit is used so small
screens fill. Sampling stays nearest-neighbour (`image-rendering: pixelated`,
`imageSmoothingEnabled = false`). The displayed size is snapped so CSS px × devicePixelRatio
is a whole number of device pixels. Taps are mapped through `canvas.getBoundingClientRect()`.

The rotate overlay is a DOM element. It appears only when all three are true:
`(pointer: coarse) and (hover: none)`, the screen's short side (`screen.width/height`)
is under `CONFIG.display.rotateOverlayMaxScreenShortSide` (500), and the window is landscape.

## Art: the Designer's manifest

The game reads `assets/manifest.json` in the Designer's own format (`wyrmwake-art/manifest.json`):

```json
{ "meta": { ... },
  "sheets": [
    { "id": "jaculus_lv1_attack", "path": "sheets/dragons/jaculus_lv1_attack.png", "batch": 1,
      "category": "dragon", "dragon": "jaculus", "level": 1, "anim": "attack",
      "frame_w": 48, "frame_h": 48, "frames": 4, "fps": 10, "loop": false,
      "anchor": [24, 47], "hit_frame": 1 } ] }
```

* `path` is relative to the manifest. Sheets are horizontal strips: frame i sits at
  x = i*frame_w, y = 0. They are drawn with nearest-neighbour filtering at whole-number
  scales only.
* `anchor` is the pixel inside the frame that lands on the game position. Sprites use
  bottom-centre, with the feet on the last row. Tiles use top-left.
* If two entries share an `id`, the later one wins, so batch 2 can simply be appended.

How the game uses each category:

| category / id | use |
|---|---|
| `dragon` (`dragon`, `level` 1-5, `anim` idle/attack) | Each level has its own art. `idle` loops. `attack` plays once, timed so `hit_frame` lands on the shot, then returns to idle. A missing level uses the nearest level (ties go to the lower one). With no attack strip, the dragon stays idle. Ehecatl has no shot, so its attack strip plays as a gust every ~2.6 s while it buffs a neighbour. |
| `enemy` (`enemy` poacher / brute / boss, `anim` walk) | All enemies face right. They are mirrored on leftward stretches, or per entry with `"facing":"left"`. The final boss uses `boss_final` if present, otherwise `boss`. |
| `clutch` (`state` full / mid / low) | Picked by warmth: above 67% full, above 34% mid, otherwise low. |
| `grass_1..3`, `path_h`, `path_v`, `path_corner_{ne,nw,se,sw}`, `path_end_{n,s,e,w}` | The background is built from these, with path tiles centred on each lane. |
| `slot_empty`, `slot_highlight`, `slot_highlight_overlay` | Board slots, the slot under a dragged dragon, and the pulsing ring on slots it can merge with. |
| projectiles `jaculus_javelin`, `zmei_fireball`, `kanju_tidemist` | Drawn facing right with the anchor at the tip, rotated by atan2(dy, dx). The angle snaps to 32 steps so the pixels don't shimmer. |
| `jaculus_hit`, `zmei_explosion`, `kanju_mist_pool` | Jaculus impact. Zmei blast, drawn at the whole-number scale nearest to the blast diameter (art is ~26 px across): x2-x4 depending on level and boosts. Kanju slow zone: drawn under the enemies for the slow's duration, at most 10 at a time. |
| `ehecatl_aura` / `ehecatl_aura_gold` | Behind each Ehecatl, centred on its slot: Lv1-3 use the normal aura, Lv4-5 the gold one. |
| `merge_sparkle`, `levelup_flash`, `coin_pickup` | Merge: the sparkle plays and the old sprite stays until frame 3, then the new dragon appears with the level-up flash over it. `coin_pickup` plays at the kill spot when coins are earned. |
| `btn_summon`, `btn_enhance` (96x32), `btn_pause`/`btn_resume`/`btn_restart` (32x32) | The frame index is the state (`states` order: normal / pressed / disabled). Text goes in `text_area`, 2 px lower when pressed. Tap areas are padded to at least 48 px. Pause swaps to resume while paused. On the pause screen, resume and restart are drawn at 2x. |
| `panel_9slice`, `btn_panel_9slice`, `bar_frame_9slice` + `bar_fill_warmth` | 9-slices use the manifest `slice` insets. The warmth fill is stretched horizontally inside the bar's 3 px well. |
| `icon_coin`, `icon_heart`, `icon_warmth`, `wave_badge` | `icon_coin` sits on the coins panel and `icon_warmth` by the warmth bar. `icon_heart` is on the end screens (full or empty). `wave_badge` is drawn at 2x, with "N/20" in its `text_area`. |
| `enh_card_*` (`enhancement` field), `enh_card_select` | Drawn at 2x (112x160, three across). Our boost name goes in `text_area.title` and our description in `text_area.body`; the card's own `effect` text is used only if ours doesn't fit. The select overlay is drawn at -2,-2 on the pressed or hovered card. Boost id to card mapping: `CONFIG.art.cards`. |
| `screen_win`, `screen_lose` | Full-screen 360x640 background with the title built into the art. Stats and buttons go in `safe_areas.text_and_buttons`. |
| `app_icon_*` | Not loaded by the game. `index.html` links `app_icon_64_native` (favicon) and `app_icon_180` (apple-touch-icon). `manifest.webmanifest` lists 180/512/1024. |

Ids are looked up through `CONFIG.art.slots`, and the first one present wins. Sheets in
`CONFIG.art.noPreload` (app icons, `*_native`) are skipped.

**Fallbacks.** A missing or broken file never stops the game. It falls back as described above,
and the console gets one `[art]` warning listing what failed.

**Designer drop-in (no code changes):**
1. Copy the updated `manifest.json` over `assets/manifest.json`.
2. Copy the new PNGs into `assets/`, using the same relative paths as in the manifest.
3. Optional: run `python3 tools/embed-manifest.py` so that opening `index.html` straight
   from disk (file://) also sees the new entries. Browsers block `fetch` on file://, so
   in that case the game uses a copy of the manifest embedded in `index.html`. Over http
   (GitHub Pages, or `python3 -m http.server`) it always reads `assets/manifest.json`.
