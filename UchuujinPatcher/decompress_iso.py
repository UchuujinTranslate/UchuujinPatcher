# Script for decompressing original game iso

import pycdlib
import os


# Make dir
os.mkdir("isofiles")

iso_name = "2668 - Nichijou - Uchuujin (Japan) (v1.01).iso"

iso = pycdlib.PyCdlib()
iso.open(iso_name)

# Grab files
# (Will add more files when they are needed.)
iso.get_file_from_iso(
    "isofiles/ICON0.PNG", iso_path='/PSP_GAME/ICON0.PNG')
iso.get_file_from_iso(
    "isofiles/sc.cpk", iso_path='/PSP_GAME/USRDIR/DATA/sc.cpk')
iso.get_file_from_iso(
    "isofiles/EBOOT.BIN", iso_path='/PSP_GAME/SYSDIR/EBOOT.BIN')
iso.get_file_from_iso(
    "isofiles/lt.bin", iso_path='/PSP_GAME/USRDIR/lt.bin')
iso.close()
