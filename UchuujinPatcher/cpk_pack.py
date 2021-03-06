# Pack modified sc scripts back into sc.cpk

# Use CriPakTools here again.
# for %%f in (*) do ..\..\executables\CriPakTools.exe ..\..\temp_pack\sc.cpk %%f ..\..\cpkdumps\sc\%%f && ECHO Put %%f file into "sc.cpk".
import os
from shutil import copyfile, rmtree

pack_dir = "pack_patched/"
scripts = "weblate_scripts/"

copyfile("bin/CriPakTools.exe", "isofiles/CriPakTools.exe")
copyfile("isofiles/sc.cpk", "isofiles/new_sc.cpk")

# Must execute in same dir as well
cwd = os.getcwd()
os.chdir("isofiles/")



for filename in os.listdir(pack_dir):
    print(f"Packing {filename}...")
    os.system(f"CriPakTools.exe new_sc.cpk {filename} {pack_dir}{filename}")
    
# Delete tool
os.remove("CriPakTools.exe")

# Go back to root dir
# print(cwd)
os.chdir(cwd)
