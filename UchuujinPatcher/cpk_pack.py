# Pack modified sc scripts back into sc.cpk

# Use CriPakTools here again.
# for %%f in (*) do ..\..\executables\CriPakTools.exe ..\..\temp_pack\sc.cpk %%f ..\..\cpkdumps\sc\%%f && ECHO Put %%f file into "sc.cpk".
import os
from shutil import copyfile, rmtree


def cpk_pack_sc():
    os.system("bin\\crifilesystem\\cpkmakec.exe work/isofiles/sc_patched -mode=ID -mask work/isofiles/new_sc.cpk")
    #sc_dir = "sc_patched/"
    #scripts = "weblate_scripts/"
    #
    #copyfile("bin/CriPakTools.exe", "work/isofiles/CriPakTools.exe")
    #copyfile("work/isofiles/sc.cpk", "work/isofiles/new_sc.cpk")
    #
    ## Must execute in same dir as well
    #cwd = os.getcwd()
    #os.chdir("work/isofiles/")
    #
    #
    #
    #for filename in os.listdir(sc_dir):
    #    print(f"Packing {filename}...")
    #    os.system(f"CriPakTools.exe new_sc.cpk {filename} {sc_dir}{filename}")
    #    
    ## Delete tool
    #os.remove("CriPakTools.exe")
    #
    ## Go back to root dir
    ## print(cwd)
    #os.chdir(cwd)


if __name__ == "__main__":
    cpk_pack_sc()
