# Reading the game's PMF (PSMF) movies: split them into H.264 video and
# ATRAC3+ audio, and convert them to MP4 with ffmpeg.
#
# Layout of a PMF, as found in this game:
#   0x000-0x7FF  PSMF header
#   0x800-       MPEG-PS packs of 2048 bytes
#                 0xE0 video PES (H.264 Main, 480x272, 29.97 fps)
#                 0xBD audio PES (ATRAC3+, 4 byte private header + frames)
#   Each audio frame is an 8 byte header (0F D0 pp pp 00 00 00 00, where pppp
#   holds the sample rate, channels and frame size) and 744 bytes of data.
import glob
import os
import re
import shutil
import struct
import subprocess

try:
    from UchuujinPatcher import console
except ImportError:
    import console

PES_START = b"\x00\x00\x01"
VIDEO_ID = 0xE0
AUDIO_ID = 0xBD
PACK_ID = 0xBA
# 90 kHz clock used by PES timestamps
CLOCK = 90000


def find_ffmpeg(name="ffmpeg"):
    """Path to ffmpeg/ffprobe: PATH first, then the winget install folder."""
    found = shutil.which(name)
    if found:
        return found
    local = os.environ.get("LOCALAPPDATA", "")
    pattern = os.path.join(local, "Microsoft", "WinGet", "Packages",
                           "Gyan.FFmpeg*", "ffmpeg-*", "bin", name + ".exe")
    hits = sorted(glob.glob(pattern))
    if hits:
        return hits[-1]
    raise FileNotFoundError(
        name + " not found. Install it with: winget install Gyan.FFmpeg")


def read_pts(b):
    """33 bit timestamp from the 5 byte PES encoding."""
    return (((b[0] >> 1) & 7) << 30 | b[1] << 22 | (b[2] >> 1) << 15
            | b[3] << 7 | b[4] >> 1)


def iter_packets(data):
    """Yield (stream_id, offset, payload, pts or None) for each PES packet."""
    pos = 0x800
    end = len(data) - 6
    while pos < end:
        if data[pos:pos + 3] != PES_START:
            pos += 1
            continue
        sid = data[pos + 3]
        if sid == PACK_ID:
            pos += 14 + (data[pos + 13] & 7)
            continue
        if sid < 0xBB:
            pos += 1
            continue
        length = struct.unpack(">H", data[pos + 4:pos + 6])[0]
        if sid in (VIDEO_ID, AUDIO_ID):
            header_len = data[pos + 8]
            pts = read_pts(data[pos + 9:pos + 14]) if data[pos + 7] & 0x80 else None
            yield sid, pos, data[pos + 9 + header_len:pos + 6 + length], pts
        pos += 6 + length


def demux_audio(data):
    """ATRAC3+ frame data, the 2 byte codec parameters and the first PTS."""
    stream = bytearray()
    first_pts = None
    for sid, _, payload, pts in iter_packets(data):
        if sid != AUDIO_ID:
            continue
        if first_pts is None and pts is not None:
            first_pts = pts
        stream += payload[4:]
    frames = []
    params = None
    pos = stream.find(b"\x0f\xd0")
    while 0 <= pos < len(stream) - 8:
        params = bytes(stream[pos + 2:pos + 4])
        size = (struct.unpack(">H", params)[0] & 0x3FF) * 8 + 8
        frames.append(bytes(stream[pos + 8:pos + 8 + size]))
        pos += 8 + size
    return frames, params, first_pts


def write_oma(path, frames, params):
    """Sony OMA container so ffmpeg can decode the audio."""
    header = bytearray(96)
    header[0:4] = b"EA3\x01"
    header[4] = 0
    header[5] = 96
    header[6:8] = b"\xff\xff"
    header[32] = 1  # ATRAC3+
    header[33] = 0
    header[34:36] = params
    with open(path, "wb") as f:
        # ffmpeg looks for an ID3-style "ea3" tag (empty here) before the header
        f.write(b"ea3\x03\x00\x00\x00\x00\x00\x00")
        f.write(header)
        for frame in frames:
            f.write(frame)


def pmf_to_mp4(pmf_path, mp4_path):
    ffmpeg = find_ffmpeg()
    with open(pmf_path, "rb") as f:
        data = f.read()
    frames, params, audio_pts = demux_audio(data)
    video_pts = next(p for s, _, _, p in iter_packets(data)
                     if s == VIDEO_ID and p is not None)
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", pmf_path]
    if frames:
        oma = mp4_path + ".oma"
        write_oma(oma, frames, params)
        # the audio PES starts a little before the first video frame
        cmd += ["-itsoffset", "%.4f" % ((audio_pts - video_pts) / CLOCK), "-i", oma,
                "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-c:v", "copy", "-movflags", "+faststart", mp4_path]
    try:
        console.run(cmd, "ffmpeg " + os.path.basename(mp4_path))
    finally:
        if frames and os.path.exists(mp4_path + ".oma"):
            os.remove(mp4_path + ".oma")


if __name__ == "__main__":
    import sys
    pmf_to_mp4(sys.argv[1], sys.argv[2])
