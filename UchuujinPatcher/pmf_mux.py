# Building a PMF (PSMF) movie again from H.264 access units and ATRAC3+ frames.
#
# The muxer follows the layout of the game's own movies, which it was checked
# against by re-muxing the original streams:
#  * 2048 byte packs holding one PES packet each (video 0xE0 or audio 0xBD),
#    padded with a 0xBE packet when a GOP or the audio ends mid-pack
#  * fixed GOPs of 59 frames; the first pack of a GOP holds a system header
#    (0xBB) and a private stream 2 packet (0xBF) listing the size of every
#    access unit of the GOP
#  * no B-frames, DTS = PTS - 1 frame, the first PTS is 90000
#  * a PTS/DTS pair is only written on some video PES packets and applies to
#    the first access unit starting inside it; the others follow at 1 frame
#    each
#  * audio is one frame stream cut into PES packets, each led by a 4 byte
#    count of the bytes that still belong to the previous frame
import bisect
import re
import struct

PACK_SIZE = 2048
GOP_FRAMES = 59
FRAME_TICKS = 3003
FIRST_PTS = 90000
CLOCK = 90000
# the mux sends video this far ahead of its DTS and audio ahead of its PTS
VIDEO_LEAD = 90000
AUDIO_LEAD = 16600
FIRST_VIDEO_LEAD = 56850
# a PTS is written again once this many frames have passed
STAMP_FRAMES = 16
AUDIO_FRAME_TICKS = 2048 * CLOCK / 44100
AUDIO_FRAME_BYTES = 752
# 2048 bytes at the 1.25 MB/s mux rate, in 27 MHz ticks
PACK_TICKS = PACK_SIZE * 27000000 / 1250000
SYSTEM_HEADER = bytes.fromhex("000001bb000c80c35180f07fb9e0ebbde308")
VIDEO_EXT = bytes.fromhex("1e60eb")
AUDIO_EXT = bytes.fromhex("1e6004")


def split_access_units(es):
    """Cut an Annex B H.264 stream into access units at the access unit delimiters."""
    starts = [m.start() for m in re.finditer(b"\x00\x00\x00\x01\x09", es)]
    return [es[a:b] for a, b in zip(starts, starts[1:] + [len(es)])]


def encode_pts(marker, value):
    return bytes([
        marker << 4 | ((value >> 30) & 7) << 1 | 1,
        (value >> 22) & 0xFF,
        ((value >> 15) & 0x7F) << 1 | 1,
        (value >> 7) & 0xFF,
        (value & 0x7F) << 1 | 1])


def pack_header(scr27):
    base, ext = divmod(int(scr27), 300)
    x = (1 << 46 | ((base >> 30) & 7) << 43 | 1 << 42
         | ((base >> 15) & 0x7FFF) << 27 | 1 << 26
         | (base & 0x7FFF) << 11 | 1 << 10 | ext << 1 | 1)
    return b"\x00\x00\x01\xba" + x.to_bytes(6, "big") + bytes.fromhex("0186a3f8")


def padding(size):
    return b"\x00\x00\x01\xbe" + struct.pack(">H", size - 6) + b"\xff" * (size - 6)


def private_stream_2(sizes):
    # 01 E0, four counters (left at 0), 4 zero bytes, 4*N+2, N, then N * (0x0080, size)
    body = b"\x01\xe0" + bytes(8) + bytes(4)
    body += struct.pack(">HH", 4 * len(sizes) + 2, len(sizes))
    for size in sizes:
        body += struct.pack(">HH", 0x80, size)
    return b"\x00\x00\x01\xbf" + struct.pack(">H", len(body)) + body


def pes(stream_id, payload, flags, header):
    body = bytes([0x81, flags, len(header)]) + header + payload
    return b"\x00\x00\x01" + bytes([stream_id]) + struct.pack(">H", len(body)) + body


def video_pes(payload, pts=None, ext=False, stuffing=0):
    header, flags = b"", 0x00
    if pts is not None:
        header = encode_pts(3, pts) + encode_pts(1, pts - FRAME_TICKS)
        flags = 0xC0
    if ext:
        header += VIDEO_EXT
        flags |= 0x01
    return pes(0xE0, payload, flags, header + b"\xff" * stuffing)


def audio_pes(payload, pts, ext=False):
    header = encode_pts(2, pts)
    flags = 0x80
    if ext:
        header += AUDIO_EXT
        flags |= 0x01
    return pes(0xBD, payload, flags, header)


