# Call sc_patch_translations.py from main repo
# Patches in English text into scripts

# Multiprocess or implement looping through all in
# normal script
# Implement it normal first, then add multiprocessing

import os
from sc.sc_patch_translations_tmp import patch_translations
from multiprocessing import Pool
import time
import struct

try:
    from UchuujinPatcher import console
except ImportError:
    import console
from sc import text_layout

# from UchuujinPatcher.config_handling import config
# config = config()


def report_overflow(records):
    """Write reports about messages that needed special handling.

    work/split_report.txt lists the messages that were split into two boxes,
    work/layout_report.txt the ones that still don't fit."""
    records.sort(key=lambda o: (o["file"], o["id"]))
    splits = [o for o in records if o.get("kind") == "split"]
    overflow = [o for o in records if o.get("kind", "overflow") == "overflow"]

    if splits:
        report = "work/split_report.txt"
        with open(report, "w", encoding="utf-8") as f:
            f.write(f"{len(splits)} messages were too long for one text box "
                    "and are shown as two boxes.\n"
                    "sc/NNNN is the script number, id the message in it.\n\n")
            for o in splits:
                f.write(f"sc/{o['file']} id {o['id']} - {o['speaker']}\n"
                        f"{o['text']}\n\n")
        console.info(f"{len(splits)} long messages split into two boxes, "
                     f"see {report}")

    if not overflow:
        console.ok("All translated messages fit in the text box")
        return
    report = "work/layout_report.txt"
    with open(report, "w", encoding="utf-8") as f:
        f.write(f"{len(overflow)} messages need more than "
                f"{text_layout.MAX_LINES} lines and will overflow the box.\n"
                "They need to be shortened or split in the translation.\n\n")
        for o in overflow:
            f.write(f"sc/{o['file']} id {o['id']} ({o['lines']} lines, "
                    f"about {o['excess']} characters too long)\n"
                    f"{o['text']}\n\n")
    console.warn(f"{len(overflow)} messages are too long for the text box, "
                 f"see {report}")


def patch_sc():
    start_time = time.time()

    sc_dir = "work/isofiles/sc/"
    # scripts = "work/repos/weblate/scripts/"
    patched_dir = "work/isofiles/sc_patched/"
    # scripts_tmp = "work/repos/weblate/scripts/temp/"

    try:
        os.makedirs(patched_dir)
    except FileExistsError:
        console.warn("sc_patched directory already exists")

    multiThreaded = True

    # preparation
    filenames = []
    for filename in os.listdir(sc_dir):
        filenames.append(filename)
    console.info(f"Patching {len(filenames)} script files")

    def writeEBootPointers():
        # do this work after patching translations
        eboot = open("work/isofiles/EBOOT_patched.BIN", "r+b")
        newScOffset = 0
        ptrOff = 0x147044
        eboot.seek(ptrOff, 0)

        for filename in filenames:
            # print(f'writing for {filename}')
            newScSize = os.path.getsize(
                patched_dir+filename)  # get new sc size
            eboot.write(struct.pack("<HH", newScOffset >> 11, newScSize >> 11))
            newScOffset += newScSize

    # multithreaded version, ran 3 secs total!
    if multiThreaded:
        with Pool() as pool:
            console.info(f"Using {pool._processes} worker processes")
            done = 0
            overflow = []
            for result in pool.imap_unordered(patch_translations, filenames):
                overflow.extend(result or [])
                done += 1
                console.progress(done, len(filenames), "scripts")
        report_overflow(overflow)

        # calculate new pointer sc.cpk
        console.info("Writing eboot pointers")
        writeEBootPointers()

    # old single threaded version, 18 secs
    else:
        overflow = []
        for done, filename in enumerate(os.listdir(sc_dir), 1):
            overflow.extend(patch_translations(filename) or [])
            console.progress(done, len(filenames), "scripts")
        report_overflow(overflow)
        writeEBootPointers()

    elapsed_time = time.time() - start_time
    console.ok(f"Scripts patched in {console.format_time(elapsed_time)}")


if __name__ == "__main__":
    patch_sc()
