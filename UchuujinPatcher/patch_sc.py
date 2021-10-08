# Call sc_patch_translations.py from main repo
# Patches in English text into scripts

# Multiprocess or implement looping through all in 
# normal script
# Implement it normal first, then add multiprocessing

import os

pack_dir = "isofiles/pack/"
scripts = "weblate_scripts/"

for filename in os.listdir(pack_dir):
    # Call as python command right now, but later on, 
    # import as a module for better flexibility and speed, 
    # requires modifying main repo's code
    print(f"Patching {filename}...")
    os.system(
        f"py main_src/sc/sc_patch_translations.py \
         {pack_dir}{filename} \
         {scripts}{filename}.json \
         {scripts}en_US/{filename}.po")
    
