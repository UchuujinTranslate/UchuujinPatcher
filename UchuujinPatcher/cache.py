# Tracks whether the files extracted from the original iso (work/isofiles)
# are still valid, so they can be reused between runs.

import hashlib
import json
import os

try:
    from UchuujinPatcher import decompress_iso
except ImportError:
    import decompress_iso

STAMP_PATH = "work/cache_stamp.json"
CGS_META_PATH = "UchuujinPatcher/union/cgs.json"

# Bump when the extraction scripts change in a way that makes old extracted
# files wrong, to force a rebuild.
CACHE_VERSION = 1

# Everything in work/isofiles that only depends on the original iso.
# Anything else in there is build output and is deleted before each run.
KEEP = {
    "ICON0.PNG", "sc.cpk", "union.cpk", "EBOOT.BIN", "lt.bin", "pr.bin",
    "EBOOT_DEC.BIN", "sc", "union", "cgs", "pr", "pr_cgs",
}


def _file_hash(path):
    md5 = hashlib.md5()
    with open(path, "rb") as f:
        md5.update(f.read())
    return md5.hexdigest()


def current_stamp():
    iso_name = decompress_iso.find_iso()
    if iso_name is None:
        return None
    st = os.stat(iso_name)
    return {
        "version": CACHE_VERSION,
        "iso": iso_name,
        "iso_size": st.st_size,
        "iso_mtime_ns": st.st_mtime_ns,
        "cgs_meta": _file_hash(CGS_META_PATH),
    }


def is_valid():
    """True if work/isofiles was built from the current iso and scripts."""
    try:
        with open(STAMP_PATH) as f:
            saved = json.load(f)
    except (OSError, ValueError):
        return False
    if saved != current_stamp():
        return False
    return all(os.path.exists("work/isofiles/" + name) for name in KEEP)


def write_stamp():
    stamp = current_stamp()
    if stamp is not None:
        with open(STAMP_PATH, "w") as f:
            json.dump(stamp, f, indent=2)
