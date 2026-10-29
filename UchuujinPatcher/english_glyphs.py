# English punctuation glyphs.
#
# The game's font only has Japanese full-width punctuation, which the
# original patch reused for English: "? ! : ; ( ) -" all took an 18 pixel
# wide cell and the quotes were Japanese marks. These glyphs replace them.
#
# They go into glyph slots that no script text uses (found by scanning every
# script), so Japanese text that has not been translated yet keeps its
# original punctuation.
#
# The game only draws glyph codes below 0xDB3 (the EBOOT checks this in
# several places), so the blank slots at the end of the font (0xDB3-0xDBB)
# can NOT be used: anything drawn there is invisible.
#
# Glyph cell is 20x18 pixels: capitals span rows 2-14, lowercase rows 6-14,
# the baseline is row 14. Art: ' ' = clear, '.' '+' = light, '#' = solid.
# The advance is in units of 2 pixels.

# char: (glyph code, advance, first row, art lines)
GLYPHS = {
    "!": (0xDAD, 2, 2, [
        " ##", " ##", " ##", " ##", " ##", " ##", " ##", " ##", " ##",
        "", "", "",
        " ##", " ##"]),
    "?": (0xDAE, 5, 2, [
        " +####+ ",
        "##+  +##",
        "##    ##",
        "      ##",
        "     +#+",
        "    +#+ ",
        "   +#+  ",
        "   ##   ",
        "   ##   ",
        "", "", "",
        "   ##   ",
        "   ##   "]),
    ":": (0xDA7, 2, 8, [
        " ##", " ##", "", "", "", " ##", " ##"]),
    ";": (0xD7E, 2, 8, [
        " ##", " ##", "", "", "",
        " ##", " ##", " +#", "+# "]),
    "(": (0xD7D, 3, 2, [
        "  +#",
        " +#.",
        " ##",
        "+#",
        "##", "##", "##", "##", "##", "##", "##",
        "+#",
        " ##",
        " +#.",
        "  +#"]),
    ")": (0xD7C, 3, 2, [
        "#+",
        ".#+",
        " ##",
        "  #+",
        "  ##", "  ##", "  ##", "  ##", "  ##", "  ##", "  ##",
        "  #+",
        " ##",
        ".#+",
        "#+"]),
    "-": (0xD7B, 4, 9, [
        "######",
        "######"]),
    "—": (0xD78, 7, 9, [
        "############",
        "############"]),
    "…": (0xD77, 6, 13, [
        "##  ##  ##",
        "##  ##  ##"]),
    ".": (0xDB2, 2, 13, [
        "##",
        "##"]),
    ",": (0xDAF, 2, 13, [
        "##",
        "##",
        "#+",
        "#"]),
    '"': (0xDB0, 4, 2, [
        "##  ##",
        "##  ##",
        "##  ##",
        "+#  +#"]),
    "–": (0xDB1, 5, 9, [
        "########",
        "########"]),
    "#": (0xD76, 6, 3, [
        "   ##  ##",
        "   ##  ##",
        "##########",
        "##########",
        "  ##  ##",
        "  ##  ##",
        "  ##  ##",
        "##########",
        "##########",
        " ##  ##",
        " ##  ##"]),
    "~": (0xD75, 7, 8, [
        " +##+    .#",
        "##++##  ###",
        "+#  +####+"]),
    # the apostrophe reuses the slot the original patch already used
    "'": (0x0C, 2, 2, [
        " ##",
        " ##",
        " ##",
        " +#"]),
}

# Other characters drawn with one of the glyphs above.
ALIASES = {
    "“": '"', "”": '"',
    "‘": "'", "’": "'",
    "～": "~", "〜": "~",
}

# Full-width forms that translators sometimes type. They are drawn with the
# glyph of the plain character (which may be one of the glyphs above).
FULLWIDTH = {
    "！": "!", "？": "?", "（": "(", "）": ")", "：": ":", "；": ";",
    "，": ",", "．": ".", "＃": "#", "＆": "&", "―": "—",
}


GLYPH_LIMIT = 0xDB3


def char_codes():
    """char -> glyph code for the characters this module redraws."""
    codes = {ch: spec[0] for ch, spec in GLYPHS.items()}
    codes.update({alias: codes[ch] for alias, ch in ALIASES.items()})
    return codes


def apply_fullwidth(table):
    """Point the full-width forms at the glyph of the plain character.

    table must already contain the plain characters (and char_codes())."""
    for full, plain in FULLWIDTH.items():
        if plain in table:
            table[full] = table[plain]
