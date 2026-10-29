# Improve the English side of the patched font:
#  - respace the letters and digits, so no two glyphs touch
#  - draw the English punctuation glyphs (see english_glyphs.py)
# Runs after adjust_width_font, which sets every glyph width.

try:
    from UchuujinPatcher import console, english_glyphs, font_tools
except ImportError:
    import console
    import english_glyphs
    import font_tools

FONT_PATH = "work/isofiles/lt_patched.bin"
LEVELS = {" ": 0, ".": 1, "+": 2, "#": 3}

# Glyph codes of the digits, capitals and lowercase letters.
LETTER_CODES = range(0x92, 0xD0)
# Smallest gap kept between the ink of a glyph and the edge of its advance.
MARGIN = 1
# Narrow stems (i l I j) look cramped next to round letters with 1 pixel.
WIDE_MARGIN = 2
WIDE_MARGIN_CODES = {0xBE, 0xC1, 0xA4, 0xBF}  # i l I j
# Glyphs with an odd ink width and a vertical stem: d q (right), r t f (left).
ROUND_UP_CODES = {0xB9, 0xC6, 0xC7, 0xC9, 0xBB}

# Glyph codes that need their rows fixed. Every other lowercase letter has
# its x-height between rows 6 and 14, but these were drawn one row too high.
I_CODE = 0xBE
G_CODE = 0xBC
Y_CODE = 0xCE


def glyph_rows(top, art):
    rows = [[0] * font_tools.GLYPH_W for _ in range(font_tools.GLYPH_H)]
    for i, line in enumerate(art):
        for col, ch in enumerate(line):
            rows[top + i][col] = LEVELS[ch]
    return rows


def body_bounds(rows):
    """(first, last) columns of the glyph, ignoring faint-only edge columns.

    A column at either edge that has only a few faint pixels (the tip of an
    antialiased curve or crossbar) is not counted, so it sits in the margin
    instead of making the glyph one pixel wider."""
    first, last = font_tools.ink_bounds(rows)

    def faint(col):
        values = [row[col] for row in rows if row[col]]
        return max(values) <= 1 and len(values) <= 3

    while first < last and faint(first):
        first += 1
    while last > first and faint(last):
        last -= 1
    return first, last


def respace_glyph(data, code, margin=MARGIN):
    """Make sure no glyph touches the next one.

    The ink is placed `margin` pixels from the start of the cell, and the
    advance (a whole number of units, 2 pixels each) is the ink plus the
    margins, rounded down. For an odd ink width that leaves one side with a
    pixel less, which is fine for round letters but makes a stem only 1 pixel
    from its neighbour (du, qu, ra). Glyphs in ROUND_UP_CODES have a stem and
    keep both margins instead."""
    rows = font_tools.decode_glyph(data, code)
    if font_tools.ink_bounds(rows) is None:
        return
    first, last = body_bounds(rows)
    ink = last - first + 1
    units = (ink + 2 * margin) // 2
    if code in ROUND_UP_CODES and units * 2 - ink < 2 * margin:
        units += 1
    shift = margin - first
    shifted = [[0] * font_tools.GLYPH_W for _ in rows]
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            if value and 0 <= c + shift < font_tools.GLYPH_W:
                shifted[r][c + shift] = value
    font_tools.write_glyph(data, code, shifted, units)


def remap_rows(data, code, mapping):
    """Rebuild a glyph so that row `dst` is the old row `src`."""
    rows = font_tools.decode_glyph(data, code)
    new = [[0] * font_tools.GLYPH_W for _ in rows]
    for dst, src in mapping.items():
        new[dst] = list(rows[src])
    font_tools.write_glyph(data, code, new, font_tools.advance(data, code))


def fix_glyph_heights(data):
    # g and y: move the part above the descender down one row
    body = {6 + k: 5 + k for k in range(9)}
    remap_rows(data, G_CODE, {**body, 15: 15, 16: 16, 17: 17})
    remap_rows(data, Y_CODE, {**body, 15: 14, 16: 15, 17: 16})
    # i: dot on rows 2-3, stem from row 6 like the j
    art = ["##", "##", "", "++"] + ["##"] * 9
    font_tools.write_glyph(data, I_CODE, glyph_rows(2, art), 2)


def patch_font_data(data):
    fix_glyph_heights(data)
    for code in LETTER_CODES:
        respace_glyph(data, code,
                      WIDE_MARGIN if code in WIDE_MARGIN_CODES else MARGIN)

    for ch, (code, advance, top, art) in english_glyphs.GLYPHS.items():
        # the game ignores glyph codes above this limit
        assert code < english_glyphs.GLYPH_LIMIT, f"{ch!r} uses slot {code:#x}"
        font_tools.write_glyph(data, code, glyph_rows(top, art), advance)
        respace_glyph(data, code)


def patch_font():
    with open(FONT_PATH, "rb") as f:
        data = bytearray(f.read())

    patch_font_data(data)
    console.info(f"Respaced {len(LETTER_CODES)} letter and digit glyphs, "
                 f"redrew {len(english_glyphs.GLYPHS)} punctuation glyphs")

    with open(FONT_PATH, "wb") as f:
        f.write(data)


if __name__ == "__main__":
    patch_font()
