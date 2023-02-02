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
    os.makedirs(os.path.dirname("output/"), exist_ok=True)
    copyfile(isoName, "output/NichiPatched.iso")

    # Possible english translation icon replacement?
    print("Replacing ICON0.PNG")
    os.system(
        "bin\\UMD-replace.exe output/NichiPatched.iso PSP_GAME/ICON0.PNG UchuujinPatcher/extra_files/NEW_ICON0.PNG")

    # Replace sc.cpk with patched version.
    print("Replacing sc.cpk")
    os.system(
        "bin\\UMD-replace.exe output/NichiPatched.iso PSP_GAME/USRDIR/DATA/sc.cpk work/isofiles/new_sc.cpk")
    
    # Replace union.cpk with patched version.
    print("Replacing union.cpk")
    os.system(
        "bin\\UMD-replace.exe output/NichiPatched.iso PSP_GAME/USRDIR/DATA/union.cpk work/isofiles/new_union.cpk")

    # Replace EBOOT.BIN with patched version.
    print("Replacing EBOOT.BIN")
    os.system(
        "bin\\UMD-replace.exe output/NichiPatched.iso PSP_GAME/SYSDIR/EBOOT.BIN work/isofiles/EBOOT_patched.BIN")
    # Replace lt.bin with patched version.
    print("Replacing lt.bin")
    os.system(
        "bin\\UMD-replace.exe output/NichiPatched.iso PSP_GAME/USRDIR/DATA/lt.bin work/isofiles/lt_patched.bin")
    print("Replacing pr.bin")
    os.system(
        "bin\\UMD-replace.exe output/NichiPatched.iso PSP_GAME/USRDIR/DATA/pr.bin work/isofiles/pr_patched.bin")


if __name__ == "__main__":
    replace_iso()
