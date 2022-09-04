# Most likely use UMD-replace here
# Look into compiling for other OS's

# Replace changed files back into original game iso
# Make copy of game iso

# Use?
# https://clalancette.github.io/pycdlib/example-modifying-file-in-place.html
from shutil import copyfile, rmtree
import os


def replace_iso():
    # Create duplicate of original .iso for patching.
    print("Copying game iso")
    isoName = "2668 - Nichijou - Uchuujin (Japan) (v1.01).iso"
    copyfile(isoName, "NichiPatched.iso")

    # Possible english translation icon replacement?
    print("Replacing ICON0.PNG")
    os.system("bin\\UMD-replace.exe NichiPatched.iso PSP_GAME/ICON0.PNG UchuujinPatcher/NEW_ICON0.PNG")

    # Replace sc.cpk with patched version.
    print("Replacing sc.cpk")
    os.system("bin\\UMD-replace.exe NichiPatched.iso PSP_GAME/USRDIR/DATA/sc.cpk isofiles/new_sc.cpk")

    # Replace EBOOT.BIN with patched version.
    print("Replacing EBOOT.BIN")
    os.system("bin\\UMD-replace.exe NichiPatched.iso PSP_GAME/SYSDIR/EBOOT.BIN isofiles/EBOOT_patched.BIN")
    # Replace lt.bin with patched version.
    print("Replacing lt.bin")
    os.system("bin\\UMD-replace.exe NichiPatched.iso PSP_GAME/USRDIR/DATA/lt.bin isofiles/lt_patched.bin")


if __name__ == "__main__":
    replace_iso()
