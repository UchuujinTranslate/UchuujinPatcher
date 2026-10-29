# Changelog

All changes below are unreleased and uncommitted (work done 2026-10-27 to 2026-10-29).

## Build process

### Clean console output
- New `UchuujinPatcher/console.py`: banner, numbered step headers (`[3/19]`), info/ok/warn/error lines, an in-place progress bar, timers.
- `main.py` is now a list of named steps. Each prints its time, and a timing table is shown at the end.
- External tools (CriPakTools, armips, deceboot, cpkmakec, GimConv, UMD-replace, xdelta3) run through `console.run`. Their output is hidden unless a tool fails, in which case the error and the last 15 lines are shown.
- Removed per-file prints, stray debug prints and the checksum print from the script patcher.

### No more ISO prompt
- `decompress_iso.py` picks `Nichijou - Uchuujin (Japan).iso` if present, otherwise the first `.iso`, and warns if there are several.

### Faster image conversion
- GimConv ran once per image, one after another. Images are now written first and converted in parallel (up to 32 workers).
- `union_cgs_extract.py`: 937 images in about 14 s (the serial version took over a minute).
- Same change in `pr_dump.py`, `pr_pack.py` and `union_cgs_insert.py` through `console.run_all`.
- GimConv gives slightly different bytes on repeated runs for 23 of the extracted images (serial runs also differ), so those PNGs are not byte-identical between runs.

### Reuse work between runs
- New `cache.py` and `work/cache_stamp.json` (ISO name, size, modification time and a hash of `cgs.json`).
- When the stamp matches, ISO extraction, both CPK dumps, CG extraction, the `pr.bin` unpack and the EBOOT decrypt are skipped.
- `cleanup.py` now deletes only build output, using a whitelist of ISO-derived files to keep.
- Git repos are fetched and reset in place instead of re-cloned (falls back to the existing copy when offline).
- Removed the unused `master` clone and the unused `work/weblate_scripts` copy.
- `py main.py --clean` forces a full rebuild.
- The EBOOT decrypt is its own step, and copying the translated images is its own step (it runs every time so new translations are picked up).
- Bump `CACHE_VERSION` in `cache.py` if the extraction scripts change in a way that makes old extracted files wrong.
- Cold build about 1:20, warm build about 0:30.

## Text layout (`sc/text_layout.py`)

- Translated dialog is laid out by real pixel width, using the per-glyph widths in `lt.bin`. Translators' line breaks are kept when they fit, and lines that are too wide are wrapped.
- Measured from PPSSPP screenshots: one width unit is 2 screen pixels, so the usable text width is 174 units. The last row is 166 because the next-arrow is drawn over its right end. The box holds 3 text rows (a 4th row is drawn over the 1st).
- `LINE_COLS` in `EBOOT.asm` now comes from `text_layout.MAX_COLUMNS` (41) via armips `-equ`. A value of 80 was tried and broke line breaks.
- Layout only applies to translated text, so untranslated Japanese is untouched.
- Overflowing messages that cannot be split are listed in `work/layout_report.txt`, with how many characters each is over.

### Splitting long messages into two boxes (experimental, tested in the game on one message)
- A message that needs more than 3 rows becomes two boxes by the same speaker. 85 messages are split in the current build.
- The script format stores each box as its own entry. The new first box is inserted before the original entry and gets a fresh id after the last one (ids are referenced by script commands, so none are renumbered). It carries the minimal tail `fb ff eb fe 00 00`. The original entry keeps its id and its full tail.
- The header's message count and the pointer table are updated. If the pointer table would not fit, the script is not split.
- Only messages whose entry ends with `fb ff` are split (the kind tested). The 6 that end with `98 ff` or `fd ff` stay unsplit.
- The break point is chosen by scoring: prefer the end of a sentence or clause, avoid ending a box on a word like "the" or "will be", prefer starting the next box with "and", "but", "from"..., keep the boxes roughly balanced.
- `work/split_report.txt` lists every split message with its script, id, speaker and text.
- Switch it off by setting `SPLIT_ALL = False` in `text_layout.py`.

## Font

### Glyph format (decoded)
- `lt.bin` is a list of 0x5C-byte records. Each has a 20x18 bitmap at 2 bits per pixel (first pixel in the low bits), and byte 0x5B is the advance width in units of 2 pixels. `font_tools.py` encodes and decodes glyphs and renders PNG previews.
- The game only draws glyph codes below `0xDB3`.

### English punctuation (`english_glyphs.py`, `font_patch.py`)
- The font only had Japanese full-width punctuation (18 px wide). New narrow glyphs for `! ? : ; ( ) - – — … . , " '` plus `#` and `~`, in glyph slots that no script uses.
- Curly quotes and `～ 〜` map to the new glyphs. Full-width `！ ？ （ ） ： ； ， ． ＃ ＆ ―` in translated text map to the plain English ones.
- Untranslated Japanese keeps its original glyphs.
- The build fails if a glyph is assigned a code at or above the game's limit.

### Spacing and shapes
- Letters and digits are respaced so no two glyphs touch (at least 1 px of margin on each side). `i l I j` get 2 px. `d q r t f` keep both margins so a stem next to them isn't 1 px away. `a` and `e` keep their original width.
- `i` redrawn at the same height as `j` (it was one row low).
- `g` and `y` moved down one row (they were one row too tall).

## Smaller fixes
- `pr_pack.py` used `sys.exit()` without importing `sys`.
- `cgs_insert` closes `EBOOT_patched.BIN` when it finishes.
- CriPakTools is run as `.\CriPakTools.exe` after moving to `console.run` (the bare name was not found, which broke both CPK dumps; found and fixed in testing).
- `patch_translations` returns its overflow and split records, and `patch_sc.py` writes the reports.

## Not verified / open
- Everything above was built end to end in a scratch copy, and all 224 patched scripts read back with a valid structure. In PPSSPP only the following have been checked: punctuation, line wrapping and the tutorial split (map text, and the antenna text in the backlog).
- Not yet seen in the game: the other splits, the `i g y u` changes, `#` and `~`.
- 6 messages still overflow (`98ff` or `fdff` endings), for example `sc/0021` id 59 (5 rows).
- Voiced or animated lines in split messages are the main unknown: the first box carries no commands, and the original box keeps all of them.

## New files
`console.py`, `cache.py`, `font_tools.py`, `english_glyphs.py`, `font_patch.py`, `sc/text_layout.py`, `CHANGELOG.md`
