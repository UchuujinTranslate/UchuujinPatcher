# Use this file to structure the project and
# be the main way to order the scripts
# mpX = multiprocessing

# Order:
# config - Check if exists, if not, go into creation process
# setup

# Setup process, could run together
# mp1 - clone_repo
# mp1 - decompress_iso

# The rest must be in order roughly
# cpk_dump
# mp2 - patch_eboot
# mp2 - patch_sc
# cpk_pack
# replace_iso
# create_binary_patch
# distrib

import argparse
import os

import UchuujinPatcher.create_binary_patch
import UchuujinPatcher.replace_iso
import UchuujinPatcher.pr_pack
import UchuujinPatcher.union_pack
import UchuujinPatcher.union.union_cgs_insert
import UchuujinPatcher.cpk_pack
import UchuujinPatcher.adjust_width_font
import UchuujinPatcher.patch_lt
import UchuujinPatcher.patch_eboot
import UchuujinPatcher.pr_dump
import UchuujinPatcher.cpk_dump
import UchuujinPatcher.decompress_iso
import UchuujinPatcher.clone_repo
import UchuujinPatcher.cleanup
import UchuujinPatcher.cache
import UchuujinPatcher.font_patch

import UchuujinPatcher.union_dump
import UchuujinPatcher.union.union_cgs_extract
from UchuujinPatcher import console

parser = argparse.ArgumentParser(description="Build the Uchuujin English patch.")
parser.add_argument("--clean", action="store_true",
                    help="delete everything (including cloned repos and "
                         "files extracted from the iso) and rebuild from scratch")
args = parser.parse_args()


def run_sc_patch():
    # multiprocessing scripts must launch on their own to function properly
    # launching as a function will cause main.py to run constantly
    os.system("py UchuujinPatcher/patch_sc.py")
    # old way
    # import UchuujinPatcher.patch_sc
    # UchuujinPatcher.patch_sc.patch_sc()


def copy_translated_images():
    UchuujinPatcher.union.union_cgs_extract.copy_cgs_translated()
    UchuujinPatcher.pr_dump.copy_pr_translated()


# Files extracted from the original iso don't change between runs, so these
# steps (marked cached=True) are skipped while the cache is still valid.
use_cache = not args.clean and UchuujinPatcher.cache.is_valid()

P = UchuujinPatcher
steps = [
    # (title, function, only depends on the original iso)
    ("Cleaning previous build",
     lambda: P.cleanup.del_last_ver(clean=args.clean, keep_cache=use_cache), False),
    ("Updating translation repositories", P.clone_repo.clone_repos, False),
    ("Extracting game files from ISO", P.decompress_iso.decompress_iso, True),
    ("Unpacking sc.cpk", P.cpk_dump.cpk_dump, True),
    ("Unpacking union.cpk", P.union_dump.union_dump, True),
    ("Extracting CG images", P.union.union_cgs_extract.cgs_extract, True),
    ("Unpacking pr.bin", P.pr_dump.pr_dump, True),
    ("Decrypting EBOOT", P.patch_eboot.decrypt_eboot, True),
    ("Copying translated images", copy_translated_images, False),
    ("Patching EBOOT", P.patch_eboot.patch_eboot, False),
    ("Patching lt.bin", P.patch_lt.patch_lt, False),
    ("Adjusting font widths", P.adjust_width_font.adjust_width_font, False),
    ("Redrawing punctuation glyphs", P.font_patch.patch_font, False),
    ("Patching scripts (sc)", run_sc_patch, False),
    ("Packing sc.cpk", P.cpk_pack.cpk_pack_sc, False),
    ("Inserting CG images", P.union.union_cgs_insert.cgs_insert, False),
    ("Packing union.cpk", P.union_pack.cpk_pack_union, False),
    ("Packing pr.bin", P.pr_pack.pr_pack, False),
    ("Building patched ISO", P.replace_iso.replace_iso, False),
    ("Creating distributable patch", P.create_binary_patch.create_binary_patch, False),
]
last_cached = max(i for i, step in enumerate(steps) if step[2])

total_timer = console.Timer()
console.banner("Uchuujin English Patcher")
if args.clean:
    console.info("--clean: rebuilding everything from scratch")
elif use_cache:
    console.info("Original ISO unchanged: reusing previously extracted files")
else:
    console.info("No valid cache: extracting files from the ISO")

timings = []
for index, (title, func, cached) in enumerate(steps):
    console.step(index + 1, len(steps), title)
    if cached and use_cache:
        console.ok("Skipped, using cached files")
        timings.append((title, "cached  "))
        continue
    timer = console.Timer()
    func()
    timings.append((title, timer.elapsed()))
    console.ok(f"Finished in {timer.elapsed()}")
    if index == last_cached:
        UchuujinPatcher.cache.write_stamp()

console.banner("All done!")
for title, took in timings:
    print(f"  {took}  {title}")
print()
print(f"  Total execution time: {total_timer.elapsed()}")
