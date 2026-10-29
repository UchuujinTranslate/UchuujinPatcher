# Helpers for the game's font (lt.bin).
#
# lt.bin is a list of 0x5C byte records, one per glyph code:
#   0x00-0x59  20x18 pixel bitmap, 2 bits per pixel, 5 bytes per row,
#              first pixel of a byte in the lowest two bits
#              (0 = transparent .. 3 = fully opaque)
#   0x5A       unused
#   0x5B       advance width, in units of 2 screen pixels (added by this patch)

import struct
import zlib

GLYPH_SIZE = 0x5C
BITMAP_BYTES = 90
WIDTH_OFFSET = 0x5B
GLYPH_W = 20
GLYPH_H = 18


def decode_glyph(data, code):
    """Return the glyph as a list of GLYPH_H rows of GLYPH_W values (0-3)."""
    raw = data[code * GLYPH_SIZE:code * GLYPH_SIZE + BITMAP_BYTES]
    pixels = [(b >> s) & 3 for b in raw for s in (0, 2, 4, 6)]
    return [pixels[r * GLYPH_W:(r + 1) * GLYPH_W] for r in range(GLYPH_H)]


def encode_glyph(rows):
    pixels = [p for row in rows for p in row]
    assert len(pixels) == GLYPH_W * GLYPH_H
    return bytes(pixels[i] | pixels[i + 1] << 2 | pixels[i + 2] << 4
                 | pixels[i + 3] << 6 for i in range(0, len(pixels), 4))


def write_glyph(data, code, rows, advance):
    """Write a glyph bitmap and advance width into the font data (bytearray)."""
    base = code * GLYPH_SIZE
    data[base:base + BITMAP_BYTES] = encode_glyph(rows)
    data[base + WIDTH_OFFSET] = advance


def advance(data, code):
    return data[code * GLYPH_SIZE + WIDTH_OFFSET]


def art_to_rows(art):
    """Build glyph rows from ASCII art. ' ' = 0, '.' = 1, '+' = 2, '#' = 3.

    The art can be smaller than the cell; it is placed at the top left.
    Rows are given from the top of the cell (row 6 is the top of lowercase
    letters, row 14 is the baseline)."""
    levels = {" ": 0, ".": 1, "+": 2, "#": 3}
    rows = [[0] * GLYPH_W for _ in range(GLYPH_H)]
    for r, line in enumerate(art):
        for c, ch in enumerate(line):
            rows[r][c] = levels[ch]
    return rows


def rows_to_art(rows):
    return ["".join(" .+#"[p] for p in row) for row in rows]


def ink_bounds(rows, min_value=1):
    """(first column, last column) with a pixel of at least min_value, or
    None if there is none. min_value=2 ignores faint antialiasing."""
    cols = [c for c in range(GLYPH_W)
            if any(row[c] >= min_value for row in rows)]
    return (cols[0], cols[-1]) if cols else None


# ------------------------------ preview ------------------------------ #

def _png(width, height, rgb_rows):
    raw = b"".join(b"\x00" + bytes(row) for row in rgb_rows)

    def chunk(tag, body):
        return (struct.pack(">I", len(body)) + tag + body
                + struct.pack(">I", zlib.crc32(tag + body)))
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


def render_lines(data, lines, scale=3):
    """Render lines of glyph codes the way the game draws them.

    lines is a list of lists of glyph codes; each glyph is drawn at the
    current x and the x advances by 2 * its width unit."""
    pad = 10
    line_h = GLYPH_H - 1
    width = max(sum(advance(data, c) * 2 for c in line) for line in lines) + 20 + 2 * pad
    height = len(lines) * line_h + 2 * pad
    canvas = [[255.0] * width for _ in range(height)]
    for li, line in enumerate(lines):
        x = pad
        y = pad + li * line_h
        for code in line:
            rows = decode_glyph(data, code)
            for r in range(GLYPH_H):
                for c in range(GLYPH_W):
                    a = rows[r][c] / 3
                    if a and 0 <= x + c < width and y + r < height:
                        canvas[y + r][x + c] *= 1 - a
            x += advance(data, code) * 2
    out = []
    for row in canvas:
        px = []
        for v in row:
            px += [int(v)] * 3
        line = bytes(px)
        scaled = b"".join(line[i:i + 3] * scale for i in range(0, len(line), 3))
        out.extend([scaled] * scale)
    return _png(width * scale, height * scale, out)
