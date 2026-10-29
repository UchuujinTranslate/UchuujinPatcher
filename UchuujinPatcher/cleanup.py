import os
import shutil
import stat
try:
    from UchuujinPatcher import console
except ImportError:
    import console
try:
    from UchuujinPatcher import cache
except ImportError:
    import cache

# --------------------------- Delete old versions --------------------------- #
# Files that only depend on the original iso (and the git repos) are kept
# between runs, see cache.py. Everything the patcher builds is removed.


# needed for deleting read-only files in .git
def on_rm_error(func, path, exc_info):
    # path contains the path of the file that couldn't be removed
    # let's just assume that it's read-only and unlink it.
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)


def remove(path, label=None):
    """Remove a file or directory. Returns True if something was removed."""
    try:
        if os.path.isdir(path):
            shutil.rmtree(path, onerror=on_rm_error)
        else:
            os.remove(path)
    except FileNotFoundError:
        return False
    if label:
        console.info(f"Removed {label}")
    return True


def del_last_ver(clean=False, keep_cache=False):
    """Prepare for a new build.

    clean:      delete everything, including the cloned repos.
    keep_cache: keep the files extracted from the original iso."""
    if clean:
        remove("work", "work/ (full clean)")
    elif keep_cache:
        # keep only what comes from the original iso
        isofiles = "work/isofiles"
        removed = 0
        for name in os.listdir(isofiles):
            if name not in cache.KEEP:
                remove(os.path.join(isofiles, name))
                removed += 1
        console.info(f"Removed {removed} build files from work/isofiles, "
                     "kept extracted iso files")
    else:
        remove(cache.STAMP_PATH)
        remove("work/isofiles", "stale work/isofiles")

    remove("output", "output/")
    remove("NichiPatched.iso", "old NichiPatched.iso")


if __name__ == "__main__":
    del_last_ver()
