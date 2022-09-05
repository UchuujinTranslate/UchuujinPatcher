# Script for decompressing original game iso

import pycdlib
import os

def decompress_iso():
    # Make dir
    print("Making isofiles directory")
    os.mkdir("work/isofiles")
    
    iso_name = None
    
    # iterating over all iso files
    for file in os.listdir(os.getcwd()):
        if file.endswith('.iso'):
            print("Found: " + file) 
            iso_response = input("Is this the correct original .iso? (Y/N) ")
            if iso_response.lower() == 'y':
                iso_name = file
                break
    if iso_name == None:
        print("Could not find .iso! Exiting.")
        quit()

    print("Extracting files from original iso...")
    #iso_name = "2668 - Nichijou - Uchuujin (Japan) (v1.01).iso"
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
    iso.get_file_from_iso(
        "work/isofiles/union.cpk", iso_path='/PSP_GAME/USRDIR/DATA/union.cpk')
    iso.close()


if __name__ == "__main__":
    decompress_iso()
