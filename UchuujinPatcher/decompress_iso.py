# Script for decompressing original game iso

import pycdlib
import os

def decompress_iso():
    # Make dir
    print("Making isofiles directory")
    os.mkdir("work/isofiles")

    print("Extracting files from original iso...")
    iso_name = "2668 - Nichijou - Uchuujin (Japan) (v1.01).iso"
    iso = pycdlib.PyCdlib()
    iso.open(iso_name)

    # Grab files
    # (Will add more files when they are needed.)
    print("Extracting ICON0.PNG")
    iso.get_file_from_iso(
        "work/isofiles/ICON0.PNG", iso_path='/PSP_GAME/ICON0.PNG')
    print("Extracting sc.cpk")
    iso.get_file_from_iso(
        "work/isofiles/sc.cpk", iso_path='/PSP_GAME/USRDIR/DATA/sc.cpk')
    print("Extracting EBOOT.BIN")
    iso.get_file_from_iso(
        "work/isofiles/EBOOT.BIN", iso_path='/PSP_GAME/SYSDIR/EBOOT.BIN')
    print("Extracting lt.bin")
    iso.get_file_from_iso(
        "work/isofiles/lt.bin", iso_path='/PSP_GAME/USRDIR/DATA/lt.bin')
    iso.close()


if __name__ == "__main__":
    decompress_iso()