def patch_header(header, old_frames, new_frames, stream_size):
    """Copy of the PSMF header with the duration and stream size updated."""
    header = bytearray(header)
    old_end = FIRST_PTS + old_frames * FRAME_TICKS
    new_end = FIRST_PTS + new_frames * FRAME_TICKS
    old = struct.pack(">I", old_end)
    new = struct.pack(">I", new_end)
    at = bytes(header[:0x100]).find(old)
    while at >= 0:
        header[at:at + 4] = new
        at = bytes(header[:0x100]).find(old, at + 4)
    header[12:16] = struct.pack(">I", stream_size)
    return bytes(header)


def build_pmf(header, aus, frames, params, audio_pts):
    """Assemble a PMF.

    header: 0x800 byte PSMF header of the movie being replaced
    aus: H.264 access units (Annex B, each starting with a delimiter)
    frames: ATRAC3+ frame data; params: the two codec parameter bytes
    audio_pts: PTS of the first audio frame"""
    audio = bytearray()
    for frame in frames:
        audio += b"\x0f\xd0" + params + bytes(4) + frame
    assert len(audio) == len(frames) * AUDIO_FRAME_BYTES

    video = b"".join(aus)
    au_start = []
    pos = 0
    for au in aus:
        au_start.append(pos)
        pos += len(au)
    gop_limits = [au_start[a + GOP_FRAMES] if a + GOP_FRAMES < len(aus) else len(video)
                  for a in range(0, len(aus), GOP_FRAMES)]

    def audio_pts_of(frame):
        return round(audio_pts + frame * AUDIO_FRAME_TICKS)

    out = bytearray(header)
    vpos = apos = 0
    audio_packs = 0
    last_stamp = -10 ** 9
    t = (FIRST_PTS - FRAME_TICKS - FIRST_VIDEO_LEAD) * 300.0

    while vpos < len(video) or apos < len(audio):
        vdue = adue = None
        if vpos < len(video):
            current = bisect.bisect_right(au_start, vpos) - 1
            vdue = (FIRST_PTS + FRAME_TICKS * (current - 1) - VIDEO_LEAD) * 300.0
        if apos < len(audio):
            # the first packs go out at once to prime the audio buffer
            adue = float("-inf") if audio_packs < 2 else \
                (audio_pts_of(apos // AUDIO_FRAME_BYTES) - AUDIO_LEAD) * 300.0
        t = max(t, min(x for x in (vdue, adue) if x is not None))
        pack = bytearray(pack_header(t))

        if adue is not None and adue <= t and (vdue is None or vdue > t or adue <= vdue):
            room = min(PACK_SIZE - len(pack) - 6 - 3 - 5 - 4 - (3 if audio_packs == 0 else 0),
                       len(audio) - apos)
            cont = (-apos) % AUDIO_FRAME_BYTES
            first_frame = (apos + cont) // AUDIO_FRAME_BYTES
            payload = struct.pack(">I", cont) + bytes(audio[apos:apos + room])
            pack += audio_pes(payload, audio_pts_of(first_frame), audio_packs == 0)
            apos += room
            audio_packs += 1
        else:
            gop = vpos_gop = bisect.bisect_right(au_start, vpos) - 1
            gop = gop // GOP_FRAMES
            gop_first = au_start[gop * GOP_FRAMES] == vpos
            if gop_first:
                sizes = [len(a) for a in aus[gop * GOP_FRAMES:(gop + 1) * GOP_FRAMES]]
                pack += SYSTEM_HEADER + private_stream_2(sizes)
            limit = gop_limits[gop]
            room = PACK_SIZE - len(pack) - 6 - 3 - (13 if gop_first else 0)
            n = min(room, limit - vpos)
            # first access unit that starts inside this packet
            a = bisect.bisect_left(au_start, vpos)
            stamp = None
            if a < len(aus) and (a == 0 or a % GOP_FRAMES == 0 or a - last_stamp >= STAMP_FRAMES):
                with_stamp = min(room - (0 if gop_first else 10), limit - vpos)
                if au_start[a] < vpos + with_stamp:
                    stamp = FIRST_PTS + FRAME_TICKS * a
                    last_stamp = a
                    n = with_stamp
            built = video_pes(video[vpos:vpos + n], stamp, gop_first)
            left = PACK_SIZE - len(pack) - len(built)
            if 0 < left < 6:
                # too little room for a padding packet: stuff the PES header instead
                built = video_pes(video[vpos:vpos + n], stamp, gop_first, left)
            pack += built
            vpos += n
        if len(pack) < PACK_SIZE:
            pack += padding(PACK_SIZE - len(pack))
        assert len(pack) == PACK_SIZE, len(pack)
        out += pack
        t += PACK_TICKS
    return bytes(out)
