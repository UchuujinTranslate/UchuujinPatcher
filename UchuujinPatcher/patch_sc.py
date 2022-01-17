# Call sc_patch_translations.py from main repo
# Patches in English text into scripts

# Multiprocess or implement looping through all in 
# normal script
# Implement it normal first, then add multiprocessing

import os
import shutil

pack_dir = "isofiles/pack/"
scripts = "repos/weblate/scripts/"
patched_dir = "isofiles/pack_patched/"

try:
    os.mkdir(patched_dir)
except FileExistsError:
    print("Dir already exists")

for filename in os.listdir(pack_dir):
    # Call as python command right now, but later on, 
    # import as a module for better flexibility and speed, 
    # requires modifying / integrating extraction tool code
    print(f"Patching {filename}...")
    os.system(
        f"py main_src/sc/sc_patch_translations.py \
         {pack_dir}{filename} \
         {scripts}{filename}.json \
         {scripts}en_US/{filename}.po")
    
    shutil.move(filename, patched_dir)
    
    # input("Waiting for input")
    
    
