# The game's four movies (op, yokoku, koutyou, ed) are PMF files stored
# outside the cpks. This module
#  * extracts them from the original iso and converts them to MP4, so they can
#    be edited (movies/original/<name>.mp4)
#  * turns edited videos from movies/translated/<name>.mp4 back into PMF files
#    and gives them to replace_iso
#
# Only the picture is replaced. The audio of the original movie is kept
# bit for bit, so an edited video has to run as long as the original (the
# frame count is padded or cut to match).
#
#   py UchuujinPatcher/movies.py extract [name ...]
#   py UchuujinPatcher/movies.py build [name ...]
import hashlib
import json
import os
import subprocess
import sys

try:
    from UchuujinPatcher import console, pmf_mux, video_tools
    from UchuujinPatcher import decompress_iso
except ImportError:
    import console
    import pmf_mux
    import video_tools
    import decompress_iso

MOVIES = ["op", "yokoku", "koutyou", "ed"]
ISO_DIR = "/PSP_GAME/USRDIR/DATA/"
ISO_PATH = "PSP_GAME/USRDIR/DATA/"
ORIGINAL_PMF_DIR = "work/movies/original"
BUILT_DIR = "work/movies/built"
EDITABLE_DIR = "movies/original"
TRANSLATED_DIR = "movies/translated"
SOURCE_EXTENSIONS = (".mp4", ".mkv", ".mov", ".avi", ".webm")

# bump when the encoding or muxing changes, to rebuild cached movies
BUILD_VERSION = 1
WIDTH, HEIGHT = 480, 272
FRAME_RATE = "30000/1001"
# bytes the muxer adds on top of the video and audio payload
MUX_OVERHEAD = 0.015


def original_pmf(name):
    """Path of the original movie, extracted from the iso when missing."""
    path = f"{ORIGINAL_PMF_DIR}/{name}.pmf"
    if not os.path.exists(path):
        import pycdlib
        iso_name = decompress_iso.find_iso()
        if iso_name is None:
            raise FileNotFoundError("original iso not found")
        os.makedirs(ORIGINAL_PMF_DIR, exist_ok=True)
        iso = pycdlib.PyCdlib()
        iso.open(iso_name)
        try:
            iso.get_file_from_iso(path, iso_path=f"{ISO_DIR}{name}.pmf")
        finally:
            iso.close()
    return path


def extract_movies(names=MOVIES):
    """Extract movies from the iso and convert them to editable MP4 files."""
    os.makedirs(EDITABLE_DIR, exist_ok=True)
    for name in names:
        console.info(f"Extracting {name}.pmf")
        video_tools.pmf_to_mp4(original_pmf(name), f"{EDITABLE_DIR}/{name}.mp4")
    console.ok(f"Movies written to {EDITABLE_DIR}/")


def find_source(name):
    for ext in SOURCE_EXTENSIONS:
        path = f"{TRANSLATED_DIR}/{name}{ext}"
        if os.path.exists(path):
            return path
    return None


def file_hash(path):
    md5 = hashlib.md5()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            md5.update(block)
    return md5.hexdigest()


def encode_video(source, out_path, frames, bitrate_kbps):
    """Encode to the H.264 stream the PSP expects: Main profile, level 2.1,
    480x272 at 29.97 fps, no B-frames and an IDR every 59 frames."""
    ffmpeg = video_tools.find_ffmpeg()
    filters = (f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease:flags=lanczos,"
               f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FRAME_RATE},"
               f"tpad=stop_mode=clone:stop={frames},format=yuv420p")
    gop = pmf_mux.GOP_FRAMES
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", source,
           "-an", "-vf", filters, "-frames:v", str(frames),
           "-c:v", "libx264", "-profile:v", "main", "-level:v", "2.1",
           "-preset", "slow", "-crf", "17",
           "-maxrate", f"{bitrate_kbps}k", "-bufsize", f"{bitrate_kbps * 2}k",
           "-x264-params",
           f"aud=1:bframes=0:keyint={gop}:min-keyint={gop}:scenecut=0:ref=3:weightp=0",
           "-f", "h264", out_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, errors="replace")
    if result.returncode != 0:
        console.error(f"ffmpeg failed encoding {source}")
        for line in result.stdout.strip().splitlines()[-15:]:
            print(f"      {line}")
        raise RuntimeError("encoding failed")


