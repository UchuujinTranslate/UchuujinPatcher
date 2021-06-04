# Pack modified sc scripts back into sc.cpk

# Use CriPakTools here again.
# for %%f in (*) do ..\..\executables\CriPakTools.exe ..\..\temp_pack\sc.cpk %%f ..\..\cpkdumps\sc\%%f && ECHO Put %%f file into "sc.cpk".
import os
from shutil import copyfile, rmtree

pack_dir = "pack/"
scripts = "weblate_scripts/"

copyfile("bin/CriPakTools.exe", "isofiles/CriPakTools.exe")


# Must execute in same dir as well
cwd = os.getcwd()
os.chdir("isofiles/")



for filename in os.listdir(pack_dir):
    # Call as python command right now, but later on,
    # import as a module for better flexibility and speed,
    # requires modifying main repo's code
    print(f"Packing {filename}...")
    os.system(f"CriPakTools.exe sc.cpk {filename} pack/{filename} new_sc.cpk")

# Delete tool
os.remove("CriPakTools.exe")

# Go back to root dir
# print(cwd)
os.chdir(cwd)
