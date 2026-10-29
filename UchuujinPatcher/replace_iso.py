# Most likely use UMD-replace here
# Look into compiling for other OS's

# Replace changed files back into original game iso
# Make copy of game iso

# Use?
# https://clalancette.github.io/pycdlib/example-modifying-file-in-place.html
from shutil import copyfile, rmtree
import os
try:
    from UchuujinPatcher import console, movies
except ImportError:
    import console
    import movies


def replace_iso():
    # Create duplicate of original .iso for patching.
    console.info("Copying original ISO to output/NichiPatched.iso")
    isoName = "Nichijou - Uchuujin (Japan).iso"
    os.makedirs(os.path.dirname("output/"), exist_ok=True)
    copyfile(isoName, "output/NichiPatched.iso")

    # Possible english translation icon replacement?
    console.info("Replacing ICON0.PNG")
    console.run(
        "bin\\UMD-replace.exe output/NichiPatched.iso PSP_GAME/ICON0.PNG UchuujinPatcher/extra_files/NEW_ICON0.PNG")

    # Replace sc.cpk with patched version.
    console.info("Replacing sc.cpk")
    console.run(
        "bin\\UMD-replace.exe output/NichiPatched.iso PSP_GAME/USRDIR/DATA/sc.cpk work/isofiles/new_sc.cpk")
    
    # # Replace union.cpk with patched version.
    console.info("Replacing union.cpk")
    console.run(
        "bin\\UMD-replace.exe output/NichiPatched.iso PSP_GAME/USRDIR/DATA/union.cpk work/isofiles/new_union.cpk")

    # Replace EBOOT.BIN with patched version.
    console.info("Replacing EBOOT.BIN")
    console.run(
        "bin\\UMD-replace.exe output/NichiPatched.iso PSP_GAME/SYSDIR/EBOOT.BIN work/isofiles/EBOOT_patched.BIN")
    
    # Replace lt.bin with patched version.
    console.info("Replacing lt.bin")
    console.run(
        "bin\\UMD-replace.exe output/NichiPatched.iso PSP_GAME/USRDIR/DATA/lt.bin work/isofiles/lt_patched.bin")
    
    console.info("Replacing pr.bin")
    console.run(
        "bin\\UMD-replace.exe output/NichiPatched.iso PSP_GAME/USRDIR/DATA/pr.bin work/isofiles/pr_patched.bin")

    # Edited movies from movies/translated/, see movies.py
    for iso_path, movie in movies.built_movies():
        console.info(f"Replacing {os.path.basename(iso_path)}")
        console.run(f"bin\\UMD-replace.exe output/NichiPatched.iso {iso_path} {movie}")


if __name__ == "__main__":
    replace_iso()