def build_movie(name, source):
    """Encode source and mux it with the original audio into BUILT_DIR/name.pmf."""
    original = original_pmf(name)
    with open(original, "rb") as f:
        data = f.read()
    old_aus = pmf_mux.split_access_units(
        b"".join(p for s, _, p, _ in video_tools.iter_packets(data) if s == video_tools.VIDEO_ID))
    frames, params, audio_pts = video_tools.demux_audio(data)
    audio_bytes = len(frames) * pmf_mux.AUDIO_FRAME_BYTES
    # the picture has to fit in what the original movie leaves after its audio
    budget = len(data) * (1 - MUX_OVERHEAD) - 0x800 - audio_bytes
    duration = len(old_aus) * pmf_mux.FRAME_TICKS / pmf_mux.CLOCK
    bitrate = int(budget * 8 / duration / 1000)

    os.makedirs(BUILT_DIR, exist_ok=True)
    es_path = f"{BUILT_DIR}/{name}.h264"
    for attempt in range(4):
        console.info(f"Encoding {name} at up to {bitrate} kb/s "
                     f"({len(old_aus)} frames)")
        encode_video(source, es_path, len(old_aus), bitrate)
        with open(es_path, "rb") as f:
            aus = pmf_mux.split_access_units(f.read())
        pmf = pmf_mux.build_pmf(data[:0x800], aus, frames, params, audio_pts)
        if len(pmf) <= len(data):
            break
        console.warn(f"{name}.pmf is {len(pmf) - len(data)} bytes too large, "
                     "lowering the bitrate")
        bitrate = int(bitrate * 0.93)
    else:
        raise RuntimeError(f"could not fit {name} into {len(data)} bytes")
    os.remove(es_path)

    pmf = pmf_mux.patch_header(pmf[:0x800], len(old_aus), len(aus), len(pmf) - 0x800) + pmf[0x800:]
    with open(f"{BUILT_DIR}/{name}.pmf", "wb") as f:
        f.write(pmf)
    console.ok(f"{name}.pmf built ({len(pmf) / 1e6:.1f} MB, original {len(data) / 1e6:.1f} MB)")


def build_movies():
    """Build every movie that has an edited video in movies/translated/.

    Returns the names that were built (or reused from an earlier run)."""
    built = []
    for name in MOVIES:
        source = find_source(name)
        if source is None:
            continue
        stamp = {"version": BUILD_VERSION, "source": file_hash(source)}
        stamp_path = f"{BUILT_DIR}/{name}.json"
        pmf_path = f"{BUILT_DIR}/{name}.pmf"
        if os.path.exists(pmf_path) and os.path.exists(stamp_path):
            with open(stamp_path) as f:
                if json.load(f) == stamp:
                    console.info(f"{name}.pmf is up to date")
                    built.append(name)
                    continue
        build_movie(name, source)
        with open(stamp_path, "w") as f:
            json.dump(stamp, f)
        built.append(name)
    if not built:
        console.info(f"No edited movies in {TRANSLATED_DIR}/, keeping the originals")
    return built


def built_movies():
    """(iso path, file) of each movie replace_iso has to put into the iso."""
    return [(f"{ISO_PATH}{name}.pmf", f"{BUILT_DIR}/{name}.pmf")
            for name in MOVIES
            if find_source(name) and os.path.exists(f"{BUILT_DIR}/{name}.pmf")]


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    chosen = sys.argv[2:] or MOVIES
    if command == "extract":
        extract_movies(chosen)
    elif command == "build":
        build_movies()
    else:
        print(__doc__)
