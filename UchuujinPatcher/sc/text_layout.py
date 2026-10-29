# Line layout for translated dialog.
#
# The game does not measure text: it wraps after a fixed number of glyphs
# per line and only has room for three lines of text under the speaker name.
# Translations are written without knowing the real pixel width of each
# glyph, so lines run out of the box or wrap into rows that don't exist.
#
# This works on the encoded 16-bit glyph codes (the same ones written into
# the script) and uses the per-glyph advance widths stored in lt.bin, which
# is exactly what the game's variable width font routine uses, so the width
# computed here is the width drawn on screen.

import struct
from functools import lru_cache

# Inner width of the text box in glyph width units. One unit is drawn as
# 2 pixels of the PSP's 480x272 screen (measured against PPSSPP screenshots:
# 168 units of text measured 333px). The text box is 371px wide and the text
# starts 10px inside it, so the usable width is ~351px = ~175 units.
MAX_WIDTH = 174
# The "next" arrow is drawn over the right end of the last text row.
LAST_LINE_WIDTH = 166
# Glyphs per line before the game wraps on its own. patch_eboot.py passes
# this to armips as LINE_COLS, so the game and the layout always agree.
# The original game used 22 and an earlier patch raised it to 41. Setting it
# to 80 was tried and broke the game's line breaks, so keep it at 41.
MAX_COLUMNS = 41
# Text rows under the speaker name (a fourth row is drawn over the first).
MAX_LINES = 3

NEWLINE = 0xFFFE
SPACE = 0x0000
LT_PATH = "work/isofiles/lt_patched.bin"
GLYPH_SIZE = 0x5C
WIDTH_OFFSET = 0x5B


