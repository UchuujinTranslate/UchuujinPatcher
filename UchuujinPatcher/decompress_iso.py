# Script for decompressing original game iso

import pycdlib
import os
try:
    from UchuujinPatcher import console
except ImportError:
    import console

# replace_iso.py and create_binary_patch.py expect this exact name
EXPECTED_ISO = "Nichijou - Uchuujin (Japan).iso"


def find_iso():
    """Name of the original iso in the working directory, or None."""
    isos = [f for f in os.listdir(os.getcwd()) if f.endswith('.iso')]
    if not isos:
        return None
    return EXPECTED_ISO if EXPECTED_ISO in isos else isos[0]


def decompress_iso():
    iso_name = find_iso()
    if iso_name is None:
        console.error("Could not find .iso! Exiting.")
        quit()
    if iso_name != EXPECTED_ISO:
        console.warn(f"Using {iso_name}, expected {EXPECTED_ISO}")

    # Make dir
    console.info("Creating work/isofiles directory")
    os.makedirs("work/isofiles")

    console.info("Reading " + iso_name)
    #iso_name = "2668 - Nichijou - Uchuujin (Japan) (v1.01).iso"
    iso = pycdlib.PyCdlib()
    iso.open(iso_name)
    


    # Grab files
    # (Will add more files when they are needed.)
    console.info("Extracting ICON0.PNG")
    iso.get_file_from_iso(
        "work/isofiles/ICON0.PNG", iso_path='/PSP_GAME/ICON0.PNG')
    console.info("Extracting sc.cpk")
    iso.get_file_from_iso(
        "work/isofiles/sc.cpk", iso_path='/PSP_GAME/USRDIR/DATA/sc.cpk')
    console.info("Extracting union.cpk")
    iso.get_file_from_iso(
        "work/isofiles/union.cpk", iso_path='/PSP_GAME/USRDIR/DATA/union.cpk')
    console.info("Extracting EBOOT.BIN")
    iso.get_file_from_iso(
        "work/isofiles/EBOOT.BIN", iso_path='/PSP_GAME/SYSDIR/EBOOT.BIN')
    console.info("Extracting lt.bin")
    iso.get_file_from_iso(
        "work/isofiles/lt.bin", iso_path='/PSP_GAME/USRDIR/DATA/lt.bin')
    console.info("Extracting pr.bin")
    iso.get_file_from_iso(
        "work/isofiles/pr.bin", iso_path='/PSP_GAME/USRDIR/DATA/pr.bin')
    
    iso.close()


if __name__ == "__main__":
    decompress_iso()
