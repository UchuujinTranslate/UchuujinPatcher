# Call sc_patch_translations.py from main repo
# Patches in English text into scripts

# Multiprocess or implement looping through all in 
# normal script
# Implement it normal first, then add multiprocessing

import os
import shutil
import struct
from UchuujinPatcher.sc.sc_patch_translations_tmp import patch_translations

def patch_sc():
    sc_dir = "work/isofiles/sc/"
    scripts = "work/repos/weblate/scripts/"
    patched_dir = "work/isofiles/sc_patched/"
    scripts_tmp = "work/repos/weblate/scripts/temp/"
    try:
        os.mkdir(patched_dir)
    except FileExistsError:
        print("Dir already exists")

    #calculate new pointer sc.cpk
    eboot = open("work/isofiles/EBOOT_patched.BIN", "r+b")
    newScOffset = 0
    ptrOff = 0x147044
    eboot.seek(ptrOff,0)
    for filename in os.listdir(sc_dir):
        # Call as python command right now, but later on, 
        # import as a module for better flexibility and speed, 
        # requires modifying / integrating extraction tool code
        print(f"Patching {filename}...")
        patch_translations(sc_dir + filename,
                           scripts_tmp + filename + ".json",
                           scripts + "en_US/" + filename + ".po", 
                           patched_dir,
                           scripts + filename + ".json"
                           )
        
        # os.system(
        #     f"py UchuujinPatcher/sc/sc_patch_translations_tmp.py \
        #     {pack_dir}{filename} \
        #     {scripts_tmp}{filename}.json \
        #     {scripts}en_US/{filename}.po\
        #     {patched_dir}\
        #     {scripts}{filename}.json")
        newScSize =os.path.getsize(patched_dir+filename)#get new sc size
        eboot.write(struct.pack("<HH",newScOffset>>11,newScSize>>11))
        newScOffset+=newScSize

        #shutil.move(filename, patched_dir)#need original sc file for comparing
        
        # input("Waiting for input")
        
        
if __name__ == "__main__":
    patch_sc()
