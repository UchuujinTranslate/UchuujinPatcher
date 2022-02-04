# Call sc_patch_translations.py from main repo
# Patches in English text into scripts

# Multiprocess or implement looping through all in 
# normal script
# Implement it normal first, then add multiprocessing

import os
import shutil
import struct

pack_dir = "isofiles/pack/"
scripts = "repos/weblate/scripts/"
patched_dir = "isofiles/pack_patched/"
scripts_tmp = "repos/weblate/scripts/temp/"
try:
    os.mkdir(patched_dir)
except FileExistsError:
    print("Dir already exists")

#calculate new pointer sc.cpk
eboot = open("isofiles/EBOOT_patched.BIN","r+b")
newScOffset = 0
ptrOff = 0x147044
eboot.seek(ptrOff,0)
for filename in os.listdir(pack_dir):
    # Call as python command right now, but later on, 
    # import as a module for better flexibility and speed, 
    # requires modifying / integrating extraction tool code
    print(f"Patching {filename}...")
    os.system(
        f"py main_src/sc/sc_patch_translations_tmp.py \
         {pack_dir}{filename} \
         {scripts_tmp}{filename}.json \
         {scripts}en_US/{filename}.po\
         {patched_dir}\
         {scripts}{filename}.json")
    newScSize =os.path.getsize(patched_dir+filename)#get new sc size
    eboot.write(struct.pack("<HH",newScOffset>>11,newScSize>>11))
    newScOffset+=newScSize

    #shutil.move(filename, patched_dir)#need original sc file for comparing
    
    # input("Waiting for input")
    
    