@lru_cache(maxsize=None)
def load_widths(path=LT_PATH):
    """Advance width of every glyph, indexed by glyph code."""
    with open(path, "rb") as f:
        data = f.read()
    return bytes(data[i * GLYPH_SIZE + WIDTH_OFFSET]
                 for i in range(len(data) // GLYPH_SIZE))


def is_control(code):
    # 0xF000 and up are control codes (newline, colors, waits...)
    return code >= 0xF000


def glyph_width(code, widths):
    if is_control(code) or code >= len(widths):
        return 0
    return widths[code]


def line_width(codes, widths):
    return sum(glyph_width(c, widths) for c in codes)


def line_columns(codes):
    return sum(1 for c in codes if not is_control(c))


class Limits:
    """Maximum size of each text row."""

    def __init__(self, max_width=MAX_WIDTH, last_width=LAST_LINE_WIDTH,
                 max_columns=MAX_COLUMNS, max_lines=MAX_LINES):
        self.max_width = max_width
        self.last_width = last_width
        self.max_columns = max_columns
        self.max_lines = max_lines

    def width(self, index):
        return self.last_width if index == self.max_lines - 1 \
            else self.max_width


def fits(codes, widths, limits, index):
    return (line_width(codes, widths) <= limits.width(index)
            and line_columns(codes) <= limits.max_columns)


def split_words(codes):
    words, cur = [], []
    for c in codes:
        if c == SPACE:
            if cur:
                words.append(cur)
                cur = []
        else:
            cur.append(c)
    if cur:
        words.append(cur)
    return words


def wrap_line(codes, widths, limits, first_index=0):
    """Greedy word wrap of one logical line.

    first_index is the row the line starts on (the last row is narrower).
    Returns a list of lines."""
    if fits(codes, widths, limits, first_index):
        return [codes]
    lines, cur = [], []

    def index():
        return first_index + len(lines)

    for word in split_words(codes):
        candidate = cur + [SPACE] + word if cur else word
        if fits(candidate, widths, limits, index()):
            cur = candidate
            continue
        if cur:
            lines.append(cur)
        cur = word
        # a single word that is too long is split where it stops fitting
        while not fits(cur, widths, limits, index()):
            n = len(cur) - 1
            while n > 1 and not fits(cur[:n], widths, limits, index()):
                n -= 1
            lines.append(cur[:n])
            cur = cur[n:]
    if cur:
        lines.append(cur)
    return lines


def layout(codes, widths, limits=None):
    """Lay out one message.

    Lines the translator already broke are kept if they fit. Lines that are
    too wide are wrapped, and if that needs more than max_lines the whole
    message is reflowed to use as few lines as possible.

    Returns (codes, line_count)."""
    limits = limits or Limits()
    trailing_newline = bool(codes) and codes[-1] == NEWLINE
    body = codes[:-1] if trailing_newline else codes

    logical = [[]]
    for c in body:
        if c == NEWLINE:
            logical.append([])
        else:
            logical[-1].append(c)

    lines = []
    for line in logical:
        lines.extend(wrap_line(line, widths, limits, len(lines)))

    if len(lines) > limits.max_lines:
        flat = []
        for line in logical:
            if flat and line:
                flat.append(SPACE)
            flat.extend(line)
        reflowed = wrap_line(flat, widths, limits)
        if len(reflowed) < len(lines):
            lines = reflowed

    out = []
    for i, line in enumerate(lines):
        if i:
            out.append(NEWLINE)
        out.extend(line)
    if trailing_newline:
        out.append(NEWLINE)
    return out, len(lines)


def layout_bytes(data, widths, limits=None):
    """layout() on little-endian encoded text. Returns (bytes, line_count)."""
    codes = list(struct.unpack("<{}H".format(len(data) // 2), data))
    out, count = layout(codes, widths, limits)
    return struct.pack("<{}H".format(len(out)), *out), count


def excess_glyphs(data, max_lines=MAX_LINES):
    """Number of glyphs that end up below the last row the box has."""
    codes = struct.unpack("<{}H".format(len(data) // 2), data)
    newlines = excess = 0
    for c in codes:
        if c == NEWLINE:
            newlines += 1
        elif newlines >= max_lines and not is_control(c):
            excess += 1
    return excess


# ------------------- splitting long messages across boxes ------------------- #
#
# A message that needs more rows than the box has is shown as several boxes
# by the same speaker, like the game's own long speeches. The script file
# stores each box as its own entry, so a split adds entries:
#   - the new first box is inserted before the original entry and gets a new
#     id after the last one (ids are referenced by the script commands, so the
#     original ids are never changed)
#   - the original entry keeps its id and command tail, and shows the last box
#   - the first box ends with only "end of text" + "wait" (fb ff, eb fe 00 00),
#     which every ordinary entry also contains
#
# Tested in the game on the map tutorial text (sc/0208 id 27): two boxes,
# the backlog shows both and the script continues normally. Entries that end
# with something other than "fb ff" (98 ff and fd ff: automatic or voice
# driven messages) were not tested, so they are left alone and reported.

SPLIT_ALL = True
SPLIT_ONLY = set()  # (script, message id) pairs to split even if SPLIT_ALL is off
SPLIT_TAIL = "fbffebfe0000"
SPLIT_TAIL_KIND = "fbff"  # the entry ending the split was tested with


def split_enabled(script, message_id, tail_hex=""):
    if (script, message_id) in SPLIT_ONLY:
        return True
    return SPLIT_ALL and tail_hex.startswith(SPLIT_TAIL_KIND)


# Words a box should not end on: the sentence obviously continues.
WEAK_WORDS = {
    "a", "an", "the", "and", "or", "but", "nor", "of", "to", "in", "on", "at",
    "for", "with", "by", "as", "if", "that", "which", "who", "whom", "whose",
    "is", "are", "was", "were", "be", "been", "will", "would", "can", "could",
    "should", "may", "might", "shall", "has", "have", "had", "do", "does",
    "did", "not", "no", "my", "your", "his", "her", "its", "our", "their",
    "this", "these", "those", "than", "then", "so", "from", "into", "about",
    "i", "you", "he", "she", "we", "they", "it", "because", "when", "while",
}
# Words that read naturally at the start of the next box.
CONJUNCTIONS = {
    "and", "but", "or", "so", "because", "when", "while", "although",
    "though", "which", "if", "until", "since", "as", "where", "then",
}
PREPOSITIONS = {"from", "with", "in", "on", "at", "for", "to", "about", "by"}
SENTENCE_END = ".!?\u2026"          # . ! ? ...
CLAUSE_END = ",;:\u2014"            # , ; : em dash


def _glyph_chars():
    """glyph code -> character, for the letters, digits and punctuation."""
    try:
        from UchuujinPatcher import english_glyphs
    except ImportError:
        import english_glyphs
    chars = {code: ch for ch, code in english_glyphs.char_codes().items()
             if ch not in english_glyphs.ALIASES}
    chars.update({0x92 + k: str(k) for k in range(10)})
    chars.update({0x9C + k: chr(ord("A") + k) for k in range(26)})
    chars.update({0xB6 + k: chr(ord("a") + k) for k in range(26)})
    return chars


def word_text(word):
    chars = _glyph_chars()
    return "".join(chars.get(c, "?") for c in word)


def break_score(before, after, widths):
    """How good it is to end a box after the word `before`.

    Higher is better: ends of sentences and clauses are good, ending on a
    word like "the" or "will be" is bad, and boxes of similar size are good."""
    text = word_text(before).rstrip("\"')")
    score = 0
    if text and text[-1] in SENTENCE_END:
        score += 50
    elif text and text[-1] in CLAUSE_END:
        score += 20
    if text.strip(SENTENCE_END + CLAUSE_END).lower() in WEAK_WORDS:
        score -= 25
    following = word_text(after).lower().strip(SENTENCE_END + CLAUSE_END)
    if following in CONJUNCTIONS:
        score += 18
    elif following in PREPOSITIONS:
        score += 8
    return score


def paginate(codes, widths, limits=None):
    """Split a message into boxes of at most max_lines rows each.

    The text is reflowed (the translator's line breaks are ignored). A
    message that needs two boxes is split where it reads best: after the end
    of a sentence or clause, not after a word like "the" or "will be", and
    with the two boxes about the same size. Longer messages just get their
    rows spread evenly. Returns a list of boxes, each a list of rows (lists
    of codes)."""
    limits = limits or Limits()
    body = codes[:-1] if codes and codes[-1] == NEWLINE else codes
    words = split_words([SPACE if c == NEWLINE else c for c in body])

    def wrap(word_list, rows_per_box):
        """Greedy rows for word_list, at most rows_per_box per box."""
        boxes, i = [], 0
        while i < len(word_list):
            rows = []
            while i < len(word_list) and len(rows) < rows_per_box:
                row, cur = len(rows), []
                while i < len(word_list):
                    candidate = (cur + [SPACE] + word_list[i]
                                 if cur else word_list[i])
                    # a word wider than a whole row goes on a row of its own
                    if fits(candidate, widths, limits, row) or not cur:
                        cur = candidate
                        i += 1
                    else:
                        break
                rows.append(cur)
            boxes.append(rows)
        return boxes

    boxes = wrap(words, limits.max_lines)
    total_rows = sum(len(b) for b in boxes)
    target = -(-total_rows // len(boxes))
    if target < limits.max_lines:
        balanced = wrap(words, target)
        if len(balanced) <= len(boxes):
            boxes = balanced

    if len(boxes) == 2:
        best = None
        for k in range(1, len(words)):
            first = wrap(words[:k], limits.max_lines)
            second = wrap(words[k:], limits.max_lines)
            if len(first) != 1 or len(second) != 1:
                continue   # each side must fit one box
            rows_a, rows_b = first[0], second[0]
            width_a = line_width([c for w in words[:k] for c in w], widths)
            width_b = line_width([c for w in words[k:] for c in w], widths)
            score = (break_score(words[k - 1], words[k], widths)
                     - abs(width_a - width_b) / 12
                     - 6 * abs(len(rows_a) - len(rows_b)))
            if best is None or score > best[0]:
                best = (score, [rows_a, rows_b])
        if best:
            boxes = best[1]
    return boxes


def fit_bytes(data, widths, split=False, limits=None):
    """Lay out encoded text, splitting it into boxes if allowed.

    Returns (list of encoded boxes, rows in the tallest box)."""
    limits = limits or Limits()
    codes = list(struct.unpack("<{}H".format(len(data) // 2), data))
    out, count = layout(codes, widths, limits)
    if count <= limits.max_lines or not split:
        return [struct.pack("<{}H".format(len(out)), *out)], count

    boxes = paginate(codes, widths, limits)
    packed = []
    for rows in boxes:
        flat = []
        for row in rows:
            flat.extend(row)
            flat.append(NEWLINE)
        packed.append(struct.pack("<{}H".format(len(flat)), *flat))
    return packed, max(len(rows) for rows in boxes)
