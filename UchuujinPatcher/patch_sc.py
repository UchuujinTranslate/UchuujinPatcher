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

# from UchuujinPatcher.config_handling import config
# config = config()


def patch_sc():
    start_time = time.time()

    sc_dir = "work/isofiles/sc/"
    scripts = "work/repos/weblate/scripts/"
    patched_dir = "work/isofiles/sc_patched/"
    scripts_tmp = "work/repos/weblate/scripts/temp/"

    try:
        os.makedirs(patched_dir)
    except FileExistsError:
        print("Dir already exists")

    multiThreaded = True

    # preparation
    filenames = []
    for filename in os.listdir(sc_dir):
        filenames.append(filename)
    print(filenames)

    def writeEBootPointers():
        # do this work after patching translations
        eboot = open("work/isofiles/EBOOT_patched.BIN", "r+b")
        newScOffset = 0
        ptrOff = 0x147044
        eboot.seek(ptrOff, 0)

        # print(f'writing for {filename}')
        newScSize = os.path.getsize(
            patched_dir+filename)  # get new sc size
        eboot.write(struct.pack("<HH", newScOffset >> 11, newScSize >> 11))
        newScOffset += newScSize

    # multithreaded version, ran 3 secs total!
    if multiThreaded:
        print("Multithreaded!")

        with Pool() as pool:
            pool.map(patch_translations, filenames)

        # calculate new pointer sc.cpk
        print("Writing eboot pointers")
        for filename in filenames:
            writeEBootPointers()

    # old single threaded version, 18 secs
    else:
        for filename in os.listdir(sc_dir):
            print(f"Patching {filename}...")
            patch_translations(filename)
        writeEBootPointers()

    elapsed_time = time.time() - start_time
    print('sc patch time:', time.strftime(
        "%H:%M:%S", time.gmtime(elapsed_time)))


if __name__ == "__main__":
    patch_sc()
